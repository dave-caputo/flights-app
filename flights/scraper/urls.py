from django.conf.urls import url

from scraper.views import CarrouselView, CarouselFlightsView, FlightsView


urlpatterns = [
    url(r'^flights/(?P<airport>\w+)/(?P<operation>\w+)/$',
        FlightsView.as_view(), name='flights'),

    url(r'^carrousel/', CarrouselView.as_view(),
        name='carrousel'),

    url(r'^carousel/(?P<airport>\w+)/(?P<operation>\w+)/$',
        CarouselFlightsView.as_view(),
        name='carousel_flights'),
]
