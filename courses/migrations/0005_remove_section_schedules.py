# Generated by Django 3.0.1 on 2020-01-15 03:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_section_schedules'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='schedules',
        ),
    ]
