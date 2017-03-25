from django.conf.urls import url

from scraper.views import HeathrowArrivalsView, HeathrowDeparturesView
from scraper.views import GatwickArrivalsView, GatwickDeparturesView
from scraper.views import CarrouselView

urlpatterns = [
    url(r'^heathrow_departures/', HeathrowDeparturesView.as_view(),
        name='heathrow_departures'),
    url(r'^heathrow_arrivals/', HeathrowArrivalsView.as_view(),
        name='heathrow_arrivals'),
    url(r'^gatwick_arrivals/', GatwickArrivalsView.as_view(),
        name='gatwick_arrivals'),
    url(r'^gatwick_departures/', GatwickDeparturesView.as_view(),
        name='gatwick_departures'),
    url(r'^carrousel/', CarrouselView.as_view(),
        name='carrousel'),
]
