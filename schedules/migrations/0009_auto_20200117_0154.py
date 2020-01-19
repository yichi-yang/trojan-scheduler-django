# Generated by Django 3.0.1 on 2020-01-17 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0008_schedule_sections'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='task',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]