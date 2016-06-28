from django.conf.urls import include, url
from account.views import create_oauth2_client

urlpatterns = [
    url(r'^create_oauth2_client/', create_oauth2_client, name='create_oauth2_client'),
]