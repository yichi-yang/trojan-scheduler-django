from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings

# Create your models here.


class RequestData(models.Model):
    coursebin = JSONField()
    preference = JSONField()


class Task(models.Model):
    PENDING = 'PD'
    PROCESSING = 'PS'
    DONE = 'DN'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (DONE, 'Done'),
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


class Schedule(models.Model):
    early_score = models.FloatField()
    late_score = models.FloatField()
    break_score = models.FloatField()
    reserved_score = models.FloatField()
    total_score = models.FloatField()
    task = models.ForeignKey(
        Task, related_name='schedules', on_delete=models.PROTECT)
    public = models.BooleanField(default=False)
