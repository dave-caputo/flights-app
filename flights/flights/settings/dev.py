from __future__ import absolute_import, unicode_literals

from .base import *


import os


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^@aruo_ql14%g&rmh@rmz97cjaaxd7ur%wg=v#-7*cq$n7q&=a'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

FLIGHTS_KEY = os.environ.get('flights_KEY')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'flights',
        'USER': 'davecaputo',
        'PASSWORD': os.environ.get('mysql_PW'),
        'HOST': 'localhost',
    }
}


try:
    from .local import *
except ImportError:
    pass
