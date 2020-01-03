from django.shortcuts import render
from rest_framework import viewsets
from .models import Course, Section
from .serializers import CourseSerializer, SectionDetailSerializer
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

    def get_object_or_none(self, name, lock=False):
        queryset = self.filter_queryset(self.get_queryset())
        if lock:
            queryset = queryset.select_for_update()
        instance = None
        try:
            instance = queryset.get(name=name)
        except Course.DoesNotExist:
            pass
        if instance is not None:
            self.check_object_permissions(self.request, instance)
        return instance

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

            instance = self.get_object_or_none(name, lock=True)

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
                    return Response(self.get_serializer(instance).data)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)

            # if fetched course's name does not match current instance,
            # select the new one to match
            if course['name'] != name:
                instance = self.get_object_or_none(course['name'], lock=True)

            serializer = self.get_serializer(
                instance, data=course, partial=False)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class SectionView(viewsets.ModelViewSet):

    serializer_class = SectionDetailSerializer
    lookup_field = 'section_id'

    def get_queryset(self):
        return Section.objects.all().filter(course__term=self.kwargs['term'])
