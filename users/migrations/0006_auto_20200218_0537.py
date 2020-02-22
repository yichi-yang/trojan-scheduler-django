# Generated by Django 3.0.1 on 2020-02-18 05:37

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20200217_0355'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='display_name_choice',
            field=models.CharField(choices=[('US', 'username'), ('FR', 'first name'), ('LS', 'last name'), ('FL', 'full name'), ('NC', 'nickname')], default='US', max_length=2),
        ),
        migrations.AddField(
            model_name='user',
            name='nickname',
            field=models.CharField(blank=True, max_length=150, validators=[django.contrib.auth.validators.UnicodeUsernameValidator]),
        ),
        migrations.AddField(
            model_name='user',
            name='show_date_joined',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='show_email',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='show_name',
            field=models.BooleanField(default=False),
        ),
    ]