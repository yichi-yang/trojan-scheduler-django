from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import get_user_model


class UserOwnerEditOnly(BasePermission):

    def has_object_permission(self, request, view, obj):

        assert isinstance(obj, get_user_model()), (
            'Expected a User instance, got %s instead.' %
            (type(obj))
        )

        return request.method in SAFE_METHODS or obj == request.user
