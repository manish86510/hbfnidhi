import random
from django.forms import forms
from django.shortcuts import render, redirect
from masteradmin.models import *
from django.http import HttpResponse, JsonResponse
import datetime
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import time
from .forms import BankStatementForm

from django.shortcuts import render, get_object_or_404
from django.utils import timezone



def Customer_Login(request):
    if request.method == 'POST':
        enter_email = request.POST.get('username')
        enter_password = request.POST.get('pass')
        
        try:
            customer = Customer.objects.get(email=enter_email, password=enter_password)
            if customer.is_verify == 0:  # 0 means verified
                request.session['customer_name'] = customer.first_name
                request.session['customer_id'] = customer.member
                # request.session['customer_idd'] = customer.agent
                
                
                # Fetch SavingAccount object for the logged-in customer
                try:
                    saving_account = SavingAccount.objects.get(member=customer.member)
                    request.session['account_no'] = saving_account.account_no
                    request.session['branch_name'] = saving_account.branch_name
                    request.session['branch_code'] = saving_account.branch_code
                    request.session['ifsc'] = saving_account.ifsc
                    request.session['account_balance'] = saving_account.account_balance
                except SavingAccount.DoesNotExist:
                    # Handle case where SavingAccount does not exist for the customer
                    request.session['account_no'] = None
                    request.session['branch_name'] = None
                    request.session['branch_code'] = None
                    request.session['ifsc']=None
                    request.session['account_balance']='None'
                
                return render(request, 'Customer/Home.html', {'customer_id': customer.member})
            else:
                message = "Account not verified by admin"
                return render(request, 'Customer/login.html', {'message': message})
        except Customer.DoesNotExist:
            message = "Invalid Credentials"
            return render(request, 'Customer/login.html', {'message': message})
    else:
        return render(request, 'Customer/login.html')

    
    
# def customer_account(self):
#     return render(self,'Customer/Accounts.html')


# def customer_account(request):
    
#     member_id = request.session.get('customer_id')
   
    

#     # Fetch the SavingAccount details for the logged-in user
#     try:
#         saving_account = SavingAccount.objects.get(member=member_id)
#     except SavingAccount.DoesNotExist:
#         saving_account = None
    
#     context = {

#         'saving_account': saving_account,
#     }
    
#     return render(request, 'Customer/Accounts.html', context)



# import ipdb
#S Previous solution start
# def customer_account(request):
#     # ipdb.set_trace()
#     member_id = request.session.get('customer_id')
    
#     member  = Customer.objects.get(member=member_id)
 
#     transactions = Transactions.objects.filter(member_id=member.id)  # Assuming you have a DebitTransaction model with member and transaction_date fields

#     # Fetch the SavingAccount details for the logged-in user
#     try:
#         saving_account = SavingAccount.objects.get(member=member_id)
#     except SavingAccount.DoesNotExist:
#         saving_account = None
    
#     # Call the signal handler for each 'Transfer' type transaction
#     for transaction in transactions:
#         if transaction.transaction_type == 'Transfer':
#             create_transfer_transaction(sender=Transactions, instance=transaction, created=True)
    
#     context = {
#         'transactions': transactions,
#         'saving_account': saving_account,
#     }
    
#     return render(request, 'Customer/Accounts.html', context)
##S Previous solution end




# import ipdb
#the absolute correct code start

# def customer_account(request):
#     member_id = request.session.get('customer_id')
#     member = get_object_or_404(Customer, member=member_id)

#     try:
#         saving_account = SavingAccount.objects.get(member=member_id)
#         current_balance = Decimal(saving_account.account_balance)
#     except SavingAccount.DoesNotExist:
#         saving_account = None
#         current_balance = Decimal(0)

#     transactions = Transactions.objects.filter(member_id=member.id)

#     balances = []
#     for transaction in transactions:
#         if transaction.transaction_type == 'Transfer':
#             from_account = SavingAccount.objects.get(member=member_id)
#             to_account = SavingAccount.objects.get(id=transaction.account_no.id)
#             corresponding_saving_account = SavingAccount.objects.get(id=transaction.account_no.id)
#             transaction.corresponding_saving_account = corresponding_saving_account

#             Transfertransaction = TransferTransactions.objects.create(
#                 from_account_no=from_account,
#                 to_account_no=to_account,
#                 amount=transaction.amount,
#                 description=transaction.description
#             )
#             Transfertransaction.save()

#         current_balance -= Decimal(transaction.amount)
#         balances.append(current_balance)

