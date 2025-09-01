
import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

# SECRET_KEY = 'django-insecure-$m4s6^$3cwhz#2o0xyr^e#fc8y*vu#1bb$()-2u0#vt0jh40_e'
#DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'diagnoz.apps.DiagnozConfig',
]

INSTALLED_APPS += [
    'rest_framework',
    'django_filters',
    'corsheaders',

]


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'seam.urls'

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

WSGI_APPLICATION = 'seam.wsgi.application'
# CSRF_TRUSTED_ORIGINS = ['https://myserver.tld']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR / 'db.sqlite3)'),
        #        'ENGINE': 'mssql',
        #        'NAME': 'dbseam',
        #        'HOST': '127.0.0.1',
        #        'PORT': '50001',
        #        'OPTIONS': {'driver':'ODBC Driver 16 for SQL Server','SERVER':'STARIC777','Persist Security Info':'False','Integrated Security':'true'},
    },
}

# DATABASES = {
#    'default': {
#        'ENGINE': 'mssql',
#        'NAME':  'dbseam',
#        'OPTIONS': { 'driver': 'ODBC Driver 16 for SQL Server', },
#        'HOST':  'http://192.168.1.113',
#        'PORT': 50001,
#
#    },
#    'extra': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR / 'db.sqlite3)'),
#    }
#}


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



LANGUAGE_CODE = 'uk'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR / 'static/')
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR / 'media/')

STATICFILES_DIRS = [
    BASE_DIR / 'diagnoz/static'
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

