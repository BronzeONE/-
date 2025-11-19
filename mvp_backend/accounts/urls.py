from django.urls import path

from .views import LoginView, ParticipationView, ProfileView, RegistrationView

urlpatterns = [
    path('auth/register/', RegistrationView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('profile/me/', ProfileView.as_view(), name='profile-detail'),
    path('profile/participation/', ParticipationView.as_view(), name='profile-participation'),
]

