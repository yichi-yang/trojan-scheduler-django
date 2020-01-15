from django.urls import path, include
from rest_framework import routers
from .views import TaskView, ScheduleView

router = routers.DefaultRouter()
router.register('tasks', TaskView)
router.register('schedules', ScheduleView)

urlpatterns = [
    path("", include(router.urls)),
]
