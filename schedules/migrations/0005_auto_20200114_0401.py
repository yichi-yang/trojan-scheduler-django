# Generated by Django 3.0.1 on 2020-01-14 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0004_schedule_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('PD', 'Pending'), ('PS', 'Processing'), ('DN', 'Done')], max_length=2),
        ),
    ]
