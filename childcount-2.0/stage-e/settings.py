#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: dgelvin

from django.conf import settings

INSTALLED_APPS.extend([
    'django.contrib.admin',
    'reversion',
    'south',
    'djcelery',
])

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "childcount"
BROKER_PASSWORD = "childcount"
BROKER_VHOST = "ccvhost"

CELERY_DISABLE_RATE_LIMITS = True

settings.configure(**locals())
