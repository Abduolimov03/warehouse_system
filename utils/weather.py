import requests
import threading
import time
from django.conf import settings

def send_telegram_message(text: str):
    """
    Telegramga xabar yuboradi
    """
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"[Telegram Error] {e}")



def fetch_weather(city: str = "Tashkent/Angren"):
    api_key = getattr(settings, "OPENWEATHER_API_KEY", None)
    if not api_key:
        print("[Weather Error] OPENWEATHER_API_KEY settingsda mavjud emas")
        return None

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()

        temp = data['main']['temp']
        weather_desc = data['weather'][0]['description'].capitalize()
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        message = (
            f"🌤 Ob-havo - {city}\n"
            f"🌡 Harorat: {temp}°C\n"
            f"💧 Namlik: {humidity}%\n"
            f"💨 Shamol: {wind_speed} m/s\n"
            f"📝 Holat: {weather_desc}"
        )
        return message
    except Exception as e:
        print(f"[Weather Fetch Error] {e}")
        return None

def weather_scheduler(city: str = "Tashkent"):
    while True:
        message = fetch_weather(city)
        if message:
            send_telegram_message(message)
            print("✅ Telegramga ob-havo yuborildi")
        else:
            print("❌ Ob-havo ma'lumotini olishda xatolik")
        time.sleep(86400)  # 24 soat = 86400 soniya

def start_weather_scheduler(city: str = "Tashkent"):
    """
    Threadni ishga tushiradi (daemon=True, server ishlashda fon)
    """
    thread = threading.Thread(target=weather_scheduler, args=(city,), daemon=True)
    thread.start()
    print("⏳ Weather scheduler ishga tushdi...")
