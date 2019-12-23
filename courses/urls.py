from django.urls import path, include
from rest_framework import routers
from .views import CourseView

router = routers.DefaultRouter()
router.register('courses/(?P<term>\d+)', CourseView, basename='courses')

urlpatterns = [
    path("", include(router.urls)),
]
