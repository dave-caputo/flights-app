from django.core.cache import cache
from django.views.generic import TemplateView
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from scraper.source.heathrow_source import get_heathrow_flights
from scraper.source.gatwick_source import get_gatwick_flights
from scraper.source.schiphol_source import get_schiphol_flights


class FlightsView(TemplateView):
    template_name = 'scraper/flights.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        g = {'heathrow': get_heathrow_flights,
             'gatwick': get_gatwick_flights,
             'schiphol': get_schiphol_flights}
        airport = self.kwargs['airport']
        operation = self.kwargs['operation']
        context['flights'] = g[airport](operation)
        return context


class CarouselView(TemplateView):
    template_name = 'scraper/carousel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carousel_data'] = [
            ('heathrow', 'departures'),
            ('heathrow', 'arrivals'),
            ('gatwick', 'departures'),
            ('gatwick', 'arrivals'),
            ('schiphol', 'departures'),
            ('schiphol', 'arrivals')]
        return context


class CarouselFlightsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None, operation=None, airport=None):
        g = {'heathrow': get_heathrow_flights,
             'gatwick': get_gatwick_flights,
             'schiphol': get_schiphol_flights}
        data = g[airport](operation)
        return Response(data)


class FlightsAjaxView(TemplateView):
    template_name = 'scraper/flights_ajax.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        g = {'heathrow': get_heathrow_flights,
             'gatwick': get_gatwick_flights,
             'schiphol': get_schiphol_flights}
        airport = self.kwargs['airport']
        operation = self.kwargs['operation']
        context['flights'] = g[airport](operation)
        return context
