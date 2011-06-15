#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: dgelvin
import time
from django.conf import settings

try:
    INSTALLED_APPS.extend([
    'django.contrib.admin',
    'reversion',
    'south',
    'djcelery',
    'alerts'
    ])
except NameError:
    print "Could not find INSTALLED_APPS"

DEBUG = False

# Set this so that reports generate in
# Tigrinya
LANGUAGE_CODE = 'am'
LANGUAGES = (
    ('en', 'English'),
    ('fr', 'French'),
    ('am', 'Tigrinya'),
)

# NOTE!!!!!!!
# Save yourself hours of debugging
# and make sure that whenever you
# change the following celery settings
# you change them in django_uwsgi.py also
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "childcount"
BROKER_PASSWORD = "childcount"
BROKER_VHOST = "ccvhost"

CELERY_RESULT_BACKEND = 'amqp'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_LOADER='django'
CELERY_AMQP_TASK_RESULT_EXPIRES = 60*60
CELERY_IMPORTS = ('reportgen.definitions',)

CACHE_BACKEND = 'file:///var/cache/childcount?max_entries=10000&cull_frequency=2'

ADMIN_MEDIA_PREFIX = '/adminmedia/'

TIME_ZONE = 'Africa/Kampala'
time.tzset()

settings.configure(**locals())
