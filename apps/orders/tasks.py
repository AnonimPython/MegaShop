#? Celery tasks: sending emails via RabbitMQ / Celery-задачи: отправка email через RabbitMQ
from celery import shared_task
from django.core.mail import send_mail
from config import logger


@shared_task
def send_order_confirmation(order_id, user_email):
    #* Sends order confirmation asynchronously via Celery / Отправляет подтверждение заказа асинхронно через Celery
    subject = f'Order confirmation #{order_id}'
    message = f'Order #{order_id} confirmed! Thank you for shopping at MegaShop.'
    logger.info(f'Sending order confirmation #{order_id} to {user_email}')
    send_mail(subject, message, 'noreply@megashop.ru', [user_email])


@shared_task
def send_order_status_update(order_id, new_status, user_email):
    #* Notification of order status change / Уведомление клиента об изменении статуса заказа
    from .models import Order
    status_display = dict(Order.STATUS_CHOICES).get(new_status, new_status)
    subject = f'Order #{order_id} status updated'
    message = f'Your order #{order_id} status changed to "{status_display}".'
    logger.info(f'Order #{order_id} status update: {status_display} → {user_email}')
    send_mail(subject, message, 'noreply@megashop.ru', [user_email])
