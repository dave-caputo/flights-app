from django.conf.urls import url

from scraper.views import HeathrowArrivalsView, HeathrowDeparturesView
from scraper.views import GatwickArrivalsView

urlpatterns = [
    url(r'^heathrow_departures/', HeathrowDeparturesView.as_view(),
        name='heathrow_departures'),
    url(r'^heathrow_arrivals/', HeathrowArrivalsView.as_view(),
        name='heathrow_arrivals'),
    url(r'^gatwick_arrivals/', GatwickArrivalsView.as_view(),
        name='gatwick_arrivals'),
]
