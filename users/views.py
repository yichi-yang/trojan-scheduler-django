from django.shortcuts import render
from rest_framework import viewsets, mixins, generics, permissions, status, views
from .models import User
from .permissions import UserOwnerEditOnly
from .serializers import UserSerializer, UsernameSerializer, EmailSerializer
from custom_jwt.authentication import JWTEmailVerificationAuthentication, JWTPasswordResetAuthentication
from custom_jwt.tokens import EmailVerificationToken, PasswordResetToken
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.conf import settings


class UserView(viewsets.GenericViewSet,
               mixins.RetrieveModelMixin,
               mixins.CreateModelMixin,
               mixins.DestroyModelMixin,
               mixins.UpdateModelMixin):

    permission_classes = (UserOwnerEditOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class EmailVerificationView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTEmailVerificationAuthentication,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):

        user = request.user

        user.email_verified = True
        user.invalidate_token_before = now()
        user.save()

        serializer = self.get_serializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EmailSendTokenView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    throttle_scope = 'email'

    def post(self, request, *args, **kwargs):

        user = request.user

        if user.email_verified:
            return Response({"detail": "email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

        email_field_name = User.get_email_field_name()
        email = getattr(user, email_field_name)

        token = EmailVerificationToken.for_user(user)

        context = {"username": user.username,
                   "email_verification_url": settings.SITE_BASE_URL + "/verify/?no-update&token=" + str(token)}

        text = render_to_string("email_verification.txt", context)
        html = render_to_string("email_verification.html", context)

        send_mail(
            'Trojan Scheduler Email Verification',
            text,
            'scheduler@yichiyang.com',
            [email],
            html_message=html,
            fail_silently=False,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class TokenInvalidateView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        user = request.user

        current_time = now()

        user.invalidate_token_before = current_time
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordForgetView(generics.GenericAPIView):

    serializer_class = EmailSerializer
    throttle_scope = 'email'

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        email_field_name = User.get_email_field_name()
        query = {email_field_name: email,  "email_verified": True}

        user = None
        not_found = False
        more_than_one = False

        try:
            user = User.objects.get(**query)
        except User.DoesNotExist:
            not_found = True
        except User.MultipleObjectsReturned:
            more_than_one = True

        text = ""
        html = ""

        if not_found:
            text = render_to_string("reset_not_found_email.txt", context={
                                    "password_forget_url": settings.SITE_BASE_URL + "/password/forget/"})
            html = render_to_string("reset_not_found_email.html", context={
                                    "password_forget_url": settings.SITE_BASE_URL + "/password/forget/"})
        elif more_than_one:
            text = render_to_string("reset_multiple_account_email.txt")
            html = render_to_string("reset_multiple_account_email.html")
        else:
            token = PasswordResetToken.for_user(user)
            text = render_to_string("reset_password_email.txt", context={
                                    "password_reset_url": settings.SITE_BASE_URL + "/password/reset/?no-update&token=" + str(token)})
            html = render_to_string("reset_password_email.html", context={
                                    "password_reset_url": settings.SITE_BASE_URL + "/password/reset/?no-update&token=" + str(token)})

        send_mail(
            'Trojan Scheduler Password Reset',
            text,
            'scheduler@yichiyang.com',
            [email],
            html_message=html,
            fail_silently=False,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTPasswordResetAuthentication,)
    serializer_class = UserSerializer

    def get_serializer_context(self):
        return {**super().get_serializer_context(), 'reset_password': True}

    def post(self, request, *args, **kwargs):

        user = request.user

        serializer = self.get_serializer(user,
                                         data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
