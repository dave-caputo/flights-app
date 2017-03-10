from django.conf.urls import url

from data.views import EnrouteFlightsView

urlpatterns = [
    url(r'^enroute/', EnrouteFlightsView.as_view(), name='enroute'),
]
