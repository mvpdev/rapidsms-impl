#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

import os
import sys

import django.core.handlers.wsgi

filedir = os.path.dirname(__file__)  # this is in the rapidsms directory
rootpath = "/home/mvp/sms"

# load rapidsms config
os.environ['RAPIDSMS_INI'] = os.path.join(rootpath, 'local.ini')
from rapidsms.webui import settings


# NOTE!!!!!!!
# Save yourself hours of debugging
# and make sure that whenever you
# change the following celery settings
# you change them in settings.py also
settings.BROKER_HOST = "localhost"
settings.BROKER_PORT = 5672
settings.BROKER_USER = "mvp"
settings.BROKER_PASSWORD = "africa"
settings.BROKER_VHOST = "rsmsvhost"

settings.CELERY_RESULT_BACKEND = 'amqp'
settings.CELERY_DISABLE_RATE_LIMITS = True
settings.CELERY_LOADER='django'
settings.CELERY_AMQP_TASK_RESULT_EXPIRES = 60*60
settings.CELERY_IMPORTS = ('reportgen.definitions',)

# set rapidsms config as django config
os.environ['DJANGO_SETTINGS_MODULE'] = 'rapidsms.webui.settings'

# set rapidsms home
os.environ["RAPIDSMS_HOME"] = rootpath

# celery loader
os.environ["CELERY_LOADER"] = "django"

# add non-rapidsms django apps
from django.conf import settings
settings.INSTALLED_APPS.extend(['reversion'])

# create WSGI handler
application = django.core.handlers.wsgi.WSGIHandler()
