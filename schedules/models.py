from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from courses.validators import validate_termcode
from django.conf import settings

# Create your models here.


class RequestData(models.Model):
    coursebin = JSONField()
    preference = JSONField()


class Task(models.Model):
    PENDING = 'PD'
    IN_PROGRESS = 'IP'
    DONE = 'DN'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (DONE, 'Done'),
    ]
    
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="tasks",
        on_delete=models.CASCADE,
    )
    request_data = models.OneToOneField(
        RequestData, related_name="task", on_delete=models.CASCADE)


class Schedule(models.Model):
    term = models.PositiveIntegerField(validators=[validate_termcode, ])
    sections = ArrayField(models.PositiveIntegerField())
    early_score = models.FloatField()
    late_score = models.FloatField()
    break_score = models.FloatField()
    reserved_score = models.FloatField()
    total_score = models.FloatField()
    task = models.ForeignKey(
        Task, related_name='schedules', on_delete=models.PROTECT)
