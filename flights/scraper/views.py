from django.views.generic import TemplateView
from django.shortcuts import render

from scraper.source.heathrow_source import get_heathrow_flights
from scraper.source.gatwick_source import get_gatwick_flights


# Create your views here.
class HeathrowDeparturesView(TemplateView):
    template_name = 'scraper/heathrow_departures.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departures'] = get_heathrow_flights('departures')
        return context


class HeathrowArrivalsView(TemplateView):
    template_name = 'scraper/heathrow_arrivals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['arrivals'] = get_heathrow_flights('arrivals')
        return context


class GatwickDeparturesView(TemplateView):
    template_name = 'scraper/gatwick_departures.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departures'] = get_gatwick_flights('departures')
        return context


class GatwickArrivalsView(TemplateView):
    template_name = 'scraper/gatwick_arrivals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['arrivals'] = get_gatwick_flights('arrivals')
        return context
