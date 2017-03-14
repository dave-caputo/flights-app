from django.conf.urls import url

from scraper.views import HeathrowDeparturesView

urlpatterns = [
    url(r'^heathrow_departures/', HeathrowDeparturesView.as_view(),
        name='heathrow_departures'),
]
