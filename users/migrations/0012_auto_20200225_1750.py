# Generated by Django 3.0.1 on 2020-02-25 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0005_auto_20200223_0652'),
        ('users', '0011_auto_20200225_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='saved_task_data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user', to='schedules.RequestData'),
        ),
    ]