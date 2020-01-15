from django.db import models
from .validators import validate_termcode, validate_days_array
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from schedules.models import Schedule

# Create your models here.


class Course(models.Model):
    name = models.CharField(max_length=20)
    term = models.PositiveIntegerField(validators=[validate_termcode, ])
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'term')

    def __str__(self):
        semesters = ['Spring', 'Summer', 'Fall']
        return '{name} ({term} {semester})'.format(name=self.name, term=str(self.term // 10), semester=semesters[self.term % 10 - 1])


class Section(models.Model):
    class Meta:
        ordering = ['course', 'order_fetched']

    course = models.ForeignKey(
        Course, related_name='sections', on_delete=models.CASCADE)
    section_id = models.PositiveIntegerField()
    section_type = models.CharField(max_length=30)
    need_clearance = models.BooleanField()
    registered = models.CharField(max_length=30)
    instructor = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=30, blank=True)
    start = models.TimeField(blank=True, null=True)
    end = models.TimeField(blank=True, null=True)
    days = ArrayField(models.PositiveSmallIntegerField(),
                      size=7, validators=[validate_days_array, ], blank=True)
    order_fetched = models.PositiveSmallIntegerField()
    schedules = models.ManyToManyField(Schedule, related_name='sections')

    def validate_unique(self, exclude=None):
        if Section.objects.exclude(id=self.id).filter(section_id=self.section_id, course__term=self.course.term).exists():
            raise ValidationError("Section must have unique(course.term, section_id)")
        super(Section, self).validate_unique(exclude)

    def __str__(self):
        semesters = ['Spring', 'Summer', 'Fall']
        return '{course} {section_id} {section_type}'.format(course=self.course.name, section_id=self.section_id, section_type=self.section_type)
