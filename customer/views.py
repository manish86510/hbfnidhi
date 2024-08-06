import csv
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
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from decimal import Decimal
from datetime import datetime, time as dt_time
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages


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
                    # request.session['account_balance'] = saving_account.account_balance
                    request.session['account_balance'] = str(saving_account.account_balance)  # Convert Decimal to string
                except SavingAccount.DoesNotExist:
                    # Handle case where SavingAccount does not exist for the customer
                    request.session['account_no'] = None
                    request.session['branch_name'] = None
                    request.session['branch_code'] = None
                    request.session['ifsc']=None
                    request.session['account_balance']='None'
                
                return render(request, 'Customer/Home.html', {'customer_id': customer.member, 'customer_name': customer.first_name})
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

import ipdb
def customer_account(request):
    ipdb.set_trace()
    member_id = request.session.get('customer_id')
    member = get_object_or_404(Customer, member=member_id)
    customer_name = member.first_name 

    try:
        saving_account = SavingAccount.objects.get(member=member_id)
        current_balance = Decimal(saving_account.account_balance)
    except SavingAccount.DoesNotExist:
        saving_account = None
        current_balance = Decimal(0)

    transactions = Transactions.objects.filter(member_id=member.id)

    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        if start_date and end_date:
            # Adjust end_date to include the entire end day
            end_date = datetime.combine(end_date, dt_time.max)
            transactions = transactions.filter(transaction_date__range=(start_date, end_date))
            
            
        
    balances = []
    running_balance = current_balance

    for transaction in transactions:
        if transaction.transaction_type == 'Transfer':
            # Find the transfer transactions related to this transaction
            transfers = TransferTransactions.objects.filter(
                from_account_no=transaction.account_no
            ) | TransferTransactions.objects.filter(
                to_account_no=transaction.account_no
            )
            
            for transfer in transfers:
                if transfer.from_account_no == transaction.account_no:
                    running_balance = Decimal(transfer.remaining_balance)
                elif transfer.to_account_no == transaction.account_no:
                    running_balance = Decimal(transfer.remaining_balance)
        
        else:
            # For non-transfer transactions, adjust the balance
            running_balance = Decimal(transaction.amount)

        balances.append(running_balance)

 
 

    paginator = Paginator(list(zip(transactions, balances)), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = BankStatementForm()

    context = {
        'page_obj': page_obj,
        'saving_account': saving_account,
        'form': form,
        'start_date': request.GET.get('startDate', ''),
        'end_date': request.GET.get('endDate', ''),
        'customer_name': customer_name, 
    }

    return render(request, 'Customer/Accounts.html', context)





def download_transactions(request):
    member_id = request.session.get('customer_id')
    member = get_object_or_404(Customer, member=member_id)

    try:
        saving_account = SavingAccount.objects.get(member=member_id)
    except SavingAccount.DoesNotExist:
        saving_account = None

    transactions = Transactions.objects.filter(member_id=member.id)

    # Create an HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Transaction ID', 'Beneficiary', 'Amount', 'Balance After Transaction', 'Date', 'Type'])

    current_balance = Decimal(saving_account.account_balance) if saving_account else Decimal(0)

    for transaction in transactions:
        if transaction.transaction_type == 'Transfer':
            try:
                corresponding_saving_account = SavingAccount.objects.get(id=transaction.account_no.id)
                transaction.corresponding_saving_account = corresponding_saving_account
            except SavingAccount.DoesNotExist:
                print("Account does not exist")

        current_balance -= Decimal(transaction.amount)
        
        writer.writerow([
            transaction.transaction_id,
            transaction.corresponding_saving_account.account_no if transaction.corresponding_saving_account else '',
            transaction.amount,
            current_balance,
            transaction.transaction_date,
            transaction.transaction_type,
        ])

    return response




def get_bank_statement(request):
    # ipdb.set_trace()
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


# def customer_fd(self):
#     if self.method == 'POST':
#         if self.POST.get('nonbreak_roi'):
#             tenure = self.POST.get('nonbreak_roi')
#         else:
#             tenure = self.POST.get('break_roi')
#         try:
#             customer = Customer.objects.get(id=self.session['customer_id'])
#             scheme_info = FD_scheme.objects.get(tenure=tenure, breakable=self.POST.get('scheme'))
#             account = random.randint(11111111, 99999999)
#             FD.objects.create(
#                 account_number="FD"+str(account),
#                 tenure=tenure,
#                 amount=self.POST.get('amount'),
#                 rate_of_interest=self.POST.get('intrest_rate'),
#                 maturity_amount=self.POST.get('maturity'),
#                 status="Pending",
#                 is_active=0,
#                 scheme=scheme_info.id,
#                 created_date=models.DateTimeField(auto_now_add=True),
#                 associated_member=customer.member,
#             ).save()
#             message = "FD Applied successfully !"
#             scheme_non_breakable = FD_scheme.objects.filter(breakable=0)
#             scheme_breakable = FD_scheme.objects.filter(breakable=1)
#             acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
#             return render(self, 'Customer/FD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
#                                                      'scheme_breakable': scheme_breakable, 'message': message})
#         except Exception:
#             message = "Something went wrong !"
#             scheme_non_breakable = FD_scheme.objects.filter(breakable=0)
#             scheme_breakable = FD_scheme.objects.filter(breakable=1)
#             acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
#             return render(self, 'Customer/FD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
#                                                      'scheme_breakable': scheme_breakable, 'message': message})
#     else:
#         scheme_non_breakable=FD_scheme.objects.filter(breakable=0)
#         scheme_breakable = FD_scheme.objects.filter(breakable=1)
#         acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
#         return render(self, 'Customer/FD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num, 'scheme_breakable': scheme_breakable})


# def customer_rd(self):
#     if self.method == 'POST':
#         try:
#             customer = Customer.objects.get(id=self.session['customer_id'])
#             account = random.randint(11111111, 99999999)
#             RecurringDeposit.objects.create(
#                 account_number="RD"+str(account),
#                 tenure=self.POST.get('tenure'),
#                 amount=self.POST.get('amount'),
#                 rate_of_interest=self.POST.get('intrest_rate'),
#                 maturity_amount=self.POST.get('maturity'),
#                 status="Pending",
#                 created_date=models.DateTimeField(auto_now_add=True),
#                 associated_member=customer.member,
#             ).save()
#             message = "RD Applied successfully !"
#             scheme_non_breakable = RD_scheme.objects.filter(breakable=0)
#             scheme_breakable = RD_scheme.objects.filter(breakable=1)
#             acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
#             return render(self, 'Customer/RD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
#                                                      'scheme_breakable': scheme_breakable, 'message': message})
#         except Exception:
#             message = "Something went wrong !"
#             scheme_non_breakable = RD_scheme.objects.filter(breakable=0)
#             scheme_breakable = RD_scheme.objects.filter(breakable=1)
#             acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
#             return render(self, 'Customer/RD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
#                                                      'scheme_breakable': scheme_breakable, 'message': message})
#     else:
#         scheme_non_breakable = RD_scheme.objects.filter(breakable=0)
#         scheme_breakable = RD_scheme.objects.filter(breakable=1)
#         acc_num = SavingAccount.objects.get(id=self.session['customer_id'])
#         return render(self, 'Customer/RD.html', {'scheme_non_breakable': scheme_non_breakable, 'acc_num': acc_num,
#                                                  'scheme_breakable': scheme_breakable})


# old#
# def customer_rd(self):
#     return render(self, 'Customer/RD.html')
def create_fd_view(request):
    return render(request, 'Customer/create_fd.html')

##### new new fd
import ipdb
def customer_fd(request):
    ipdb.set_trace()
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    
    try:
        fd_accounts = FixedDeposit.objects.filter(customer=customer)
        
        fd_with_details = []
        for fd in fd_accounts:
            # for maturity amount calculation
            interest_rate = Decimal(fd.interest_rate.interest_rate.strip('%')) / 100
            time_in_years = (fd.maturity_date - fd.start_date).days / 365
            maturity_amount =  fd.total_amount*(1 + interest_rate) ** Decimal(time_in_years)
            fd_with_details.append({
                'fd_account': fd,
                'interest_rate': fd.interest_rate.interest_rate,  # Assuming interest_rate is a foreign key
                'start_date': fd.start_date,
                'maturity_date': fd.maturity_date,
                'total_amount':fd.total_amount,
                'maturity_amount': maturity_amount
            })
            context = {
            'fd_accounts': fd_with_details
        }
        print(context)
        return render(request, 'Customer/FD.html', context)
    except Customer.DoesNotExist:
        return render(request, 'Customer/FD.html', {'error': 'Customer not found'})




### new new fd

import ipdb
def withdraw_fd(request, fd_id):
    ipdb.set_trace()
    fd = get_object_or_404(FixedDeposit, pk=fd_id)
    member_id = request.session.get('customer_id')
    saving_account = SavingAccount.objects.filter(member=member_id).first()
    
    
    balance = Decimal(saving_account.account_balance) 
    balance += fd.total_amount
    saving_account.account_balance = str(balance)
    saving_account.save() 

    # Update FD status to matured
    fd.status = 'Matured'
    fd.save()
    
    return render(request, 'Customer/FD.html')
    
    
    
    
#new new new 
import ipdb
def customer_rd(request):
    ipdb.set_trace()
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    
    try:
        rd_accounts = RecurringDeposit.objects.filter(customer=customer)
        
        rd_with_next_payment = []
        for rd in rd_accounts:
            # Calculate next payment date
            last_payment = PaymentSchedule.objects.filter(
                rd_account=rd,
                status='Completed'
            ).order_by('-payment_date').first()
            
            if last_payment:
                next_payment_date = last_payment.payment_date + timedelta(days=30)  # Assuming monthly payments
            else:
                next_payment_date = rd.start_date + timedelta(days=30)
            
            # next_payment = PaymentSchedule.objects.filter(
            #     rd_account=rd,
            #     payment_date=next_payment_date,
            #     status='Pending'
            # ).first()  # Use .first() to get the actual object if it exists
            # print(next_payment)
            
            # Get current payment details
            current_payments = PaymentSchedule.objects.filter(
                rd_account=rd
            ).order_by('-payment_date')
            
            print(current_payments)
            print(rd.interest_rate.interest_rate)
            
            
            rd_with_next_payment.append({
                'rd_account': rd,
                'next_payment_date': next_payment_date,
                'current_payments': current_payments,
                'interest_rate': rd.interest_rate.interest_rate 
            })
            
            payment = PaymentSchedule.objects.filter(rd_account=rd)
            start_date = request.GET.get('startDate')
            end_date = request.GET.get('endDate')
            
            
            if start_date and end_date:
                start_date = parse_date(start_date)
                end_date = parse_date(end_date)
                
                
                
                if start_date and end_date:
                    end_date = datetime.combine(end_date, dt_time.max)
                    payment = payment.filter(payment_date__range=(start_date, end_date))
                    
                    
            
            
            
            

        
            paginator = Paginator(rd_with_next_payment, 10)  # Show 10 items per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            # context = {'page_obj': page_obj}
            context = {
            'rd_with_next_payment': rd_with_next_payment,
             'start_date': request.GET.get('startDate', ''),
             'end_date': request.GET.get('endDate', ''),
            'page_obj': page_obj,
        }
            print(context)
            return render(request, 'Customer/RD.html', context)
    except Customer.DoesNotExist:
        return render(request, 'Customer/RD.html', {'error': 'Customer not found'})


# new new new



# new new new

import ipdb
def download_payment(request):
    ipdb.set_trace()
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    
   
    rd_accounts = RecurringDeposit.objects.filter(customer=customer)
        
    # for rd in rd_accounts:
    #     payment = PaymentSchedule.objects.filter(rd_account=rd) 

    # Create an HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payment.csv"'

    writer = csv.writer(response)
    writer.writerow([	'Payment Date',	'Amount',	'Status'])
    
    for rd in rd_accounts:
        payments = PaymentSchedule.objects.filter(rd_account=rd)
        for payment in payments:
            writer.writerow([
                # payment.transaction_id,
                payment.payment_date,
                payment.amount,
                payment.status,
            ])
    
    return response
   
  




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



import ipdb;


def customer_funds(request):
    member_id = request.session.get('customer_id')
    member = get_object_or_404(Customer, member=member_id)
    customer_name = member.first_name 

    ipdb.set_trace()
    
    if request.method == 'POST':
        account_no = request.POST.get('account')
        amount =int(request.POST.get('amount'))
        member_id = request.session.get('customer_id')
        ipdb.set_trace()
        
        
        try:
            # Get the source saving account of the logged-in customer
            source_account = SavingAccount.objects.get(member=member_id)
            destination_account = SavingAccount.objects.get(account_no=account_no)
            if(source_account.account_balance>=amount):
                source_account.account_balance-=amount
                destination_account.account_balance+=amount
            else:   
                raise Exception("not sufficient balance to transfer")
            # Get the destination saving account based on the provided account number
            
            # Create a transaction record for the transfer
                   # Record transaction for source account
            transaction = Transactions.objects.create(
                member_id=source_account.id,
                transaction_type='Transfer',
                amount=amount,
                description='Fund Transfer',
                account_no=destination_account
            ) 
            
            
            # Record transaction for destination account
            Transactions.objects.create(
                    member_id=destination_account.id,
                    transaction_type='Transfer',
                    amount=amount,
                    description='Fund Transfer from',
                    account_no=source_account
                )
            
            
            TransferTransactions.objects.create(
                    from_account_no=source_account,
                    to_account_no=destination_account,
                    amount=-amount,
                    description='Fund Transfer',
                    remaining_balance=source_account.account_balance
                )
            
            
            
            TransferTransactions.objects.create(
                from_account_no=destination_account,
                to_account_no=source_account,
                amount=amount,  # Amount added to destination account
                description='Fund Transfer',
                remaining_balance=destination_account.account_balance
            )
                
                
            print("hello 665")
            source_account.save()
            destination_account.save()
            
        except SavingAccount.DoesNotExist:
            return render(request, 'Customer/Funds.html', {'error': 'Destination account not found.'})
        except Exception as e:
            return render(request, 'Customer/Funds.html', {'error': str(e)})
    
    return render(request, 'Customer/Funds.html', { 'customer_name': customer_name})




def customer_home(request):
    member_id = request.session.get('customer_id')
    member = get_object_or_404(Customer, member=member_id)
    customer_name = member.first_name 
    user_name=request.session['customer_name']
    member_id=request.session['customer_id']
    if user_name and member_id:
         return render(request,'Customer/Home.html',{ 'customer_name': customer_name})
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




import ipdb    
def create_fd_account(self):
    ipdb.set_trace()
    if self.method == 'POST':
        try:
            member = self.POST.get('member_id')
            interest_rate_value = self.POST.get('interest_rate')
            start_date = self.POST.get('start_date')
            maturity_date = self.POST.get('maturity_date')
            total_amount = self.POST.get('total_amount')
            print(f"Received interest_rate: {interest_rate_value}")
            
            try:
                customer = Customer.objects.get(member=member)
            except Customer.DoesNotExist:
                message = "Invalid Member ID!"
                interest_rates = FD_scheme.objects.values_list('interest_rate', flat=True)
                return render(self, 'admin/create_fd.html', {'message': message, 'interest_rates': interest_rates})
            interest_rate_qs = FD_scheme.objects.filter(interest_rate=interest_rate_value)
            if not interest_rate_qs.exists():
                message = "Invalid interest rate!"
                interest_rates = FD_scheme.objects.values_list('interest_rate', flat=True)
                return render(self, 'admin/create_fd.html', {'message': message, 'interest_rates': interest_rates})
            interest_rate_obj = interest_rate_qs.first()
            account_number = "FD" + str(random.randint(1111111111, 9999999999))
                
            FD_account = FixedDeposit(
                account_number=account_number,
                customer=customer,
                interest_rate=interest_rate_obj,
                total_amount=total_amount,
                status='Active',  # Default status
                start_date=start_date,
                maturity_date=maturity_date,
                )
            FD_account.save()
            message = "FD created successfully!"
            interest_rates = FD_scheme.objects.values_list('interest_rate', flat=True)
            return render(self, 'customer/create_fd.html', {'message': message, 'interest_rates': interest_rates})
        except Exception as e:
            message = f"An error occurred: {e}"
            interest_rates = FD_scheme.objects.values_list('interest_rate', flat=True)
            return render(self, 'customer/create_fd.html', {'message': message, 'interest_rates': interest_rates})
            
    else:
        interest_rates = FD_scheme.objects.values_list('interest_rate', flat=True)
        return render(self, 'customer/create_fd.html', {'interest_rates': interest_rates})



