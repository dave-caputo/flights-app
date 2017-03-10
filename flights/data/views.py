from django.shortcuts import render
from django.views.generic import TemplateView

from home.utils import get_enroute_flights


class EnrouteFlightsView(TemplateView):
    template_name = 'data/enroute.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroute'] = get_enroute_flights()
        return context

class ArrivedFlightsView(TemplateView):
    template_name = 'data/arrived.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['arrived'] = get_enroute_flights()
        return context
