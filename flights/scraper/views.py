from django.core.cache import cache
from django.views.generic import TemplateView
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from scraper.source.heathrow_source import get_heathrow_flights
from scraper.source.gatwick_source import get_gatwick_flights


# Create your views here.
class HeathrowDeparturesView(TemplateView):
    template_name = 'scraper/heathrow_departures.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            flights = get_heathrow_flights('departures')
            cache.set('heathrow_departures', flights, None)
            context['departures'] = flights
        except:
            flights = cache.get('heathrow_departures', 'Not Available')
            context['departures'] = flights
        # context['departures'] = get_heathrow_flights('departures')
        return context


class HeathrowArrivalsView(TemplateView):
    template_name = 'scraper/heathrow_arrivals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            flights = get_heathrow_flights('arrivals')
            # cache.set('heathrow_arrivals', flights, None)
            context['arrivals'] = flights
        except:
            flights = cache.get('heathrow_departures', 'Not Available')
            context['arrivals'] = flights
        # context['arrivals'] = get_heathrow_flights('arrivals')
        return context


class GatwickDeparturesView(TemplateView):
    template_name = 'scraper/gatwick_departures.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            flights = get_gatwick_flights('departures')
            # cache.set('gatwick_departures', flights, None)
            context['departures'] = flights
        except:
            # flights = cache.get('gatwick_departures', 'Not Available')
            context['departures'] = flights
        # context['departures'] = get_gatwick_flights('departures')
        return context


class GatwickArrivalsView(TemplateView):
    template_name = 'scraper/gatwick_arrivals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['arrivals'] = get_gatwick_flights('arrivals')
        return context


class CarrouselView(TemplateView):
    template_name = 'scraper/carrousel.html'


class CarouselFlightsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None, operation=None, airport=None):
        g = {'heathrow': get_heathrow_flights,
             'gatwick': get_gatwick_flights}
        data = g[airport](operation)
        return Response(data)
