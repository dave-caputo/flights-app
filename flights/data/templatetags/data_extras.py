import datetime

from django import template

register = template.Library()

def dformat(value):
    return datetime.datetime.fromtimestamp(int(value)).strftime('%a %d %b, %H:%M')

register.filter('dformat', dformat)
