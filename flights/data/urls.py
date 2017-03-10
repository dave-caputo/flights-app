from django.conf.urls import url

from data.views import EnrouteFlightsView, ArrivedFlightsView

urlpatterns = [
    url(r'^enroute/', EnrouteFlightsView.as_view(), name='enroute'),
    url(r'^arrived/', ArrivedFlightsView.as_view(), name='arrived'),
]
