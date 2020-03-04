# Generated by Django 3.0.1 on 2020-03-02 06:04

import django.contrib.auth.validators
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20200227_0218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(max_length=150, null=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator, users.models.nicknameUniqueValidator]),
        ),
    ]
