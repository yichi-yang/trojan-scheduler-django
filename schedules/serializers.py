from rest_framework import serializers
from .models import Task, Schedule, RequestData
from courses.serializers import SectionDetailSerializer


class ScheduleSerializer(serializers.ModelSerializer):

    sections = SectionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = ('id', 'name', 'sections', 'early_score', 'late_score',
                  'break_score', 'reserved_score', 'total_score', 'task')
        extra_kwargs = {'task': {"style": {
            'base_template': 'input.html',
            'input_type': 'text'
        }}}


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'name', 'created', 'user',
                  'status', 'request_data', 'message', 'count')


class TaskDetailSerializer(serializers.ModelSerializer):

    schedules = ScheduleSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = (*TaskSerializer.Meta.fields, 'schedules')


class RequestDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestData
        fields = ('coursebin', 'preference')