#     form = BankStatementForm()

#     context = {
#         'transactions': zip(transactions, balances),
#         'saving_account': saving_account,
#         'form': form,
#     }

#     return render(request, 'Customer/Accounts.html', context)


# import ipdb

# def get_bank_statement(request):
#     ipdb.set_trace()
#     member_id = request.session.get('customer_id')
#     transactions = []

#     if request.method == 'POST':
#         form = BankStatementForm(request.POST)
#         if form.is_valid():
            
#             start_date = form.cleaned_data['start_date']
#             end_date = form.cleaned_data['end_date']
            
            
#             saving_account = get_object_or_404(SavingAccount, member=member_id)
            
#             # Retrieve transactions for the user within the date range
#             transactions = Transactions.objects.filter(
#                 account_no=saving_account.id,
#                 transaction_date__range=[start_date, end_date]
#             )
            
#             print(f"Transactions: {transactions}")
            
#     else:
#         form = BankStatementForm()
        
        
#         return render(request, 'Customer/get_bank_statement.html', {
#         'form': form,
#         'transactions': transactions,
#         'saving_account': saving_account,  # Pass the saving account to the template
#     })




# def customer_account(request):
#     member_id = request.session.get('customer_id')
#     member = get_object_or_404(Customer, member=member_id)

#     try:
#         saving_account = SavingAccount.objects.get(member=member_id)
#         current_balance = Decimal(saving_account.account_balance)
#     except SavingAccount.DoesNotExist:
#         saving_account = None
#         current_balance = Decimal(0)

#     transactions = Transactions.objects.filter(member_id=member.id)

#     balances = []
#     for transaction in transactions:
#         if transaction.transaction_type == 'Transfer':
#             from_account = SavingAccount.objects.get(member=member_id)
#             to_account = SavingAccount.objects.get(id=transaction.account_no.id)
#             corresponding_saving_account = SavingAccount.objects.get(id=transaction.account_no.id)
#             transaction.corresponding_saving_account = corresponding_saving_account

#             Transfertransaction = TransferTransactions.objects.create(
#                 from_account_no=from_account,
#                 to_account_no=to_account,
#                 amount=transaction.amount,
#                 description=transaction.description
#             )
#             Transfertransaction.save()

#         current_balance -= Decimal(transaction.amount)
#         balances.append(current_balance)

#     form = BankStatementForm()

#     context = {
#         'transactions': zip(transactions, balances),
#         'saving_account': saving_account,
#         'form': form,
#     }

#     return render(request, 'Customer/Accounts.html', context)


def customer_account(request):
    member_id = request.session.get('customer_id')
    member = get_object_or_404(Customer, member=member_id)

    try:
        saving_account = SavingAccount.objects.get(member=member_id)
        current_balance = Decimal(saving_account.account_balance)
    except SavingAccount.DoesNotExist:
        saving_account = None
        current_balance = Decimal(0)

    transactions = Transactions.objects.filter(member_id=member.id)
    form = BankStatementForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

        if timezone.is_naive(start_datetime):
            start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
        if timezone.is_naive(end_datetime):
            end_datetime = timezone.make_aware(end_datetime, timezone.get_current_timezone())

        transactions = transactions.filter(transaction_date__range=[start_datetime, end_datetime])

    balances = []
    for transaction in transactions:
        if transaction.transaction_type == 'Transfer':
            from_account = SavingAccount.objects.get(member=member_id)
            to_account = SavingAccount.objects.get(id=transaction.account_no.id)
            corresponding_saving_account = SavingAccount.objects.get(id=transaction.account_no.id)
            transaction.corresponding_saving_account = corresponding_saving_account

            Transfertransaction = TransferTransactions.objects.create(
                from_account_no=from_account,
                to_account_no=to_account,
                amount=transaction.amount,
                description=transaction.description
            )
            Transfertransaction.save()

        current_balance -= Decimal(transaction.amount)
        balances.append(current_balance)

    context = {
        'transactions': zip(transactions, balances),
        'saving_account': saving_account,
        'form': form,
    }

    return render(request, 'Customer/Accounts.html', context)

import ipdb



