from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Task, Schedule


class TaskOwnerOnly(BasePermission):

    def has_object_permission(self, request, view, obj):

        assert isinstance(obj, Task), (
            'Expected a Task instance, got %s instead.' %
            (type(obj))
        )

        if obj.user is None and request.method in SAFE_METHODS:
            return True

        return obj.user == request.user


class ScheduleOwnerOnly(BasePermission):

    def has_object_permission(self, request, view, obj):

        assert isinstance(obj, Schedule), (
            'Expected a Schedule instance, got %s instead.' %
            (type(obj))
        )

        if (obj.task.user is None or obj.public) and request.method in SAFE_METHODS:
            return True

        return obj.task.user == request.user
