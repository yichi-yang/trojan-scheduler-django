from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from django.contrib.auth import get_user_model
from .permissions import UserOwnerOnly
from .serializers import UserSerializer


class UserView(viewsets.GenericViewSet,
               mixins.RetrieveModelMixin,
               mixins.CreateModelMixin,
               mixins.DestroyModelMixin,
               mixins.UpdateModelMixin):

    permission_classes = [UserOwnerOnly]
    queryset = get_user_model().objects.all().select_related("profile")
    serializer_class = UserSerializer
