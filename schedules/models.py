from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings
from courses.models import Section
from .validators import coursebin_validator, preference_validator, setting_validator
from copy import deepcopy

# Create your models here.


def createDefaultPreference():
    return deepcopy({
        "early_time": "10:00",
        "early_weight": 75,
        "late_time": "15:00",
        "late_weight": 25,
        "break_time": "00:10",
        "break_weight": 50,
        "reserved": [
            {
                "key": "#default0",
                "from": "11:30",
                "to": "12:30",
                "wiggle": "01:00",
                "weight": 50
            },
            {
                "key": "#default1",
                "from": "17:30",
                "to": "18:30",
                "wiggle": "01:00",
                "weight": 50
            }
        ]
    })


def createDefaultSetting():
    return deepcopy({
        "course": "",
        "term": settings.CURRENT_SEMESTER,
        "toolsOpen": False,
        "clearedSections": "",
        "clearedOnly": False,
        "excludeClosed": False,
        "exemptedSections": "",
        "savedOnly": True,
        "publicOnly": False
    })


class RequestData(models.Model):
    coursebin = JSONField(validators=[coursebin_validator, ], default=list)
    preference = JSONField(
        validators=[preference_validator, ], default=createDefaultPreference)
    setting = JSONField(
        validators=[setting_validator, ], default=createDefaultSetting)


class Task(models.Model):

    class Meta:
        ordering = ['-created']

    PENDING = 'PD'
    PROCESSING = 'PS'
    DONE = 'DN'
    WARNING = 'WN'
    ERROR = 'ER'
    EXCEPT = 'EX'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (DONE, 'Done'),
        (WARNING, 'Waring'),
        (ERROR, 'Error'),
        (EXCEPT, 'Uncaught Exception'),
    ]

    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="tasks",
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    request_data = models.OneToOneField(
        RequestData, related_name="task", on_delete=models.PROTECT)
    name = models.CharField(max_length=100, blank=True, default="")
    description = models.CharField(max_length=500, blank=True, default="")
    message = models.CharField(max_length=200, null=True, default=None)
    count = models.PositiveIntegerField(default=0)


class Schedule(models.Model):

    class Meta:
        ordering = ['-task__created', 'id']

    early_score = models.FloatField()
    late_score = models.FloatField()
    break_score = models.FloatField()
    reserved_score = models.FloatField()
    total_score = models.FloatField()
    task = models.ForeignKey(
        Task, related_name='schedules', on_delete=models.PROTECT)
    public = models.BooleanField(default=False)
    sections = models.ManyToManyField(Section)
    name = models.CharField(max_length=100, blank=True, default="")
    description = models.CharField(max_length=200, blank=True, default="")
    saved = models.BooleanField(default=False)
