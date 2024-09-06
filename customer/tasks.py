
# from celery import shared_task
# from django.core.mail import send_mail
# import logging

# logger = logging.getLogger(__name__)

# @shared_task
# def send_email_task(subject, message, recipient_list):
#     send_mail(
#         subject,
#         message,
#         'priyalsinghal38@gmail.com',
#         recipient_list,
#         fail_silently=False,
#     )

# tasks.py

# from celery import shared_task
# from django.utils import timezone
# from datetime import timedelta
# from masteradmin.models import PaymentSchedule

# @shared_task
# def enable_next_payment(rd_id):
#     # Get the next payment entry that is "Pending"
#     next_payment = PaymentSchedule.objects.filter(
#         rd_account_id=rd_id,
#         status='Pending'
#     ).order_by('payment_date').first()

#     if next_payment:
        

#         # Enable the payment entry by changing the status to "Open"
#         next_payment.status = 'Open'
#         next_payment.save()

#         print(f"Next payment for RD {rd_id} is now Open.")


from celery import shared_task

@shared_task
def add(x, y):
    return x+y

print(add)
