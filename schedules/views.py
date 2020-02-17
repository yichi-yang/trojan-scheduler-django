from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from .models import Task, Schedule, RequestData
from .serializers import TaskSerializer, TaskDetailSerializer, RequestDataSerializer, ScheduleSerializer, ScheduleDetailedSerializer
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Prefetch
from courses.models import Section
from .tasks import generate_schedule
from .permissions import TaskOwnerOnly, ScheduleOwnerOnly

# Create your views here.


class TaskView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin,
               mixins.CreateModelMixin, mixins.DestroyModelMixin):

    def get_queryset(self):
        user_pk = self.request.user.pk if self.request.user.is_authenticated else None
        if self.action == 'list':
            queryset = Task.objects.filter(user=user_pk)
        else:
            queryset = Task.objects.all()
        return self.get_serializer_class().eager_load(queryset)

    permission_classes = [TaskOwnerOnly]

    def create(self, request, *args, **kwargs):

        request_data = {'coursebin': request.data.get(
            'coursebin', None), 'preference': request.data.get('preference', None)}

        rd_serialier = RequestDataSerializer(data=request_data)
        rd_serialier.is_valid(raise_exception=True)
        request_data_instance = rd_serialier.save()

        task_data = {
            "status": Task.PENDING,
            "user": request.user.pk if request.user.is_authenticated else None,
            "request_data": request_data_instance.pk
        }

        serializer = self.get_serializer(data=task_data)
        serializer.is_valid(raise_exception=True)
        task_instance = serializer.save()

        generate_schedule.delay(request_data['coursebin'],
                                request_data['preference'],
                                task_instance.id)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskSerializer
        return TaskDetailSerializer


class ScheduleView(viewsets.ModelViewSet):

    permission_classes = [ScheduleOwnerOnly]

    def get_queryset(self):
        user_pk = self.request.user.pk if self.request.user.is_authenticated else None
        if self.action == 'list':
            saved_para = self.request.query_params.get('saved', None)
            saved_val = saved_para in ["", "True", "true"]
            if saved_para is not None:
                queryset = Schedule.objects.filter(
                    task__user=user_pk, saved=saved_val)
            else:
                queryset = Schedule.objects.filter(task__user=user_pk)
        else:
            queryset = Schedule.objects.all()
        return self.get_serializer_class().eager_load(queryset)

    def get_serializer_class(self):
        if self.action == 'list':
            return ScheduleSerializer
        return ScheduleDetailedSerializer

    def get_loader(self):
        return self.get_serializer_class().eager_load


class RequestDataView(viewsets.ModelViewSet):
    queryset = RequestData.objects.all()
    serializer_class = RequestDataSerializer
