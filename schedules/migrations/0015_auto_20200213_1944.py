# Generated by Django 3.0.1 on 2020-02-13 19:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0014_requestdata_public'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='schedule',
            options={'ordering': ['-task__created', 'id']},
        ),
    ]
