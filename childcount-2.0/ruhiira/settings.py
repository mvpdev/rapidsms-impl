#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: dgelvin

from django.conf import settings

INSTALLED_APPS.extend([
    'django.contrib.admin',
    'reversion',
    'south',
    'djcelery',
    'alerts'
])

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "rabbit"
BROKER_PASSWORD = "rabbit"
BROKER_VHOST = "virtualrabbit"

CELERY_DISABLE_RATE_LIMITS = True

ADMIN_MEDIA_PREFIX = '/adminmedia/'

settings.configure(**locals())
