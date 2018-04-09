from __future__ import absolute_import, unicode_literals

from .base import *


import os


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^@aruo_ql14%g&rmh@rmz97cjaaxd7ur%wg=v#-7*cq$n7q&=a'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

FLIGHTS_KEY = os.environ.get('flights_KEY')
SCHIPHOL_KEY = os.environ.get('schiphol_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'flights',
        'USER': 'davecaputo',
        'PASSWORD': os.environ.get('mysql_PW'),
        'HOST': 'localhost',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'flights_cache_table',
        'OPTIONS': {'MAX_ENTRIES': 10000},
        'TIMEOUT': None

    }
}

BROKER_URL = 'amqp://davecaputo:david@localhost:5672/myvhost'

INSTALLED_APPS += [
    'djcelery',
]


CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}


try:
    from .local import *
except ImportError:
    pass
