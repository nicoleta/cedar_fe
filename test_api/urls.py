
from django.conf.urls import include, url
from test_api.views import test_api

urlpatterns = [
    url(r'^', test_api),
]
