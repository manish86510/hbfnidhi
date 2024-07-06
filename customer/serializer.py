from rest_framework import serializers
from masteradmin.models import SavingAccount

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingAccount
        fields = ['member', 'ifsc', 'account_no', 'branch_code', 'branch_name','account_balance']