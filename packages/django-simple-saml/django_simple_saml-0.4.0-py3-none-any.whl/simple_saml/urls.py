from django.contrib import admin
from django.urls import path

from .views import saml_metadata_view

admin.autodiscover()

app_name = "simple_saml"

urlpatterns = [
    path("saml/", saml_metadata_view, name="saml_metadata"),
]
