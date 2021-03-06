"""
Django settings for scheduler project.

Generated by 'django-admin startproject' using Django 3.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from datetime import timedelta
from decouple import config
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=config('SENTRY_DSN'),
    integrations=[DjangoIntegration(), CeleryIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default="",
                       cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = "origin-when-cross-origin"

ADMINS = config('ADMINS', default="",
                cast=lambda v: [
                    (s.split(',', 1)[0].strip(), s.split(',', 1)[1].strip())
                    for s in v.split(';') if ',' in s])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'courses',
    'schedules',
    'users',
    'custom_jwt'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scheduler.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scheduler.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'custom_jwt.authentication.IatJWTAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'scheduler.throttles.BurstRateThrottle',
        'scheduler.throttles.SustainedRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'burst': '180/min',
        'sustained': '24000/day',
        'email': '10/day',
        'scraper': '200/hour'
    },
    'DEFAULT_PAGINATION_CLASS': 'scheduler.pagination.PageNumberPaginationWithCount',
    'PAGE_SIZE': 20,
}


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

CONN_MAX_AGE = 60


# Custom user model

AUTH_USER_MODEL = 'users.User'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Celery settings

CELERY_BROKER_URL = config('CELERY_BROKER_URL',
                           default='redis://localhost:6379')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = config('STATIC_ROOT', default=None)

# USC Schedule of Class scraping settings

USC_SOC_SCRAPER_URL = 'https://classes.usc.edu/term-{term}/classes/{course}'
USC_SOC_SCRAPER_TIMEOUT = 10
USC_SOC_CACHE_REFRESH = 5 * 60

# scheduler timeout
SCHEDULER_TIME_LIMIT = 10


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'courses.scraper': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'courses.scraper': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'courses.scraper',
        }
    },
    'loggers': {
        'courses.scraper': {
            'handlers': ['courses.scraper', ],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=8),
    'AUTH_TOKEN_CLASSES': ('custom_jwt.tokens.IatAccessToken',),
}

# email verification token life time

EMAIL_TOKEN_LIFETIME = timedelta(hours=24)
RESET_TOKEN_LIFETIME = timedelta(hours=24)

# SMTP settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL', default='webmaster@localhost')
SERVER_EMAIL = config('SERVER_EMAIL', default='root@localhost')

# default semester in settings
CURRENT_SEMESTER = "20203"

SITE_BASE_URL = "https://scheduler.yichiyang.com"
