# Generated by Django 3.0.1 on 2020-02-23 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0004_auto_20200218_0113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='description',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
