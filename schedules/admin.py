from django.contrib import admin
from .models import Task, RequestData, Schedule

# Register your models here.
admin.site.register(RequestData)
admin.site.register(Task)
admin.site.register(Schedule)