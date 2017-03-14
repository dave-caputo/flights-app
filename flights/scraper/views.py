from django.views.generic import TemplateView
from django.shortcuts import render


# Create your views here.
class HeathrowDeparturesView(TemplateView):
    template_name = 'scraper/heathrow_departures.html'
