import datetime

from django import template

from data.airlines import AIRLINES
from data.airports import AIRPORTS

# EGLL: Heathrow
# EGKK: Gatwick
# EGSS: Stansted
# EGLC: London City
# EGGW: Luton

register = template.Library()


@register.filter(name='dformat')
def dformat(value):
    return datetime.datetime.fromtimestamp(
        int(value)).strftime('%a %d %b, %H:%M')


@register.filter(name='airline')
def airline(value):
    v = value[:3]
    for airline in AIRLINES:
        if v in airline.values():
            return airline['Short Name']


@register.filter(name='location')
def location(value):
    for airline in AIRPORTS:
        if value in airline['ident']:
            return airline['municipality']
