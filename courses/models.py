from django.db import models
from .validators import validate_termcode

# Create your models here.


class Course(models.Model):
    name = models.CharField(max_length=20, unique=True)
    term = models.PositiveIntegerField(validators=[validate_termcode, ])
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        semesters = ['Spring', 'Summer', 'Fall']
        return '{name} ({term} {semester})'.format(name=self.name, term=str(self.term // 10), semester=semesters[self.term % 10 - 1])


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section_id = models.PositiveIntegerField(primary_key=True)
    section_type = models.CharField(max_length=20)
    need_clearance = models.BooleanField()
    registered = models.CharField(max_length=20)
    instructor = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=20, blank=True)
    start = models.TimeField(blank=True, null=True)
    end = models.TimeField(blank=True, null=True)
    mon = models.BooleanField()
    tue = models.BooleanField()
    wed = models.BooleanField()
    thu = models.BooleanField()
    fri = models.BooleanField()
    sat = models.BooleanField()
    sun = models.BooleanField()

    def __str__(self):
        semesters = ['Spring', 'Summer', 'Fall']
        return '{course} {section_id} {section_type}'.format(course=self.course.name, section_id=self.section_id, section_type=self.section_type)
