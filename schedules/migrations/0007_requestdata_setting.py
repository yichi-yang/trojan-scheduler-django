# Generated by Django 3.0.1 on 2020-02-28 04:04

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import schedules.models
import schedules.validators


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0006_auto_20200225_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestdata',
            name='setting',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=schedules.models.createDefaultSetting, validators=[schedules.validators.setting_validator]),
        ),
    ]
