"""
Django settings for rent_backend project.

Generated by 'django-admin startproject' using Django 1.11.27.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import base64
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e8a746$rb_+its$bgv+g!caznm*o@g8l()m)6q69p$tat@#wnu'

MIDTRANS_MERCHANT_ID = 'G624887214'
MIDTRANS_SERVER_KEY_SANDBOX = 'SB-Mid-server-atJ2H_V1IJgUskhGNhcu_F6_'
MIDTRANS_SERVER_KEY_PRODUCTION = 'Mid-server-cWH1WJBu2GDx09QrehkEktVi'

MIDTRANS_SANDBOX = 'https://app.sandbox.midtrans.com/snap/v1/transactions'
MIDTRANS_PRODUCTION = 'https://app.midtrans.com/snap/v1/transactions'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TASTYPIE_FULL_DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.0.2.2', '0.0.0.0', '192.168.0.101', 'www.sewanoproperty.com', 'sewanoproperty.com']
AUTH_USER_MODEL = "api.User"
APPEND_SLASH = False
# AUTHENTICATION_BACKENDS = ('api.backends.CustomBackend',)


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'fcm_django',
    'tastypie',
    'api.app.ApiConfig',
]

FCM_DJANGO_SETTINGS = {
    "APP_VERBOSE_NAME": "Sewano",
    # default: _('FCM Django')
    "FCM_SERVER_KEY": "AAAATgN8f_c:APA91bHObGjKyUmB6lfoNI-Iq1fad18cZP7FPfoe9jPtPAdKOlbcw2gdn3vvo1DFJQCBG2beQVruuHnhwhtIC_a-v-MjDTWHhU1MT4MnCI6Vq0_O20F492s61R4tuOINlRQp6qNj-meT",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": False,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rent_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'rent_backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'local': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sewano',
        'USER': 'lukas_kris',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'vistapro_sewano',
        'USER': 'vistapro_root',
        'PASSWORD': 'K}b8);5BveSN',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_L10N = True

SITE_ID = 2

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')  # Used to get static api_resources from web server

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Used to get media items from web server
MEDIA_ROOT = os.path.join(BASE_DIR, 'media').replace('\\', '/')

# Used to include media items in web pages
MEDIA_URL = '/media/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

# Activate Django-Heroku.
django_heroku.settings(locals())

if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']
