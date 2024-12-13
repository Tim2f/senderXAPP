# s/urls.py

from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.send_sms, name="send_sms"),
 path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
]




