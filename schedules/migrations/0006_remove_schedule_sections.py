# Generated by Django 3.0.1 on 2020-01-14 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0005_auto_20200114_0401'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='sections',
        ),
    ]