def get_bank_statement(request):
    ipdb.set_trace()
    member_id = request.session.get('customer_id')
    transactions = []
    saving_account = None

    if request.method == 'POST':
        form = BankStatementForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Convert dates to datetime
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
            
            # Convert naive datetimes to aware datetimes if necessary
            if timezone.is_naive(start_datetime):
                start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
            if timezone.is_naive(end_datetime):
                end_datetime = timezone.make_aware(end_datetime, timezone.get_current_timezone())
            
            # Debugging: Print member_id and date range
            print(f"Member ID: {member_id}, Start Date: {start_datetime}, End Date: {end_datetime}")
            
            # Retrieve the saving account
            # saving_account = get_object_or_404(SavingAccount, member=member_id)
            # print(f"Saving Account: {saving_account}")
            
            # Retrieve all transactions for the account
            # all_transactions = Transactions.objects.filter(account_no=saving_account)
            # print(f"All Transactions for account: {all_transactions}")

            # Retrieve transactions for the user within the date range
            # transactions = Transactions.objects.filter(
            #     account_no=saving_account,
            #     transaction_date__range=[start_datetime, end_datetime]
            # )
            customer = get_object_or_404(Customer, member=member_id)
            
            # Retrieve the saving account for the customer
            # saving_account = get_object_or_404(SavingAccount, account_no=customer)
            # print(f"Saving Account: {saving_account}")
            
            
            transactions = Transactions.objects.filter(
                # member=customer,
                transaction_date__range=[start_datetime, end_datetime]
            )
            
            
            # Debugging: Print the retrieved transactions
            print(f"Transactions: {transactions}")
    else:
        form = BankStatementForm()

    return render(request, 'Customer/get_bank_statement.html', {
        'form': form,
        'transactions': transactions,
        'saving_account': saving_account,
    })


class Dashboard():
    def index(self):
        return render(self, 'Customer/login.html')


def customer_logout(request):
        del request.session['customer_name']
        del request.session['customer_id']
        return render(request, 'Customer/login.html')




def customer_bill(self):
    return render(self,'Customer/Bill.html')


def customer_fd(self):
    if self.method == 'POST':
        if self.POST.get('nonbreak_roi'):
            tenure = self.POST.get('nonbreak_roi')
        else:
            tenure = self.POST.get('break_roi')
        try:
            customer = Customer.objects.get(id=self.session['customer_id'])
            scheme_info = FD_scheme.objects.get(tenure=tenure, breakable=self.POST.get('scheme'))
            account = random.randint(11111111, 99999999)
            FD.objects.create(
                account_number="FD"+str(account),
                tenure=tenure,
                amount=self.POST.get('amount'),
                rate_of_interest=self.POST.get('intrest_rate'),
                maturity_amount=self.POST.get('maturity'),
                status="Pending",
                is_active=0,
                scheme=scheme_info.id,
                created_date=models.DateTimeField(auto_now_add=True),
                associated_member=customer.member,
            ).save()
            message = "FD Applied successfully !"
            scheme_non_breakable = FD_scheme.objects.filter(breakable=0)
            scheme_breakable = FD_scheme.objects.filter(breakable=1)
            acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
            return render(self, 'Customer/FD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
                                                     'scheme_breakable': scheme_breakable, 'message': message})
        except Exception:
            message = "Something went wrong !"
            scheme_non_breakable = FD_scheme.objects.filter(breakable=0)
            scheme_breakable = FD_scheme.objects.filter(breakable=1)
            acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
            return render(self, 'Customer/FD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
                                                     'scheme_breakable': scheme_breakable, 'message': message})
    else:
        scheme_non_breakable=FD_scheme.objects.filter(breakable=0)
        scheme_breakable = FD_scheme.objects.filter(breakable=1)
        acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
        return render(self, 'Customer/FD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num, 'scheme_breakable': scheme_breakable})


def customer_rd(self):
    if self.method == 'POST':
        try:
            customer = Customer.objects.get(id=self.session['customer_id'])
            account = random.randint(11111111, 99999999)
            RD.objects.create(
                account_number="RD"+str(account),
                tenure=self.POST.get('tenure'),
                amount=self.POST.get('amount'),
                rate_of_interest=self.POST.get('intrest_rate'),
                maturity_amount=self.POST.get('maturity'),
                status="Pending",
                created_date=models.DateTimeField(auto_now_add=True),
                associated_member=customer.member,
            ).save()
            message = "RD Applied successfully !"
            scheme_non_breakable = RD_scheme.objects.filter(breakable=0)
            scheme_breakable = RD_scheme.objects.filter(breakable=1)
            acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
            return render(self, 'Customer/RD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
                                                     'scheme_breakable': scheme_breakable, 'message': message})
        except Exception:
            message = "Something went wrong !"
            scheme_non_breakable = RD_scheme.objects.filter(breakable=0)
            scheme_breakable = RD_scheme.objects.filter(breakable=1)
            acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
            return render(self, 'Customer/RD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
                                                     'scheme_breakable': scheme_breakable, 'message': message})
    else:
        scheme_non_breakable = RD_scheme.objects.filter(breakable=0)
        scheme_breakable = RD_scheme.objects.filter(breakable=1)
        acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
        return render(self, 'Customer/RD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
                                                 'scheme_breakable': scheme_breakable})


