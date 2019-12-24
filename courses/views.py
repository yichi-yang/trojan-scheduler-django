from django.shortcuts import render
from rest_framework import viewsets
from .models import Course, Section
from .serializers import CourseSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from .scraper import fetch_class
from datetime import datetime, timezone
from django.conf import settings

# Create your views here.


class CourseView(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    lookup_field = 'name'

    def get_queryset(self):
        return Course.objects.all().filter(term=self.kwargs['term'])

    def update(self, request, *args, **kwargs):
        with transaction.atomic():

            assert 'name' in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, 'name')
            )

            assert 'term' in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, 'term')
            )

            name = self.kwargs['name']
            term = self.kwargs['term']

            instance = None
            try:
                instance = self.filter_queryset(
                    self.get_queryset()).select_for_update().get(name=name)
            except Course.DoesNotExist:
                pass

            # if the Course instance exists in the database and is up to date,
            # return that Course instance
            if instance:
                delta = datetime.now(timezone.utc) - instance.updated
                if delta.total_seconds() <= settings.USC_SOC_CACHE_REFRESH:
                    return Response(self.get_serializer(instance).data)

            # fetch course information from USC Schedule of Courses
            course = fetch_class(term, name)
            # if fetch fails, return cached Course instance if possible
            if not course:
                if instance:
                    Response(self.get_serializer(instance).data)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)

            # if fetched course's name does not match current instance,
            # select the new one to match
            if course['name'] != name:
                instance = None
                try:
                    instance = self.filter_queryset(
                        self.get_queryset()).select_for_update().get(name=course['name'])
                except Course.DoesNotExist:
                    pass

            serializer = self.get_serializer(
                instance, data=course, partial=False)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

        return Response(serializer.data)
