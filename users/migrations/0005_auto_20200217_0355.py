# Generated by Django 3.0.1 on 2020-02-17 03:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200217_0222'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='iat_valid_after',
            new_name='invalidate_token_before',
        ),
    ]