def customer_loan(self):
    return render(self, 'Customer/Loan.html')


# def customer_funds(self):
#     return render(self, 'Customer/Funds.html')

# def customer_funds(request):
#     if request.method == 'POST':
#         account = request.POST.get('account')
#         ifsc = request.POST.get('ifsc')
#         amount = request.POST.get('amount')
#         member_id = request.session.get('customer_id')
        
#         try:
#             amount = float(amount) 
#             saving_account = SavingAccount.objects.get(member=member_id)
#             account_balance = float(saving_account.account_balance) - amount # Convert to float
#              # Convert to float

#             after_transaction = account_balance - amount

#             # Save the data to the DebitTransaction model
#             DebitTransaction.objects.create(
#                 member=member_id,  # Assuming the member is the logged-in user 
#                 transaction="T" + str(int(time.time())),  # Example unique transaction ID
#                 beneficiary=account,
#                 amount=amount,
#                 bal_before_transaction=account_balance,
#                 bal_after_transaction=after_transaction,
#                 transaction_amount=amount,
#                 type_of_transaction="Transfer",
#                 debit_type="Online",
#                 remark="Fund Transfer",
#             )
            
#             # Redirect to a success page or the same form
#             # Replace with your success page URL or name
        
#         except SavingAccount.DoesNotExist:
#             # Handle the case where the saving account does not exist
#             return render(request, 'Customer/Funds.html', {'error': 'Saving account not found'})
        
#         except ValueError:
#             # Handle the case where conversion to float fails
#             return render(request, 'Customer/Funds.html', {'error': 'Invalid amount or account balance'})
    
#     return render(request, 'Customer/Funds.html')


# def customer_funds(request):
#     if request.method == 'POST':
#         account = request.POST.get('account')
#         ifsc = request.POST.get('ifsc')
#         amount = request.POST.get('amount')
#         member_id = request.session.get('customer_id')
        
#         try:
#             amount = float(amount)
#             saving_account = SavingAccount.objects.get(member=member_id)
#             account_balance = float(saving_account.account_balance)
        
            
#             after_transaction = account_balance - amount
#             account_balance = after_transaction

#             # Save the data to the DebitTransaction model
#             transaction_id = "T" + str(int(time.time()))
#             DebitTransaction.objects.create(
#                 member=member_id,
#                 transaction=transaction_id,
#                 beneficiary=account,
#                 amount=amount,
#                 bal_before_transaction=account_balance,
#                 bal_after_transaction=after_transaction,
#                 transaction_amount=amount,
#                 type_of_transaction="Transfer",
#                 debit_type="Online",
#                 remark="Fund Transfer",
#             )

#             # Save the data to the CreditTransaction model
#             CreditTransaction.objects.create(
#                 member=account,  # Assuming account is the beneficiary member id
#                 transaction=transaction_id,
#                 amount=str(amount),
#                 type_of_transaction="Credit",
#                 sender_account_no=saving_account.account_no,
#                 sender_bank_name="Your Bank Name",  # Replace with actual bank name
#                 debit_type="Online",
#                 remark="Fund Transfer",
#                 status=1  # Assuming 1 means successful
#             )
            
        
#         except SavingAccount.DoesNotExist:
#             # Handle the case where the saving account does not exist
#             return render(request, 'Customer/Funds.html', {'error': 'Saving account not found'})
        
        
#     return render(request, 'Customer/Funds.html')
 
 
#  The correct code writen by me
# def customer_funds(request):
#     if request.method == 'POST':
#         account = request.POST.get('account')
#         ifsc = request.POST.get('ifsc')
#         amount = request.POST.get('amount')
#         member_id = request.session.get('customer_id')
        
#         try:
#             amount = float(amount)
#             saving_account = SavingAccount.objects.get(member=member_id)
#             print(saving_account)
#             balance_before_transaction = float(saving_account.account_balance)

#             # Check if the account has enough balance
#             if balance_before_transaction < amount:
#                 return render(request, 'Customer/Funds.html', {'error': 'Insufficient balance'})

#             balance_after_transaction = balance_before_transaction - amount

