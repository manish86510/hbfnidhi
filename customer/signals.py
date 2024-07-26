# transactions/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from masteradmin.models import Transactions, SavingAccount
# import ipdb 
@receiver(post_save, sender=Transactions)
def update_balance(sender, instance, created, **kwargs):
    if created:
        transaction = instance
        from_account = SavingAccount.objects.get(member=transaction.from_account_no.member)
        # ipdb.set_trace()
        print("helllloo")
        if transaction.transaction_type == 'Transfer':
            to_account = SavingAccount.objects.get(member=transaction.to_account_no.member)
            
            # Deduct amount from the sender's account
            from_account.account_balance -= transaction.amount
            from_account.save()
            
            # Add amount to the recipient's account
            to_account.account_balance += transaction.amount
            to_account.save()
        else:
            # Handle other transaction types if necessary
            pass
