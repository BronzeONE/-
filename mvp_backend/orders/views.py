from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile
from .models import CreatingOrder, Purchase
from .serializers import CreatingOrderSerializer, OrderDecisionSerializer, PurchaseSerializer


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
        profile: UserProfile = request.user.profile

        if not profile.is_completed:
            return Response({'detail': 'Complete your profile before responding to orders.'}, status=status.HTTP_400_BAD_REQUEST)
        if not profile.is_participating:
            return Response({'detail': 'Enable participation in your profile to accept orders.'}, status=status.HTTP_400_BAD_REQUEST)

        order.responded_at = timezone.now()

        if data['action'] == 'approve':
            order.status = CreatingOrder.STATUS_APPROVED
            order.pickup_point = data.get('pickup_point') or order.pickup_point or profile.pickup_point
            order.save(update_fields=('status', 'pickup_point', 'responded_at', 'updated_at'))

            metadata = order.payload.copy() if isinstance(order.payload, dict) else {}
            metadata.update(data.get('purchase_metadata', {}))
            pickup_point = order.pickup_point or profile.pickup_point

            Purchase.objects.update_or_create(
                creating_order=order,
                defaults={
                    'tester': request.user,
                    'external_id': data.get('external_id', ''),
                    'article': order.article,
                    'pickup_point': pickup_point or '',
                    'metadata': metadata,
                    'status': Purchase.STATUS_PENDING,
                },
            )
            return Response({'detail': 'Order approved and purchase created.'})

        order.status = CreatingOrder.STATUS_REJECTED
        order.save(update_fields=('status', 'responded_at', 'updated_at'))
        return Response({'detail': 'Order rejected.'})
