from django.shortcuts import render
from rest_framework import viewsets, mixins, generics, permissions, status, views
from django.contrib.auth import get_user_model
from .permissions import UserOwnerOnly
from .serializers import UserSerializer
from custom_jwt.authentication import JWTEmailVerificationAuthentication
from custom_jwt.tokens import EmailVerificationToken
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils.timezone import now


class UserView(viewsets.GenericViewSet,
               mixins.RetrieveModelMixin,
               mixins.CreateModelMixin,
               mixins.DestroyModelMixin,
               mixins.UpdateModelMixin):

    permission_classes = (UserOwnerOnly,)
    queryset = get_user_model().objects.all()
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

    def post(self, request, *args, **kwargs):

        user = request.user

        email_field_name = get_user_model().get_email_field_name()
        email = getattr(user, email_field_name)

        token = EmailVerificationToken.for_user(user)
        send_mail(
            'Trojan Scheduler Email Verification',
            'Use this token to verify your email address: {}'.format(
                str(token)),
            'from@example.com',
            [email],
            fail_silently=False,
        )
        serializer = self.get_serializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenInvalidateView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        user = request.user

        current_time = now()

        user.invalidate_token_before = current_time
        user.save()

        return Response({"now": current_time}, status=status.HTTP_200_OK)
