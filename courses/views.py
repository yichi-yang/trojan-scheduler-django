from django.shortcuts import render
from rest_framework import viewsets
from .models import Course, Section
from .serializers import CourseSerializer

# Create your views here.


class CourseView(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    lookup_field = 'name'

    def get_queryset(self):
        return Course.objects.all().filter(term=self.kwargs['term'])
