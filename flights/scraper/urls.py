from django.conf.urls import url

from scraper.views import HeathrowArrivalsView, HeathrowDeparturesView

urlpatterns = [
    url(r'^heathrow_departures/', HeathrowDeparturesView.as_view(),
        name='heathrow_departures'),
    url(r'^heathrow_arrivals/', HeathrowArrivalsView.as_view(),
        name='heathrow_arrivals'),
]
