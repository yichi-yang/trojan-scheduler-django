# Generated by Django 3.0.1 on 2020-03-05 23:16

import django.contrib.auth.validators
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20200305_2311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(blank=True, default=None, max_length=150, null=True, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator, users.models.nicknameUniqueValidator]),
        ),
    ]