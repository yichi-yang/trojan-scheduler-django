# Generated by Django 3.0.1 on 2020-01-15 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_remove_section_schedules'),
        ('schedules', '0007_remove_schedule_term'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='sections',
            field=models.ManyToManyField(to='courses.Section'),
        ),
    ]