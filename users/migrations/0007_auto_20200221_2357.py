# Generated by Django 3.0.1 on 2020-02-21 23:57

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20200218_0537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='invalidate_token_before',
            field=models.DateTimeField(default=users.models.five_seconds_ago),
        ),
    ]