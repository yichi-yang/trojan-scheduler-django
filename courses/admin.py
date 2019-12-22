from django.contrib import admin
from .models import Course, Section

# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    readonly_fields = ('updated',)

admin.site.register(Course, CourseAdmin)
admin.site.register(Section)