#             # Save the data to the DebitTransaction model
#             transaction_id = "T" + str(int(time.time()))
#             DebitTransaction.objects.create(
#                 member=member_id,
#                 transaction=transaction_id,
#                 beneficiary=account,
#                 amount=amount,
#                 bal_before_transaction=balance_before_transaction,
#                 bal_after_transaction=balance_after_transaction,
#                 transaction_amount=amount,
#                 type_of_transaction="Transfer",
#                 debit_type="Online",
#                 remark="Fund Transfer",
#             )

#             # Update the SavingAccount balance
#             saving_account.account_balance = balance_after_transaction
#             saving_account.save()

#             # Save the data to the CreditTransaction model
#             CreditTransaction.objects.create(
#                 member=account,  # Assuming account is the beneficiary member id
#                 transaction=transaction_id,
#                 amount=str(amount),
#                 type_of_transaction="Credit",
#                 sender_account_no=saving_account.account_no,
#                 sender_bank_name="Your Bank Name",  # Replace with actual bank name
#                 debit_type="Online",
#                 remark="Fund Transfer",
#                 status=1  # Assuming 1 means successful
#             )
            
#             # Redirect to a success page or the same form
            
#         except SavingAccount.DoesNotExist:
#             # Handle the case where the saving account does not exist
#             return render(request, 'Customer/Funds.html', {'error': 'Saving account not found'})
        
#         except ValueError:
#             # Handle the case where conversion to float fails
#             return render(request, 'Customer/Funds.html', {'error': 'Invalid amount or account balance'})
    
#     return render(request, 'Customer/Funds.html')
# correct code complete



# s solution
# import ipdb;
# def customer_funds(request):
  
#     if request.method == 'POST':
#         account_no = request.POST.get('account')
#         ifsc = request.POST.get('ifsc')
#         amount = request.POST.get('amount')
#         member_id = request.session.get('customer_id')
    
#         try:                       
#             ipdb.set_trace()                  
#             saving_account = SavingAccount.objects.get(member=member_id)
#             # this is correct
#             memberC=Customer.objects.get(member=member_id)
#             print(memberC)
#             # Print specific fields of the Customer object
#             # member_id_str = memberC.member
#             # print("Member ID:", member_id_str)
            
#             # member_id_str = memberC.member  # Assuming this is a string with a prefix like "MA4754197"
#             # print("Member ID:", member_id_str)
            
#             # Extract the numeric part of the member ID (remove the prefix "MA")
#             # prefix = "MA"
#             # member_id_str.startswith(prefix)
#             # abb = int(member_id_str[len(prefix):]) # Remove prefix
            
            
#             # Convert numeric part to integer for processing if needed
#             # member_id_numeric = int(member_id_number)
            
#             # Combine prefix and numeric part for transaction
#             # member_id_with_prefix = f"{prefix}{abb}"
            
#             # print("Member ID with Prefix:", member_id_with_prefix)
            
                
            
#             # print("Member ID Number:",abb)
#             # hello = Customer.objects.get(member=member_id_with_prefix)
#             # print(hello)
#             transaction = Transactions(
#                 member_id=memberC.id,
#                 transaction_type='Transfer',
#                 amount=amount,
#                 description='Fund Transfer',
#                 account_no=saving_account
#             )
            
#             # print(Customer.objects.get(pk=member_idd))
#             transaction.save()
            
#             # Update account balance
#             saving_account.account_balance = float(saving_account.account_balance) - float(amount)
#             saving_account.save()

#               # Redirect to a success page or show a success message
#         except Customer.DoesNotExist:
#             return render(request, 'Customer/Funds.html', {'error': 'Customer not found.'})
#         except SavingAccount.DoesNotExist:
#             return render(request, 'Customer/Funds.html', {'error': 'Account not found.'})
#         except Exception as e:
#             return render(request, 'Customer/Funds.html', {'error': str(e)})

#     return render(request, 'Customer/Funds.html')  



# import ipdb;

