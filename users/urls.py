from django.urls import path, include
from rest_framework import routers
from .views import UserView, EmailSendTokenView, EmailVerificationView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

router = routers.DefaultRouter()
router.register('users', UserView, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify_email'),
    path('verify-email/request-token/',
         EmailSendTokenView.as_view(), name='request_email_token'),
]
