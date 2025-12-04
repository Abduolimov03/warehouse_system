from django.http import JsonResponse
from .weather import start_weather_scheduler

def start_weather(request):
    city = request.GET.get("city", "Tashkent")
    start_weather_scheduler(city)
    return JsonResponse({"status": "started", "city": city})

