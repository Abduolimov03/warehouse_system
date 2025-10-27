import threading
import time
from django.utils import timezone
from django.conf import settings
from .models import Product
import requests

_running = False  # Global flag

def send_telegram_message(text: str):
    """Telegramga xabar yuborish"""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"[Telegram Error] {e}")


def check_low_stock():
    """Har 6 soatda mahsulot zahirasini tekshiradi"""
    while True:
        low_stock_products = Product.objects.filter(quantity__lt=10)
        if low_stock_products.exists():
            message = "<b>⚠️ Low Stock Alert</b>\n\n"
            for p in low_stock_products:
                message += f"• {p.name} — <b>{p.quantity}</b> dona qoldi\n"

            send_telegram_message(message)
            print(f"[{timezone.now()}] Telegram orqali ogohlantirish yuborildi.")
        else:
            print(f"[{timezone.now()}] Hammasi joyida — stok yetarli.")
        time.sleep(21600)  # 6 soat kutish


def start_low_stock_scheduler():
    """Threadni faqat bir marta ishga tushiradi"""
    global _running
    if not _running:
        _running = True
        thread = threading.Thread(target=check_low_stock, daemon=True)
        thread.start()
        print("Low stock scheduler ishga tushdi ✅")
