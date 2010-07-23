#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: dgelvin

import os
import sys

import django.core.handlers.wsgi


filedir = os.path.dirname(__file__)  # this is in the rapidsms directory
rootpath = "/home/mvp/find_tb/sms"

# load rapidsms config
os.environ['RAPIDSMS_INI'] = os.path.join(rootpath, 'local.ini')
from rapidsms.webui import settings

# set rapidsms config as django config
os.environ['DJANGO_SETTINGS_MODULE'] = 'rapidsms.webui.settings'

# set rapidsms home
os.environ["RAPIDSMS_HOME"] = rootpath

# add non-rapidsms django apps
#from django.conf import settings
#settings.INSTALLED_APPS.extend(['reversion'])

from rapidsms import manager
manager.import_local_settings(settings, os.environ['RAPIDSMS_INI'])
# create WSGI handler
application = django.core.handlers.wsgi.WSGIHandler()
