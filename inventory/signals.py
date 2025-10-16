from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EmployeeInventory, Product, ProductLog
from django.conf import settings
from django.core.mail import send_mail
import telegram

def send_telegram_message(text):
    try:
        bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=settings.TELEGRAM_ADMIN_CHAT_ID, text=text)
    except Exception as e:
        print('Telegram send error', e)

@receiver(post_save, sender=EmployeeInventory)
def on_employeeinventory_created(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        if product.quantity > 0:
            product.quantity -= 1
            product.save()
            ProductLog.objects.create(
                product = product,
                user = instance.employee.user,
                action = 'added_to_employee',
                quantity = 1
            )
            msg = f"{instance.employee.user.username} mahsulotni o'z omboriga qo'shdi: {product.name}. Qolgan: {product.quantity}"

            try:
                send_mail(
                    'Mahsulot otkazildi',
                    msg,
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER],
                    fail_silently=True
                )
            except Exception as e:
                ProductLog.objects.create(
                    product = product,
                    user = instance.employee.user,
                    action = 'removed_from_central',
                    quantity = 0
                )
                send_telegram_message(f"Diqqat! {product.name} markaziy omborda tugagan.")

