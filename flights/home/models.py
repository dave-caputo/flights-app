from __future__ import absolute_import, unicode_literals

from django.db import models
from django.core.cache import cache

from wagtail.wagtailcore.models import Page


class HomePage(Page):
    
    def get_context(self, request):
        context = super().get_context(request)
        context['enroute'] = cache.get('Enroute', 'Not found')
        return context