def customer_funds(request):
    if request.method == 'POST':
        account_no = request.POST.get('account')
        amount = request.POST.get('amount')
        member_id = request.session.get('customer_id')
        # ipdb.set_trace()
        try:
            # Get the source saving account of the logged-in customer
            source_account = SavingAccount.objects.get(member=member_id)
           
            # Get the destination saving account based on the provided account number
            destination_account = SavingAccount.objects.get(account_no=account_no)
            
            # Create a transaction record for the transfer
            transaction = Transactions.objects.create(
                member_id=source_account.id,
                transaction_type='Transfer',
                amount=amount,
                description='Fund Transfer',
                account_no=destination_account
            ) 
            print("hello")
            transaction.save()
            
            # Update source account balance (deduct amount)
            # source_account.account_balance -= float(amount)
            # source_account.save()
            
            # Update destination account balance (add amount)
            # destination_account.account_balance += float(amount)
            # destination_account.save()
            
            # Redirect to a success page or show a success message
            # Replace with your success URL name
            
        except SavingAccount.DoesNotExist:
            return render(request, 'Customer/Funds.html', {'error': 'Destination account not found.'})
        except Exception as e:
            return render(request, 'Customer/Funds.html', {'error': str(e)})
    
    return render(request, 'Customer/Funds.html')



def customer_home(request):
    user_name=request.session['customer_name']
    member_id=request.session['customer_id']
    if user_name and member_id:
         return render(request,'Customer/Home.html')
    else:
        return render(request, 'Customer/login.html')

def customer_invest(self):
    return render(self,'Customer/Invest.html')


def customer_services(self):
    return render(self,'Customer/Services.html')

def customer_profile(request):
    if request.method == "POST":
           personal= {'first-name': request.POST.get("first-name"),'last-name':request.POST.get("last-name"),
                      'father_name': request.POST.get("father_name"),'gender':request.POST.get("gender"),
                      'dob': request.POST.get("dob")}
           Customer.objects.filter(email='ankur@gmail.com').update(first_name=personal['first-name'],
                                                                   last_name=personal['last-name'],
                                                                   father_name=personal['father_name'],
                                                                   gender=personal['gender'],
                                                                   dob=personal['dob'])
           contact = {'state': request.POST.get("state"), 'city': request.POST.get("city"),
                      'current-add': request.POST.get("current-add"), 'postal': request.POST.get("postal"),
                      'email': request.POST.get("email"), 'mobile': request.POST.get("mobile")}
           Customer.objects.filter(email='ankur@gmail.com').update(state=contact['state'],
                                                                   city=contact['city'],
                                                                   current_address=contact['current-add'],
                                                                   post_office=contact['postal'],
                                                                   email=contact['email'],
                                                                   mobile=contact['mobile'])

           bank = {'bank-name': request.POST.get("bank-name"), 'account': request.POST.get("account"),
                   'branch': request.POST.get("branch"), 'ifsc': request.POST.get("ifsc"),
                   'account-holder': request.POST.get("account-holder")}
           SavingAccount.objects.filter(member_id=2).update(branch_name=bank['bank-name'],
                                                            account_no=bank['account'],
                                                            branch_code=bank['branch'],
                                                            ifsc=bank['ifsc'],
                                                            status=bank['account-holder'])
           nominee = {'nominee-name': request.POST.get("nominee-name"), 'relation': request.POST.get("relation"),
                      'nominee-dob': request.POST.get("nominee-dob")}
           UserFamily.objects.filter(user_id=2).update(nominee_name=nominee['nominee-name'],
                                                       nominee_relationship=nominee['relation'],
                                                       nominee_dob=nominee['nominee-dob'])
           return redirect('profile')
    else:
        result = Customer.objects.get(email='ankur@gmail.com')
        payment=SavingAccount.objects.get(member_id=2)
        nominee=UserFamily.objects.get(user_id=2)
        return render(request,'Customer/Profile.html',{'result': result, 'payment': payment, 'nominee': nominee})

def customer_setting(request):
    if request.method == "POST":
            oldpass = request.POST.get("oldpassword")
            personal = {'newpass': request.POST.get("newpassword"), 'conpass': request.POST.get("conpassword")}
            result= Customer.objects.get(email='ankur@gmail.com')
            if result.password == oldpass :
                if personal['newpass'] == personal['conpass']:
                    Customer.objects.filter(email='ankur@gmail.com').update(password=personal['newpass'])
                    message = 'Password successfully change'
                    return render(request, 'Customer/Settings.html', {'message': message})
                else:
                   message='Password does not match'
                   return render(request,'Customer/Settings.html',{'message': message})
            else:
                message = 'Password incorrect'
                return render(request, 'Customer/Settings.html', {'message': message})
    else:
        return render(request,'Customer/Settings.html')


def interest_rate(request):
    id = request.GET.get('strUser')
    scheme = request.GET.get('scheme')
    rate = FD_scheme.objects.get(tenure=id, breakable=scheme)
    data = {'rate': rate.interest_rate}
    return JsonResponse(data)
