# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from masteradmin.models import Transactions, TransferTransactions, SavingAccount
import ipdb
@receiver(post_save, sender=Transactions)
def create_transfer_transaction(sender, instance, created, **kwargs):
    if created and instance.transaction_type == 'Transfer':
        
        ipdb.set_trace()
        from_account = instance.account_no
        TransferTransactions.objects.create(
            from_account_no=from_account,
            to_account_no=instance.account_no.id,  # Replace with logic to find the correct 'to_account' transaction
            amount=instance.amount,
            description=instance.description
        )
