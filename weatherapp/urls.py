from django.urls import path
from .views import start_weather

urlpatterns = [
    path("start-weather/", start_weather, name="start-weather"),
]
