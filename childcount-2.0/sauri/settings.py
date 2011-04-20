#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: dgelvin

from django.conf import settings

import djcelery

INSTALLED_APPS.extend([
    'django.contrib.admin',
    'djcelery',
    'reversion',
    'south'
])

CELERY_DISABLE_RATE_LIMITS = True

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "mvp"
BROKER_PASSWORD = "africa"
BROKER_VHOST = "rsmsvhost"

CELERY_RESULT_BACKEND = 'amqp'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_LOADER='django'
CELERY_AMQP_TASK_RESULT_EXPIRES = 60*60
CELERY_IMPORTS = ('reportgen.definitions',)

DEBUG = TEMPLATE_DEBUG = True

settings.configure(**locals())
