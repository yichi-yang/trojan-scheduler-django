# Generated by Django 3.0.1 on 2020-01-12 23:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='request_data',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='task', to='schedules.RequestData'),
        ),
    ]