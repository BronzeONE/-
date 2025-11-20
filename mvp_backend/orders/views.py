from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile
from .models import CreatingOrder, Purchase, TestReport
from .serializers import (
    CreatingOrderSerializer,
    OrderDecisionSerializer,
    PurchaseSerializer,
    TestReportSerializer,
)


class PendingCreatingOrdersView(generics.ListAPIView):
    serializer_class = CreatingOrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return CreatingOrder.objects.filter(
            user=self.request.user,
            status=CreatingOrder.STATUS_PROCESSING,
        ).order_by('-created_at')


class PurchaseListView(generics.ListAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        try:
            return Purchase.objects.filter(tester=self.request.user).order_by('-created_at')
        except Exception as e:
            # Логируем ошибку для отладки
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Error loading purchases for user {self.request.user.id}: {str(e)}')
            # Если таблица не существует или есть проблемы с доступом, возвращаем пустой queryset
            return Purchase.objects.none()


class OrderDecisionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            order = CreatingOrder.objects.select_related('user').get(pk=pk, user=request.user)
        except CreatingOrder.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != CreatingOrder.STATUS_PROCESSING:
            return Response({'detail': 'Order has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Получаем или создаем профиль
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if not profile.is_completed:
            return Response({'detail': 'Complete your profile before responding to orders.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Автоматически включаем участие при принятии заказа, если профиль заполнен
        if data['action'] == 'approve' and not profile.is_participating:
            profile.is_participating = True
            profile.save(update_fields=('is_participating', 'updated_at'))

        order.responded_at = timezone.now()

        if data['action'] == 'approve':
            try:
                order.status = CreatingOrder.STATUS_APPROVED
                order.pickup_point = data.get('pickup_point') or order.pickup_point or (profile.pickup_point if profile else '')
                order.save(update_fields=('status', 'pickup_point', 'responded_at', 'updated_at'))

                metadata = {}
                if order.payload and isinstance(order.payload, dict):
                    metadata = order.payload.copy()
                if data.get('purchase_metadata'):
                    metadata.update(data.get('purchase_metadata', {}))
                
                pickup_point = order.pickup_point or (profile.pickup_point if profile else '') or ''

                # Для managed=False модели используем try/except вместо update_or_create
                try:
                    purchase = Purchase.objects.get(creating_order=order)
                    # Обновляем существующий
                    purchase.tester = request.user
                    purchase.external_id = data.get('external_id', '') or ''
                    purchase.article = order.article or ''
                    purchase.pickup_point = pickup_point
                    purchase.metadata = metadata
                    purchase.status = Purchase.STATUS_PENDING
                    purchase.save()
                    created = False
                except Purchase.DoesNotExist:
                    # Создаем новый
                    purchase = Purchase.objects.create(
                        creating_order=order,
                        tester=request.user,
                        external_id=data.get('external_id', '') or '',
                        article=order.article or '',
                        pickup_point=pickup_point,
                        metadata=metadata,
                        status=Purchase.STATUS_PENDING,
                    )
                    created = True
                return Response({
                    'detail': 'Order approved and purchase created.',
                    'purchase_id': purchase.id,
                })
            except Exception as e:
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                error_trace = traceback.format_exc()
                logger.error(f'Error creating purchase: {str(e)}\n{error_trace}')
                return Response(
                    {'detail': f'Ошибка при создании заказа: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        order.status = CreatingOrder.STATUS_REJECTED
        order.save(update_fields=('status', 'responded_at', 'updated_at'))
        return Response({'detail': 'Order rejected.'})


class TestReportView(generics.RetrieveUpdateAPIView):
    """Получить или обновить отчёт о тестировании для заказа."""
    serializer_class = TestReportSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        purchase_id = self.kwargs.get('purchase_id')
        try:
            purchase = Purchase.objects.get(id=purchase_id, tester=self.request.user)
        except Purchase.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Заказ не найден или у вас нет доступа к нему.')
        
        try:
            report = TestReport.objects.get(purchase=purchase)
        except TestReport.DoesNotExist:
            # Создаем новый отчет с данными по умолчанию
            profile = self.request.user.profile
            report = TestReport.objects.create(
                purchase=purchase,
                full_name=profile.full_name or '',
                contact=profile.contact or str(self.request.user.phone_number),
                item_name=purchase.article,
            )
        return report


class TestReportCreateView(generics.CreateAPIView):
    """Создать отчёт о тестировании."""
    serializer_class = TestReportSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def perform_create(self, serializer):
        purchase_id = self.request.data.get('purchase_id')
        try:
            purchase = Purchase.objects.get(id=purchase_id, tester=self.request.user)
        except Purchase.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Заказ не найден или у вас нет доступа к нему.')
        
        profile = self.request.user.profile
        serializer.save(
            purchase=purchase,
            full_name=serializer.validated_data.get('full_name') or profile.full_name or '',
            contact=serializer.validated_data.get('contact') or profile.contact or str(self.request.user.phone_number),
            item_name=serializer.validated_data.get('item_name') or purchase.article,
        )
