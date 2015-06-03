# coding: utf-8
import os

from .base import *
from .utils import gen_get_config_or, read_config_file

config = read_config_file()
get_config_or = gen_get_config_or(config)


SECRET_KEY = get_config_or('APP', 'secret_key', SECRET_KEY)

DJANGO_HOME = os.path.join('/opt', 'django')
STATIC_DIR = os.path.join(DJANGO_HOME, 'static_files', 'mapa_cidadao')
MEDIA_ROOT = os.path.join(STATIC_DIR, 'media')
STATIC_ROOT = os.path.join(STATIC_DIR, 'static')

DATABASE_NAME = get_config_or('DATABASE', 'NAME', default='mapa_cidadao')
DATABASE_USER = get_config_or('DATABASE', 'USER', default='mapa_cidadao')
DATABASE_PASS = get_config_or('DATABASE', 'PASSWORD', default='')
DATABASE_HOST = get_config_or('DATABASE', 'HOST', default='localhost')
DATABASE_PORT = get_config_or('DATABASE', 'PORT', default='5432')

TEST = True
if TEST:
    FACEBOOK_APP_ID = get_config_or('FACEBOOK_TEST', 'FACEBOOK_APP_ID', default='')
    FACEBOOK_API_SECRET = get_config_or('FACEBOOK_TEST', 'FACEBOOK_API_SECRET', default='')
else:
    FACEBOOK_APP_ID = get_config_or('FACEBOOK', 'FACEBOOK_APP_ID', default='')
    FACEBOOK_API_SECRET = get_config_or('FACEBOOK', 'FACEBOOK_API_SECRET', default='')

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASS,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
    }
}

ALLOWED_HOSTS = ['104.131.23.39']

DEBUG = False
TEMPLATE_DEBUG = DEBUG


EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'
