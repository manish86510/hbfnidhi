
from celery import shared_task
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email_task(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'priyalsinghal38@gmail.com',
        recipient_list,
        fail_silently=False,
    )

