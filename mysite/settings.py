"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from pathlib import Path
import datetime

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6vc%#!x-2s(a+i#w%vn+2am0_ug8=+sq8%k%-j8v*%oe(@v01$'

ALLOWED_HOSTS = [
    '0.0.0.0',
    '192.168.2.99'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'snippets',  # My app in this project
    'user',  # User management app in this project
    'graphene_django',  # ***
    'channels',  # Wasn't originally needed, but adding websockets
    'corsheaders'  # CORS - to allow React front-end on port 3000
]

MIDDLEWARE = [
    # CORS, recommended that this come before anything else that generates responses
    # https://www.stackhawk.com/blog/django-cors-guide/
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',  # CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

# https://docs.djangoproject.com/en/3.2/howto/overriding-templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # This allows a project-based template for all apps
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,  # Ensure App is listed in INSTALLED_APPS
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

ASGI_APPLICATION = 'mysite.asgi.application'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DB_USER = os.environ.get('POSTGRES_USER')
DB_PWD = os.environ.get('POSTGRES_PASSWORD')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'snippets',
        'USER': DB_USER,
        'PASSWORD': DB_PWD,
        'HOST': '192.168.2.99',
        'PORT': 5432,

    }
}

# The older, sqlite way
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     },
#     'OPTIONS': {
#         'timeout': 20,
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# ASGI/Channels version 3.0.4 development server
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# In this simple example we use in-process in-memory Channel layer.
# In a real-life cases you need Redis or something familiar.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

GRAPHENE = {
    # The path you configured in `routing.py`, including a leading slash.
    "SUBSCRIPTION_PATH": "/graphql/",
    # https://github.com/eamigo86/graphene-django-subscriptions/issues/7
    'MIDDLEWARE': [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
    ],
}

# https://django-graphql-jwt.domake.io/settings.html
GRAPHQL_JWT = {
    'JWT_PAYLOAD_HANDLER': 'mysite.schema.jwt_custom_payload_handler',
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LONG_RUNNING_REFRESH_TOKEN': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=10)  # The default is 10 days, but obviously this can be changed.
}

# This is easy, but opens the server up to attack
# CORS_ALLOW_ALL_ORIGINS = True

# This specifies a React front-end example I'm building.
CORS_ORIGIN_WHITELIST = (
    'http://192.168.2.99:3000',
)

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]
