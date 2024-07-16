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
        from_account_no = from_account.account_no
        
        recipient_member_id = instance.member_id
        
        
        try:
            to_account = SavingAccount.objects.get(member=recipient_member_id)
        except SavingAccount.DoesNotExist:
            raise ValueError(f"SavingAccount with member ID {recipient_member_id} does not exist.")
        
          # Assuming you have a field in Transactions called recipient_member_id
        # recipient_member_id = instance.recipient_member_id  # Replace with your actual field
        
        # Fetch the recipient's SavingAccount based on recipient_member_id
        # to_account = SavingAccount.objects.get(member=recipient_member_id)
        to_account_no = to_account.account_no
        TransferTransactions.objects.create( 
            from_account_no=from_account_no,
            to_account_no=to_account_no,
            # to_account_no=instance.account_no.id,  # Replace with logic to find the correct 'to_account' transaction
            amount=instance.amount,
            description=instance.description
        )
