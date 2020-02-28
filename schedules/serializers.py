from rest_framework import serializers
from .models import Task, Schedule, RequestData
from courses.serializers import SectionDetailSerializer
from django.db.models import Prefetch
from courses.models import Section


class ScheduleSerializer(serializers.ModelSerializer):

    created = serializers.DateTimeField(source="task.created", read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        source="task.user", read_only=True)

    class Meta:
        model = Schedule
        fields = ('id', 'name', 'description', 'early_score', 'late_score', 'break_score',
                  'reserved_score', 'total_score', 'task', 'created', 'public', 'user', 'saved')
        read_only_fields = ('id', 'early_score', 'late_score', 'break_score',
                            'reserved_score', 'total_score', 'task')

    @classmethod
    def eager_load(cls, queryset):
        return queryset.select_related('task')


class ScheduleDetailedSerializer(ScheduleSerializer):

    sections = SectionDetailSerializer(many=True, read_only=True)

    class Meta(ScheduleSerializer.Meta):
        fields = (*ScheduleSerializer.Meta.fields, "sections")

    @classmethod
    def eager_load(cls, queryset):
        return queryset.select_related('task').prefetch_related(
            Prefetch("sections",
                     queryset=Section.objects.all().select_related('course')
                     ))


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'created', 'user',
                  'status', 'request_data', 'message', 'count')
        read_only_fields = ('id',  'created', 'user', 'status',
                            'request_data', 'message', 'count')

    @classmethod
    def eager_load(cls, queryset):
        return queryset


class TaskDetailSerializer(serializers.ModelSerializer):

    schedules = ScheduleDetailedSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = (*TaskSerializer.Meta.fields, 'schedules')
        read_only_fields = ('schedules', *TaskSerializer.Meta.read_only_fields)

    @classmethod
    def eager_load(cls, queryset):
        return queryset.prefetch_related("schedules", Prefetch(
            "schedules__sections",
            queryset=Section.objects.all().select_related('course')
        ))


class RequestDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestData
        fields = ('coursebin', 'preference', 'setting')
