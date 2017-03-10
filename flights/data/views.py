from django.shortcuts import render
from django.views.generic import TemplateView

from home.utils import get_enroute_flights, get_arrived_flights
from home.utils import get_enroute_arrived_flights, get_scheduled_flights
from home.utils import get_departed_flights


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
        context['arrived'] = get_arrived_flights()
        return context


class EnrouteArrivedFlightsView(TemplateView):
    template_name = 'data/enroute_arrived.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['arrived'] = get_arrived_flights()
        context['enroute'] = get_enroute_flights()
        context['enroute_arrived'] = get_enroute_arrived_flights()
        return context


class ScheduledFlightsView(TemplateView):
    template_name = 'data/scheduled.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scheduled'] = get_scheduled_flights()
        return context

class DepartedFlightsView(TemplateView):
    template_name = 'data/departed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departed'] = get_departed_flights()
        return context