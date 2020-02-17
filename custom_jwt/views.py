from rest_framework_simplejwt.views import TokenViewBase
from .serializers import IatTokenObtainPairSerializer, IatTokenRefreshSerializer, IatTokenVerifySerializer


class IatTokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = IatTokenObtainPairSerializer


class IatTokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """
    serializer_class = IatTokenRefreshSerializer


class IatTokenVerifyView(TokenViewBase):
    """
    Takes a token and indicates if it is valid.  This view provides no
    information about a token's fitness for a particular use.
    """
    serializer_class = IatTokenVerifySerializer
