from __future__ import absolute_import, unicode_literals

from .base import *

import os

DEBUG = False

try:
    from .local import *
except ImportError:
    pass

SECRET_KEY = os.environ.get('secret_KEY')

FLIGHTS_KEY = os.environ.get('flights_KEY')
