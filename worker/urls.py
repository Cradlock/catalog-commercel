from django.urls import path
from .views import *

urlpatterns = [
    path("refresh/producst/",refresh_products),
    path("refresh/event/",refresh_events),
]


