from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from .models import Task, Schedule
from .serializers import TaskSerializer, TaskDetailSerializer, RequestDataSerializer, ScheduleSerializer
from rest_framework import status
from rest_framework.response import Response
from .generate_schedule import generate_schedule

# Create your views here.


class TaskView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin):

    queryset = Task.objects.all().prefetch_related("schedules")

    def create(self, request, *args, **kwargs):

        request_data = {'coursebin': request.data.get(
            'coursebin', None), 'preference': request.data.get('preference', None)}

        rd_serialier = RequestDataSerializer(data=request_data)
        rd_serialier.is_valid(raise_exception=True)
        request_data_instance = rd_serialier.save()

        task_data = {
            "status": Task.PENDING,
            "user": None,
            "request_data": request_data_instance.pk
        }

        serializer = self.get_serializer(data=task_data)
        serializer.is_valid(raise_exception=True)
        task_instance = self.perform_create(serializer)

        generate_schedule(request_data['coursebin'],
                          request_data['preference'],
                          task_instance)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskSerializer
        return TaskDetailSerializer

class ScheduleView(viewsets.ModelViewSet):

    queryset = Schedule.objects.all().prefetch_related("sections").prefetch_related("task")
    serializer_class = ScheduleSerializer