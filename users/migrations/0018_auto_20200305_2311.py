# Generated by Django 3.0.1 on 2020-03-05 23:11

import django.contrib.auth.validators
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20200305_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(blank=True, default='', max_length=150, null=True, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator, users.models.nicknameUniqueValidator]),
        ),
    ]
