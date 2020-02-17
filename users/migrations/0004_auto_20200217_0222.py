# Generated by Django 3.0.1 on 2020-02-17 02:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_iat_valid_after'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='iat_valid_after',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
