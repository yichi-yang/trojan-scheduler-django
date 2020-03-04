from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .tokens import IatToken, EmailVerificationToken, PasswordResetToken
from django.utils.translation import ugettext_lazy as _
from rest_framework_simplejwt.settings import api_settings


class IatJWTAuthentication(JWTAuthentication):

    auth_token_classes = None

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []

        auth_token_classes = self.auth_token_classes \
            if self.auth_token_classes is not None \
            else api_settings.AUTH_TOKEN_CLASSES

        for AuthToken in auth_token_classes:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append({'token_class': AuthToken.__name__,
                                 'token_type': AuthToken.token_type,
                                 'message': e.args[0]})

        raise InvalidToken({
            'detail': _('Given token not valid for any token type'),
            'messages': messages,
        })


class JWTEmailVerificationAuthentication(IatJWTAuthentication):

    auth_token_classes = (EmailVerificationToken,)


class JWTPasswordResetAuthentication(IatJWTAuthentication):

    auth_token_classes = (PasswordResetToken,)
