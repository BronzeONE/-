from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView

from .models import UserProfile
from .serializers import (
    LoginSerializer,
    ParticipationSerializer,
    RegistrationSerializer,
    UserProfileSerializer,
    UserSerializer,
)


class RegistrationView(CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'user': UserSerializer(user).data,
                'token': token.key,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_active:
            return Response({'detail': 'User account is disabled.'}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error updating profile for user {request.user.id}: {str(e)}', exc_info=True)
            from rest_framework.response import Response
            return Response(
                {'detail': f'Ошибка при сохранении профиля: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ParticipationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        profile = UserProfile.objects.select_related('user').get(user=request.user)
        serializer = ParticipationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_participating = serializer.validated_data['is_participating']

        if is_participating and not profile.is_completed:
            return Response(
                {'detail': 'Complete your profile before participating in orders.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.update(profile, serializer.validated_data)
        return Response(UserProfileSerializer(profile).data)
