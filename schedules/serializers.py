from rest_framework import serializers
from .models import Task, Schedule, RequestData
from courses.serializers import SectionDetailSerializer


class ScheduleSerializer(serializers.ModelSerializer):

    created = serializers.DateTimeField(source="task.created", read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        source="task.user", read_only=True)

    class Meta:
        model = Schedule
        fields = ('id', 'name', 'early_score', 'late_score', 'break_score',
                  'reserved_score', 'total_score', 'task', 'created', 'public', 'user')
        extra_kwargs = {'task': {"style": {
            'base_template': 'input.html',
            'input_type': 'text'
        }}}


class ScheduleDetailedSerializer(ScheduleSerializer):

    sections = SectionDetailSerializer(many=True, read_only=True)

    class Meta(ScheduleSerializer.Meta):
        fields = (*ScheduleSerializer.Meta.fields, "sections")


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'name', 'created', 'user',
                  'status', 'request_data', 'message', 'count')


class TaskDetailSerializer(serializers.ModelSerializer):

    schedules = ScheduleDetailedSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = (*TaskSerializer.Meta.fields, 'schedules')


class RequestDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestData
        fields = ('coursebin', 'preference')
