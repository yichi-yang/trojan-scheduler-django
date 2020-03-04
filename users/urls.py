from django.urls import path, include
from rest_framework import routers
from .views import (UserView, EmailSendTokenView,
                    EmailVerificationView, TokenInvalidateView,
                    PasswordForgetView, PasswordResetView)
from custom_jwt.views import (
    IatTokenObtainPairView,
    IatTokenRefreshView,
    IatTokenVerifyView
)

router = routers.DefaultRouter()
router.register('users', UserView, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path('token/', IatTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', IatTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', IatTokenVerifyView.as_view(), name='token_verify'),
    path('token/invalidate/', TokenInvalidateView.as_view(),
         name='token_invalidate'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify_email'),
    path('verify-email/request-token/',
         EmailSendTokenView.as_view(), name='request_email_token'),
    path('password/forget/',
         PasswordForgetView.as_view(), name='forget_password_token'),
    path('password/reset/',
         PasswordResetView.as_view(), name='reset_password_token'),
]
