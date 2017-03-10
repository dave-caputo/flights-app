from django.conf.urls import url

from data.views import EnrouteFlightsView, ArrivedFlightsView
from data.views import EnrouteArrivedFlightsView, ScheduledFlightsView
from data.views import DepartedFlightsView, ScheduledDepartedFlightsView

urlpatterns = [
    url(r'^enroute/', EnrouteFlightsView.as_view(), name='enroute'),
    url(r'^arrived/', ArrivedFlightsView.as_view(), name='arrived'),
    url(r'^enroute_and_arrived/', EnrouteArrivedFlightsView.as_view(), 
        name='enroute_arrived'),
    url(r'^scheduled/', ScheduledFlightsView.as_view(), name='scheduled'),
    url(r'^departed/', DepartedFlightsView.as_view(), name='departed'),
    url(r'^scheduled_and_departed/', ScheduledDepartedFlightsView.as_view(), 
        name='scheduled_departed'),
]
