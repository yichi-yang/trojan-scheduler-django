# Generated by Django 3.0.1 on 2020-02-27 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='closed',
            field=models.BooleanField(default=False),
        ),
    ]
