# Generated by Django 3.0.1 on 2020-02-25 18:01

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import schedules.models
import schedules.validators


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0005_auto_20200223_0652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestdata',
            name='coursebin',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, validators=[schedules.validators.coursebin_validator]),
        ),
        migrations.AlterField(
            model_name='requestdata',
            name='preference',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=schedules.models.createDefaultPreference, validators=[schedules.validators.preference_validator]),
        ),
    ]
