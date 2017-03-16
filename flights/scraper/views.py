from django.views.generic import TemplateView
from django.shortcuts import render

from scraper.source.heathrow_source import get_heathrow_flights


# Create your views here.
class HeathrowDeparturesView(TemplateView):
    template_name = 'scraper/heathrow_departures.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departures'] = get_heathrow_flights('departures')
        return context
