from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        from .utils import start_low_stock_scheduler
        try:
            start_low_stock_scheduler()
        except Exception as e:
            print(f"[InventoryConfig] Scheduler ishlamadi: {e}")
