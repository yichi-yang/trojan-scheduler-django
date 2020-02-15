from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    avatar = models.URLField(blank=True)
    email_verified = models.BooleanField(default=False)
