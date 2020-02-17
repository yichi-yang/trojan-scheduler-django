from rest_framework_simplejwt.tokens import Token, BlacklistMixin
from rest_framework_simplejwt.utils import datetime_to_epoch, datetime_from_epoch, format_lazy
from rest_framework_simplejwt.state import User
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError, AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import timedelta


class IatToken(Token):
    def __init__(self, token=None, verify=True):
        self.user = None
        super().__init__(token=token, verify=verify)
        if token is None:
            self.set_iat(self.current_time)

    def set_iat(self, now):
        self.payload["iat"] = datetime_to_epoch(now)

    def verify(self):
        super().verify()
        self.check_iat()

    def check_iat(self, claim='iat', current_time=None):
        """
        Checks whether a timestamp value in the given claim has passed (since
        the given datetime value in `current_time`).  Raises a TokenError with
        a user-facing error message if so.
        """
        if current_time is None:
            current_time = self.current_time

        try:
            claim_value = self.payload[claim]
        except KeyError:
            raise TokenError(format_lazy(_("Token has no '{}' claim"), claim))

        claim_time = datetime_from_epoch(claim_value)

        invalidate_token_before = self.get_user().invalidate_token_before

        if claim_time <= invalidate_token_before:
            raise TokenError(format_lazy(
                _("Token '{}' claim has expired"), claim))

    def get_user(self):
        """
        Attempts to find and return a user using the given validated token.
        """

        if self.user is not None:
            return self.user

        try:
            user_id = self[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(
                _('Token contained no recognizable user identification'))

        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed(
                _('User not found'), code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed(
                _('User is inactive'), code='user_inactive')

        self.user = user

        return user


class IatRefreshToken(BlacklistMixin, IatToken):
    token_type = 'refresh'
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        'exp',
        'iat',

        # Both of these claims are included even though they may be the same.
        # It seems possible that a third party token might have a custom or
        # namespaced JTI claim as well as a default "jti" claim.  In that case,
        # we wouldn't want to copy either one.
        api_settings.JTI_CLAIM,
        'jti',
    )

    @property
    def access_token(self):
        """
        Returns an access token created from this refresh token.  Copies all
        claims present in this refresh token to the new access token except
        those claims listed in the `no_copy_claims` attribute.
        """
        access = IatAccessToken()

        # Use instantiation time of refresh token as relative timestamp for
        # access token "exp" claim.  This ensures that both a refresh and
        # access token expire relative to the same time if they are created as
        # a pair.
        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access


class IatAccessToken(BlacklistMixin, IatToken):
    token_type = 'access'
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME


class EmailVerificationToken(BlacklistMixin, IatToken):
    token_type = 'email'
    lifetime = settings.EMAIL_TOKEN_LIFETIME


class IatUntypedToken(IatToken):
    token_type = 'untyped'
    lifetime = timedelta(seconds=0)

    def verify_token_type(self):
        """
        Untyped tokens do not verify the "token_type" claim.  This is useful
        when performing general validation of a token's signature and other
        properties which do not relate to the token's intended use.
        """
        pass
