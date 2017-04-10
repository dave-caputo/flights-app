from django.conf.urls import url

from scraper.views import CarouselView, CarouselFlightsView, FlightsView, FlightsAjaxView


urlpatterns = [
    url(r'^flights/(?P<airport>\w+)/(?P<operation>\w+)/$',
        FlightsView.as_view(), name='flights'),

    url(r'^carousel/', CarouselView.as_view(),
        name='carousel'),

    url(r'^carousel/(?P<airport>\w+)/(?P<operation>\w+)/$',
        CarouselFlightsView.as_view(),
        name='carousel_flights'),

    url(r'^flights_ajax/(?P<airport>\w+)/(?P<operation>\w+)/$',
        FlightsAjaxView.as_view(), name='flights_ajax'),
]
