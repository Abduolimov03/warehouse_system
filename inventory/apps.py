from django.apps import AppConfig
import threading
import time


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):

        from .utils import start_low_stock_scheduler

        def delayed_start():
            time.sleep(5)
            start_low_stock_scheduler()

        threading.Thread(target=delayed_start, daemon=True).start()
        print("⏳ Scheduler 5 soniyadan so‘ng ishga tushadi...")
