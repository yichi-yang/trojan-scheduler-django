from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework import mixins
from .models import Task, Schedule, RequestData
from .serializers import TaskSerializer, TaskDetailSerializer, RequestDataSerializer, ScheduleSerializer, ScheduleDetailedSerializer
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Prefetch
from courses.models import Section
from .tasks import generate_schedule
from .permissions import TaskOwnerOnly, ScheduleOwnerOnly, RequestDataOwnerOnly
from django.db import transaction
from random import randint
from django.http import Http404

# Create your views here.


class TaskView(viewsets.ModelViewSet):

    def get_queryset(self):
        user_pk = self.request.user.pk if self.request.user.is_authenticated else None
        if self.action == 'list':
            queryset = Task.objects.filter(user=user_pk)
        else:
            queryset = Task.objects.all()
        return self.get_serializer_class().eager_load(queryset)

    permission_classes = [TaskOwnerOnly]

    def create(self, request, *args, **kwargs):

        request_data = {'coursebin': request.data.pop(
            'coursebin', None), 'preference': request.data.pop('preference', None)}

        rd_serialier = RequestDataSerializer(data=request_data)
        rd_serialier.is_valid(raise_exception=True)
        request_data_instance = rd_serialier.save()

        task_data = {
            "user": request.user if request.user.is_authenticated else None,
            "request_data": request_data_instance,
            "status": Task.PENDING
        }

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_instance = serializer.save(**task_data)

        generate_schedule.delay(request_data['coursebin'],
                                request_data['preference'],
                                task_instance.id)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskSerializer
        return TaskDetailSerializer

    @transaction.atomic
    def perform_destroy(self, instance):
        instance.schedules.all().delete()
        request_data = instance.request_data
        instance.delete()
        request_data.delete()


class ScheduleView(viewsets.ModelViewSet):

    permission_classes = [ScheduleOwnerOnly]

    def get_queryset(self):
        user_pk = self.request.user.pk if self.request.user.is_authenticated else None
        if self.action == 'list':
            query_para = {}
            saved = self.request.query_params.get('saved')
            if saved:
                query_para["saved"] = saved in ["", "True", "true"]
            public = self.request.query_params.get('public')
            if public:
                query_para["public"] = public in ["", "True", "true"]

            queryset = Schedule.objects.filter(task__user=user_pk,
                                               **query_para)
        else:
            queryset = Schedule.objects.all()
        return self.get_serializer_class().eager_load(queryset)

    def get_serializer_class(self):
        if self.action == 'list':
            return ScheduleSerializer
        return ScheduleDetailedSerializer


class RandomScheduleView(generics.RetrieveAPIView):

    permission_classes = [ScheduleOwnerOnly]
    serializer_class = ScheduleDetailedSerializer

    @transaction.atomic
    def get_object(self):
        all = Schedule.objects.all().filter(public=True)
        count = all.count()
        if count == 0:
            raise Http404("No schedules found")
        return all[randint(0, count - 1)]


class RequestDataView(viewsets.ModelViewSet):
    queryset = RequestData.objects.all()
    serializer_class = RequestDataSerializer
    permission_classes = [RequestDataOwnerOnly]
