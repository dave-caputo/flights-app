from django.conf.urls import url

from profiles.views import ProfileView

urlpatterns = [
    url(r'^$', ProfileView.as_view(), name='profile'),
]
