#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8
# maintainer: dgelvin

import os

from django.conf import settings

INSTALLED_APPS.extend(['django_tracking','south','haystack'])
LOGIN_REDIRECT_URL='/findtb/'
HAYSTACK_SITECONF = 'findtb.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
PROJECT_ROOT = '/home/mvp/find_tb/sms/'
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_ROOT, 'whoosh_index')

settings.configure(**locals())
