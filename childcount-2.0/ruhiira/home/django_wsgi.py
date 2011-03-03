#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: rgaudin

import os
import sys
import glob
import time

import django.core.handlers.wsgi

filedir = os.path.dirname(__file__)  # this is in the rapidsms directory
rootpath = "/home/childcount/sms"

# load rapidsms config
os.environ['RAPIDSMS_INI'] = os.path.join(rootpath, 'local.ini')
from rapidsms.webui import settings

# set rapidsms config as django config
os.environ['DJANGO_SETTINGS_MODULE'] = 'rapidsms.webui.settings'

# set rapidsms home
os.environ["RAPIDSMS_HOME"] = rootpath

# Celery
os.environ['CELERY_LOADER'] = 'django'

# Reportlab fonts
os.environ['RL_TTFSearchPath'] = '/home/childcount/sms/lib/ccdoc'

# Get all dist packages
sys.path.extend(glob.glob('/usr/local/lib/python2.6/dist-packages/*'))
sys.path.extend('/home/childcount/sms/lib')

# add non-rapidsms django apps
from django.conf import settings
settings.INSTALLED_APPS.extend(['reversion'])

# add sms/lib to path
sys.path.extend([os.path.join(rootpath, 'lib')])
sys.path.extend([os.path.join(rootpath, 'ccdoc')])

# create WSGI handler
application = django.core.handlers.wsgi.WSGIHandler()

# Set timezone
os.environ['TZ'] = 'Africa/Kampala'
time.tzset()


