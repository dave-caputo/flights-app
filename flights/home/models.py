from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta

from django.db import models
from django.core.cache import cache

from wagtail.wagtailcore.models import Page


class HomePage(Page):

    def get_context(self, request):
        context = super().get_context(request)

        all_flights = []
        airports = ('EGLL', 'EGKK')
        for a in airports:
            c = cache.get('enroute_{}'.format(a), 'Not found')
            all_flights += c

        all_flights = sorted(all_flights,
                             key=lambda k: k['estimatedarrivaltime'])

        now = datetime.now()
        somedaysago = now - timedelta(days=3)

        current_flights = []
        for f in all_flights:
            if f['estimatedarrivaltime'] >= int(somedaysago.timestamp()):
                current_flights.append(f)
        context['enroute'] = current_flights
        return context
