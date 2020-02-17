from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class User(AbstractUser):
    avatar = models.URLField(blank=True)
    email_verified = models.BooleanField(default=False)
    invalidate_token_before = models.DateTimeField(default=now)
