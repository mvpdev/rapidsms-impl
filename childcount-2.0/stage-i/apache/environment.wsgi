import os
import sys
import glob
import re

PROJ_DIR = "/home/mvp/src/childcount"
INSTALL_ROOT = "/home/mvp/src/childcount/childcount"
VENV_ROOT = "/home/mvp/src/childcount/project_env"

for pdir in glob.glob(os.path.join(VENV_ROOT, "src", "*")):
	if not re.search("\.txt$", pdir):
		sys.path.append(pdir)

sys.path.insert(0, PROJ_DIR)
sys.path.insert(0, INSTALL_ROOT)
sys.path.insert(0, os.path.join(INSTALL_ROOT, 'apps'))
sys.path.insert(0, os.path.join(INSTALL_ROOT, 'lib'))
sys.path.insert(0, os.path.join(VENV_ROOT, 'lib', 'python2.6', 'site-packages'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'childcount.settings'

import django.core.handlers.wsgi

#filedir = os.path.dirname(__file__)  # this is in the rapidsms directory
#rootpath = "/home/mvp/src/childcount/childcount"

# load rapidsms config
os.environ['RAPIDSMS_INI'] = os.path.join(INSTALL_ROOT, 'local.ini')
from rapidsms.webui import settings

# set rapidsms config as django config
os.environ['DJANGO_SETTINGS_MODULE'] = 'rapidsms.webui.settings'

# set rapidsms home
os.environ["RAPIDSMS_HOME"] = INSTALL_ROOT

settings.BROKER_HOST = "localhost"
settings.BROKER_PORT = 5672
settings.BROKER_USER = "mvp"
settings.BROKER_PASSWORD = "africa"
settings.BROKER_VHOST = "rsmsvhost"

settings.CELERY_DISABLE_RATE_LIMITS = True
settings.CELERY_RESULT_BACKEND = 'amqp'
settings.CELERY_LOADER='django'
settings.CELERY_AMQP_TASK_RESULT_EXPIRES = 60*60
settings.CELERY_IMPORTS = ('reportgen.definitions',)

# add non-rapidsms django apps
from django.conf import settings
settings.INSTALLED_APPS.extend(['reversion'])

os.environ["CELERY_LOADER"] = "django"

# create WSGI handler
application = django.core.handlers.wsgi.WSGIHandler()
