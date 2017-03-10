from django.conf.urls import url

from data.views import EnrouteFlightsView, ArrivedFlightsView
from data.views import EnrouteArrivedFlightsView

urlpatterns = [
    url(r'^enroute/', EnrouteFlightsView.as_view(), name='enroute'),
    url(r'^arrived/', ArrivedFlightsView.as_view(), name='arrived'),
    url(r'^enroute_and_arrived/', EnrouteArrivedFlightsView.as_view(), 
        name='enroute_arrived'),
]
