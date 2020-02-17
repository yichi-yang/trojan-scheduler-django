from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .tokens import IatToken, EmailVerificationToken
from django.utils.translation import ugettext_lazy as _


class IatJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        if isinstance(validated_token, IatToken):
            return validated_token.get_user()
        else:
            return super().get_user(validated_token)


class JWTEmailVerificationAuthentication(IatJWTAuthentication):
    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        AuthToken = EmailVerificationToken

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
