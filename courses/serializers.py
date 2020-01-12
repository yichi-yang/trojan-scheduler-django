from rest_framework import serializers
from .models import Course, Section


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = ('section_id', 'section_type', 'need_clearance', 'registered', 'instructor',
                  'location', 'start', 'end', 'days', 'order_fetched')
        extra_kwargs = {'order_fetched': {'write_only': True}}


class SectionNotUniqueSerializer(serializers.ModelSerializer):

    class Meta(SectionSerializer.Meta):
        extra_kwargs = {'section_id': {'validators': []},
                        **SectionSerializer.Meta.extra_kwargs}


class SectionDetailSerializer(serializers.ModelSerializer):

    course_name = serializers.CharField(source='course.name', read_only=True)
    term = serializers.IntegerField(source='course.term', read_only=True)
    updated = serializers.DateTimeField(
        source='course.updated', read_only=True)

    class Meta:
        model = Section
        fields = ('course_name', 'term', 'section_id', 'section_type', 'need_clearance', 'registered', 'instructor',
                  'location', 'start', 'end', 'days', 'updated')


class CourseSerializer(serializers.ModelSerializer):

    sections = SectionNotUniqueSerializer(many=True)

    class Meta:
        model = Course
        fields = ('name', 'term', 'sections', 'updated')

    def create(self, validated_data):
        sections_data = validated_data.pop('sections')
        course = Course.objects.create(**validated_data)
        for section_data in sections_data:
            serializer = SectionSerializer(data=section_data)
            serializer.is_valid(raise_exception=True)
            Section.objects.create(course=course, **serializer.validated_data)
        return course

    def update(self, instance, validated_data):

        # get all sections and put them in a dict with their ids as keys
        sections_data = validated_data.pop('sections')
        sections_dict = {section_data['section_id']: section_data
                         for section_data in sections_data}

        # update attributes of the Course instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # select all related section instances
        section_instances = instance.sections.all()

        # for all existing section instances, update instances present in
        # the validated_data and delete the other
        for section_instance in section_instances:
            section_data = sections_dict.pop(section_instance.section_id, None)
            if section_data:
                serializer = SectionSerializer(
                    section_instance, data=section_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                section_instance.delete()

        # add sections that does not exist in the database
        for section_data in sections_dict.values():
            serializer = SectionSerializer(data=section_data)
            serializer.is_valid(raise_exception=True)
            Section.objects.create(
                course=instance, **serializer.validated_data)

        instance.save()

        return instance
