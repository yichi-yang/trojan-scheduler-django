from django.urls import path, include
from rest_framework import routers
from .views import CourseView, SectionView

router = routers.DefaultRouter()
router.register('courses/(?P<term>\d+)', CourseView, basename='courses')
router.register('sections/(?P<term>\d+)', SectionView, basename='sections')

urlpatterns = [
    path("", include(router.urls)),
]
