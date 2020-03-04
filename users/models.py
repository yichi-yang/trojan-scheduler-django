from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.contrib.auth.validators import UnicodeUsernameValidator
from datetime import timedelta
from django.core.exceptions import ValidationError
from schedules.models import RequestData
from .models import RequestData


def five_seconds_ago():
    return now() - timedelta(seconds=5)


def nicknameUniqueValidator(nickname):
    if not nickname:
        return
    if User.objects.all().filter(username=nickname).exists():
        raise ValidationError("A user with that username already exists.")


class User(AbstractUser):

    avatar = models.URLField(blank=True)
    email_verified = models.BooleanField(default=False)
    invalidate_token_before = models.DateTimeField(default=five_seconds_ago)

    USERNAME = 'US'
    FIRSTNAME = 'FR'
    LASTNAME = 'LS'
    FULLNAME = 'FL'
    NICKNAME = 'NC'

    DISPLAY_NAME_CHOICES = [
        (USERNAME, 'username'),
        (FIRSTNAME, 'first name'),
        (LASTNAME, 'last name'),
        (FULLNAME, 'full name'),
        (NICKNAME, 'nickname'),
    ]

    nickname = models.CharField(max_length=150,
                                null=True,
                                blank=True,
                                unique=True,
                                default="",
                                validators=(UnicodeUsernameValidator, nicknameUniqueValidator))
    display_name_choice = models.CharField(max_length=2,
                                           choices=DISPLAY_NAME_CHOICES,
                                           default=USERNAME)
    show_name = models.BooleanField(default=False)
    show_email = models.BooleanField(default=False)
    show_date_joined = models.BooleanField(default=False)
    saved_task_data = models.OneToOneField(RequestData,
                                           on_delete=models.PROTECT,
                                           related_name="owner")
