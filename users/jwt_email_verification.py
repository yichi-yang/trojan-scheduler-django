from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.tokens import BlacklistMixin, Token
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException

class NoEmailSet(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Cannot request email verification without email")
    default_code = 'email_verification_no_email'

class AlreadyVerified(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Cannot request email verification when the email is already verified")
    default_code = 'email_verification_already_verified'

class EmailDoesNotMatch(AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Email claim does not match user's current email")
    default_code = 'email_verification_not_match'


class EmailVerificationToken(BlacklistMixin, Token):
    token_type = 'email'
    lifetime = settings.EMAIL_TOKEN_LIFETIME

    @classmethod
    def for_user(cls, user):
        """
        Returns an EmailVerificationToken for the given user, sets the email claim.
        """
        token = super().for_user(user)

        email_field_name = get_user_model().get_email_field_name()
        token["email"] = getattr(user, email_field_name)

        return token


class JWTEmailVerificationAuthentication(JWTAuthentication):

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        if "email" not in validated_token.payload:
            raise InvalidToken(_('Token does not contain email claim'))
        user = self.get_user(validated_token)
        email_field_name = get_user_model().get_email_field_name()
        if(validated_token.payload.get("email") != getattr(user, email_field_name)):
            raise EmailDoesNotMatch()

        return user, validated_token

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []

        AuthToken = EmailVerificationToken  # only allow EmailVerificationToken

        try:
            return AuthToken(raw_token)
        except TokenError as e:
            messages.append({'token_class': AuthToken.__name__,
                             'token_type': AuthToken.token_type,
                             'message': e.args[0]})

        raise InvalidToken({
            'detail': _('Given token is not a EmailVerificationToken'),
            'messages': messages,
        })
