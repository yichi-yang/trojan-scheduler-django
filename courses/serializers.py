from rest_framework import serializers
from .models import Course, Section


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = ('section_id', 'section_type', 'need_clearance', 'registered', 'instructor',
                  'location', 'start', 'end', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')


class CourseSerializer(serializers.ModelSerializer):

    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'term', 'sections')
