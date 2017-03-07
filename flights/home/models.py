from __future__ import absolute_import, unicode_literals

from django.db import models
from wagtail.wagtailcore.models import Page

from home.utils import get_enroute_flights


class HomePage(Page):

    def get_context(self, request):
        context = super().get_context(request)
        context['enroute'] = get_enroute_flights()
        return context
