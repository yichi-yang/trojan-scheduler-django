from django.urls import path, include
from rest_framework import routers
from .views import TaskView, ScheduleView, RequestDataView

router = routers.DefaultRouter()
router.register('tasks', TaskView)
router.register('schedules', ScheduleView)
router.register('task-data', RequestDataView)

urlpatterns = [
    path("", include(router.urls)),
]
