import csv
from django.contrib.auth.forms import PasswordChangeForm
import random
from django.contrib.auth.hashers import make_password

from django.forms import forms
from django.shortcuts import render, redirect
from customer.tasks import enable_next_payment
from masteradmin.models import *
from django.http import HttpResponse, JsonResponse
import datetime
from django.contrib.auth import update_session_auth_hash

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
# from .tasks import send_email_task
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import math



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
                
                saving_account = SavingAccount.objects.filter(member=customer.member).first()

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

    
# def get_bank_statement(request ):

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
        
            
#     else:
#         form = BankStatementForm()
        
        
#         return render(request, 'Customer/get_bank_statement.html', {
#         'form': form,
#         'transactions': transactions,
#         'saving_account': saving_account,  # Pass the saving account to the template
#     })




def customer_account(request, account_no):

    member_id = request.session.get('customer_id')
    member = get_object_or_404(Customer, member=member_id)
    customer_name = member.first_name 

    try:
        saving_account = SavingAccount.objects.get(member=member_id, account_no=account_no)
        current_balance = Decimal(saving_account.account_balance)
    except SavingAccount.DoesNotExist:
        saving_account = None
        current_balance = Decimal(0)

    # Fetch only transfer transactions related to the account number
    transfer_transactions = TransferTransactions.objects.filter(
        from_account_no__account_no=account_no
    )
    
    TransferTransactions.objects.filter(
        from_account_no__account_no=account_no
    )
            
    
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        if start_date and end_date:
            # Adjust end_date to include the entire end day
            end_date = datetime.combine(end_date, dt_time.max)
            transfer_transactions = transfer_transactions.filter(transfer_date__range=(start_date, end_date))

    balances = []
    running_balance = current_balance
    for transfer in transfer_transactions:
        # Update the balance based on the transfer transaction
        if transfer.from_account_no.account_no == account_no:
            running_balance = Decimal(transfer.remaining_balance)
            balances.append(running_balance)

    # Pair transactions with their respective balances
    transactions_and_balances = list(zip(transfer_transactions, balances))
    
        
    paginator = Paginator(transactions_and_balances, 10)
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
            
            customer = get_object_or_404(Customer, member=member_id)
            
            
            
            transactions = Transactions.objects.filter(
                # member=customer,
                transaction_date__range=[start_datetime, end_datetime]
            )
       
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



def create_fd_view(request):
    return render(request, 'Customer/create_fd.html')



def customer_fd(request):
    
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    fd_accounts = FixedDeposit.objects.filter(customer=customer)

    if not fd_accounts.exists():
        return render(request, 'Customer/fd_Home.html')

    fd_with_details = []
    for fd in fd_accounts:
        # Determine FD status and calculate details
        # Add status-specific handling here if needed
        interest_rate = Decimal(fd.interest_rate.interest_rate.strip('%')) / 100
        time_in_years = (fd.maturity_date - fd.start_date).days / 365
        maturity_amount = fd.total_amount * (1 + interest_rate) ** Decimal(time_in_years)
        fd.maturity_amount = maturity_amount
        fd.save()

        fd_with_details.append({
            'fd_account': fd,
            'interest_rate': fd.interest_rate.interest_rate,
            'start_date': fd.start_date,
            'maturity_date': fd.maturity_date,
            'total_amount': fd.total_amount,
            'maturity_amount': maturity_amount,
            'account_number': fd.account_number,
        })

    # Check FD status and render appropriate template
    if any(fd.status == 'Active' for fd in fd_accounts):
        return render(request, 'Customer/FD.html', {'fd_accounts': fd_with_details})

    return render(request, 'Customer/fd_Home.html')





def withdraw_fd(request, fd_id):
    fd = get_object_or_404(FixedDeposit, pk=fd_id)
    member_id = request.session.get('customer_id')
   
    
    customer = get_object_or_404(Customer, member=member_id)
  
    saving_account = SavingAccount.objects.filter(member=member_id).first()
   
    
    if saving_account is None:
        # Handle the case where no saving account is found
        return render(request, 'Customer/FD.html', {'error': 'No saving account found for the customer.'})
   
    
    if fd.status != 'Active':
        # Handle the case where FD status is not Active
        return render(request, 'Customer/FD.html', {'error': 'FD status is not active.'})

    
    balance = Decimal(saving_account.account_balance) 
    balance += fd.maturity_amount
    saving_account.account_balance = str(balance)
    saving_account.save() 

    # Update FD status to matured
    fd.status = 'Matured'
    fd.save()
    
    
    TransferTransactions.objects.create(
                from_account_no=saving_account,
                to_account_no=None,  # or specify another account if needed
                amount=fd.maturity_amount,
                transfer_date=datetime.now().date(),
                remaining_balance=saving_account.account_balance,
                
                description=f'Withdrawn amount from FD account'
            )
    
    
    Transactions.objects.create(
        member_id=customer.id,
        account_no=saving_account,
        transaction_type='FD Withdrawal',
        amount=fd.maturity_amount,
        description=f'Withdrawn from FD account {fd.account_number}'
    )
    
    
    return render(request, 'Customer/fd_matured.html',  {'message': 'Your FD account has been successfully withdrawn.'})
    




# def fd_matured(request):
#     return render(request, 'Customer/fd_matured.html')



def fd_home(request):  
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    
    
    fd_accounts = FixedDeposit.objects.filter(customer=customer)
    if not fd_accounts.exists():
        # No FD accounts found, render fd_Home.html
        return render(request, 'Customer/fd_Home.html')
    fd_with_details = []
    for fd in fd_accounts:
            # for maturity amount calculation
            interest_rate = Decimal(fd.interest_rate.interest_rate.strip('%')) / 100
            time_in_years = (fd.maturity_date - fd.start_date).days / 365
            maturity_amount =  fd.total_amount*(1 + interest_rate) ** Decimal(time_in_years)
            fd.maturity_amount = maturity_amount
            fd.save() 
            fd_with_details.append({
                'fd_account': fd,
                'interest_rate': fd.interest_rate.interest_rate, 
                'start_date': fd.start_date,
                'maturity_date': fd.maturity_date,
                'total_amount':fd.total_amount,
                'maturity_amount': maturity_amount,
                'account_number': fd.account_number,
            })
            context = {
            'fd_accounts': fd_with_details
        }
     
     
        
    fd_status = fd_accounts.values_list('status', flat=True).distinct()
    
    if 'Matured' in fd_status:
        # If any FD status is 'Matured', render fd_matured.html
        return render(request, 'Customer/fd_matured.html', {'fd_accounts': fd_accounts})
    elif 'Active' in fd_status:
        # If any FD status is 'Active', render FD.html
        context = {'fd_accounts': fd_accounts}
        return render(request, 'Customer/FD.html', context)
    else:
        # Default case if no specific FD status is found
        return render(request, 'Customer/fd_Home.html')
    
    
    
  
def rd_home(request):
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    
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
        
        # Get current payment details
        current_payments = PaymentSchedule.objects.filter(
            rd_account=rd
        ).order_by('-payment_date')
        
        maturity_amount = calculate_rd_maturity_amount(rd)
        rd.maturity_amount = maturity_amount
        rd.save()
        
        rd_with_next_payment.append({
            'rd_account': rd,
            'next_payment_date': next_payment_date,
            'current_payments': current_payments,
            'interest_rate': rd.interest_rate.interest_rate,
            'maturity_amount': maturity_amount
        })
    
    # Handle date filtering
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        
        if start_date and end_date:
            end_date = dt.combine(end_date, dt.max.time())
            payment = PaymentSchedule.objects.filter(rd_account__in=rd_accounts, payment_date__range=(start_date, end_date))
        else:
            payment = PaymentSchedule.objects.filter(rd_account__in=rd_accounts)
    else:
        payment = PaymentSchedule.objects.filter(rd_account__in=rd_accounts)
    
    paginator = Paginator(rd_with_next_payment, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'rd_with_next_payment': rd_with_next_payment,
        'start_date': start_date or '',
        'end_date': end_date or '',
        'page_obj': page_obj,
    }
    
    rd_status = rd_accounts.values_list('status', flat=True).distinct()
    
    if 'Matured' in rd_status:
        return render(request, 'Customer/rd_matured.html', {'rd_accounts': rd_accounts})
    elif 'Active' in rd_status:
        return render(request, 'Customer/RD.html', context)
    else:
        return render(request, 'Customer/rd_Home.html')
    
       
    
      




def calculate_rd_maturity_amount(rd):
    # P: Monthly installment
    P = Decimal(rd.monthly_installment)
    
    # r: Monthly interest rate (annual interest rate divided by 12)
    # Remove the '%' sign and convert the remaining string to a Decimal
    annual_rate_str = rd.interest_rate.interest_rate.strip().replace('%', '')
    annual_rate = Decimal(annual_rate_str)
    
    # Convert annual interest rate to a monthly rate
    r = annual_rate / Decimal('1200')  # 12 * 100
    
    # n: Number of installments (months)
    start_date = rd.start_date
    maturity_date = rd.maturity_date
    n = ((maturity_date.year - start_date.year) * 12) + (maturity_date.month - start_date.month)
    
    # Maturity amount formula
    maturity_amount = P * (((1 + r)**n - 1) / r) * (1 + r)
    
    return round(maturity_amount, 2)


#new new new 

def customer_rd(request):
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
                
                # Trigger the Celery task to enable the next payment after 5 minutes
                # enable_next_payment.delay(rd.id)
                enable_next_payment.apply_async((rd.id,), countdown=120)
                
                
            else:
                next_payment_date = rd.start_date + timedelta(days=30)
            
            # next_payment = PaymentSchedule.objects.filter(
            #     rd_account=rd,
            #     payment_date=next_payment_date,
            #     status='Pending'
            # ).first()  # Use .first() to get the actual object if it exists
            # 
            
            
            # Get current payment details
            current_payments = PaymentSchedule.objects.filter(
                rd_account=rd,
                status__in=['Completed', 'Open']
            ).order_by('-payment_date')
            
            maturity_amount = calculate_rd_maturity_amount(rd)
            rd.maturity_amount = maturity_amount
            rd.save()
            
            
            rd_with_next_payment.append({
                'rd_account': rd,
                'next_payment_date': next_payment_date,
                'current_payments': current_payments,
                'interest_rate': rd.interest_rate.interest_rate,
                'maturity_amount': maturity_amount
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
            
            return render(request, 'Customer/RD.html', context)
    except Customer.DoesNotExist:
        return render(request, 'Customer/RD.html', {'error': 'Customer not found'})



# def deposit(request):
#     member_id = request.session.get('customer_id')
#     customer = get_object_or_404(Customer, member=member_id)
    
#     try:
#         # Assuming you're dealing with one RecurringDeposit per customer
#         rd_account = RecurringDeposit.objects.get(customer=customer)
        
        
#         # Create a new payment schedule entry
#         new_payment = PaymentSchedule.objects.create(
#             rd_account=rd_account,
#             payment_date='2024-06-20',
#             amount=4000,
#             status='Completed'
#         )
        

#         return render(request, 'Customer/RD.html')
    
#     except RecurringDeposit.DoesNotExist:
#         # Handle the case where no RecurringDeposit exists for this customer
#         return render(request, 'Customer/RD.html', {'error': 'No RecurringDeposit found for this customer.'})
    
#     except Customer.DoesNotExist:
#         # Handle the case where no customer exists
#         return render(request, 'Customer/RD.html', {'error': 'Customer not found.'})


def download_payment(request):
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


def calculate_amortization_schedule(amount, annual_rate, tenure_months):
    # Convert annual rate percentage to a decimal and calculate monthly rate
    monthly_rate = Decimal(annual_rate) / Decimal(12 * 100)  # Convert annual rate to monthly rate
    tenure_months = Decimal(tenure_months)
    
    # Avoid division by zero
    if monthly_rate == 0:
        monthly_payment = amount / tenure_months
    else:
        # Calculate monthly payment
        numerator = monthly_rate * (Decimal(1) + monthly_rate) ** tenure_months
        denominator = (Decimal(1) + monthly_rate) ** tenure_months - 1
        monthly_payment = amount * numerator / denominator
    
    schedule = []
    balance = Decimal(amount)

    for month in range(1, int(tenure_months) + 1):
        interest = balance * monthly_rate
        principal = monthly_payment - interest
        balance -= principal
        
        # Append schedule entry
        schedule.append({
            'month': month,
            'principal': round(principal, 2),
            'interest': round(interest, 2),
            'total_payment': round(monthly_payment, 2),
            'balance': round(balance, 2) if balance > 0 else 0
        })
        
    return schedule



def customer_loan(request):
    
    member_id = request.session.get('customer_id')
    
    customer = get_object_or_404(Customer, member=member_id)
    
    # Fetch personal loans for the customer
    personal_loans = Personal_loan.objects.filter(user=customer)
    
    # Calculate EMI for each loan
    for loan in personal_loans:
        try:
            loan_amount = Decimal(loan.amount)
            loan_tenure = int(loan.tenure)
            annual_rate = Decimal(loan.interest_rate.replace('%', '').strip())  # Strip any '%' and whitespace
            loan.schedule = calculate_amortization_schedule(loan_amount, annual_rate, loan_tenure)
        except InvalidOperation:
            loan.schedule = []# Handle invalid conversion by setting an empty schedule
    
  
    context = {
        'customer': customer,
        'personal_loans': personal_loans
    }
    return render(request, 'Customer/Loan.html', context)




def customer_fd(request):
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    
    try:
        fd_accounts = FixedDeposit.objects.filter(customer=customer)
        
        if not fd_accounts:
            # No FD accounts found for the customer
            context = {'message': 'No FD accounts created'}
            return render(request, 'Customer/FD.html', context)
        
        fd_with_details = []
        for fd in fd_accounts:
            # for maturity amount calculation
            interest_rate = Decimal(fd.interest_rate.interest_rate.strip('%')) / 100
            time_in_years = (fd.maturity_date - fd.start_date).days / 365
            maturity_amount =  fd.total_amount*(1 + interest_rate) ** Decimal(time_in_years)
            fd.maturity_amount = maturity_amount
            fd.save() 
            fd_with_details.append({
                'fd_account': fd.account_number,
                'interest_rate': fd.interest_rate.interest_rate,  # Assuming interest_rate is a foreign key
                'start_date': fd.start_date,
                'maturity_date': fd.maturity_date,
                'total_amount':fd.total_amount,
                'maturity_amount': maturity_amount
            })
            context = {
            'fd_accounts': fd_with_details
        }
        
        return render(request, 'Customer/FD.html', context)
    except Customer.DoesNotExist:
        return render(request, 'Customer/FD.html', {'error': 'Customer not found'})


   


def create_user_loan(request):
 
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            tenure = request.POST.get('tenure')
            amount = request.POST.get('amount')
            interest_rate = request.POST.get('interest_rate')

            try:
                customer = Customer.objects.get(member=user_id)
            except Customer.DoesNotExist:
                message = "Invalid Member ID!"
                return render(request, 'customer/create_loan.html', {'message': message})

            # If customer exists, create the loan
            loan = Personal_loan(
                user=customer,
                tenure=tenure,
                amount=amount,
                interest_rate=interest_rate,
            )
            loan.save()  # Save the loan to the database
            
            emi_amount = calculate_emi(amount, interest_rate, tenure)
        
            message = f"Loan created successfully! EMI Amount: {emi_amount:.2f}"
            return render(request, 'customer/create_loan.html', {'message': message})
            
            # message = "Loan created successfully!"
            # return render(request, 'customer/create_loan.html', {'message': message})

        except Exception as e:
            message = f"An error occurred: {str(e)}"
            return render(request, 'customer/create_loan.html', {'message': message})

    return render(request, 'customer/create_loan.html')



def calculate_emi(amount, interest_rate, tenure):
    """
    Function to calculate EMI.
    """
    

    # Convert the inputs to the correct numeric types
    amount = float(amount)
    interest_rate = float(interest_rate.replace('%', ''))
    tenure = int(tenure)

    r = (interest_rate / 12) / 100  # Monthly interest rate
    n = tenure  # Number of months

    # EMI calculation formula
    emi = (amount * r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return emi


def customer_funds(request):
  
    member_id = request.session.get('customer_id')
    member = get_object_or_404(Customer, member=member_id)
    customer_name = member.first_name 

    
    
    if request.method == 'POST':
        account_no = request.POST.get('account')
        amount =int(request.POST.get('amount'))
        member_id = request.session.get('customer_id')
   
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
            Transactions.objects.create(
                member_id=source_account.id,
                transaction_type='Transfer',
                amount=amount,
                description='Fund Transfer',
                account_no=destination_account,
               
            ) 
            
            
            # Record transaction for destination account
            # Transactions.objects.create(
            #         member_id=destination_account.id,
            #         transaction_type='Transfer',
            #         amount=amount,
            #         description='Fund Transfer from',
            #         account_no=source_account
            #     )
            
            
            TransferTransactions.objects.create(
                    from_account_no=source_account,
                    to_account_no=destination_account,
                    amount=-amount,
                    description='Fund Transfer',
                    remaining_balance=source_account.account_balance,
                   
                )
            
            
            
            TransferTransactions.objects.create(
                from_account_no=destination_account,
                to_account_no=source_account,
                amount=amount,  # Amount added to destination account
                description='Fund Transfer',
                remaining_balance=destination_account.account_balance,
               
            )
                
                
            
            source_account.save()
            destination_account.save()
            
        except SavingAccount.DoesNotExist:
            return render(request, 'Customer/Funds.html', {'error': 'Destination account not found.'})
        except Exception as e:
            return render(request, 'Customer/Funds.html', {'error': str(e)})
        
        # transactions = Transactions.objects.filter(member_id=member_id).order_by('-transfer_date')
        
        transactions = Transactions.objects.all()
        for transaction in transactions:
           print(transaction.transaction_type)

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
    member_id = request.session.get('customer_id')
    
    # Fetch the customer object based on the member ID
    customer = get_object_or_404(Customer, member=member_id)

    if request.method == "POST":
        # Updating personal details
        personal_details = {
            'first_name': request.POST.get("first-name"),
            'last_name': request.POST.get("last-name"),
            'father_name': request.POST.get("father_name"),
            'gender': request.POST.get("gender"),
            'dob': request.POST.get("dob"),
        }
        Customer.objects.filter(member=member_id).update(**personal_details)

        # Updating contact details
        contact_details = {
            'state': request.POST.get("state"),
            'city': request.POST.get("city"),
            'current_address': request.POST.get("current-add"),
            'post_office': request.POST.get("postal"),
            'email': request.POST.get("email"),
            'mobile': request.POST.get("mobile"),
        }
        Customer.objects.filter(member=member_id).update(**contact_details)

        # Updating bank details
        bank_details = {
            'branch_name': request.POST.get("bank-name"),
            'account_no': request.POST.get("account"),
            'branch_code': request.POST.get("branch"),
            'ifsc': request.POST.get("ifsc"),
            'status': request.POST.get("account-holder"),
        }
        SavingAccount.objects.filter(member=member_id).update(**bank_details)

        # Updating nominee details
        nominee_details = {
            'nominee_name': request.POST.get("nominee-name"),
            'nominee_relationship': request.POST.get("relation"),
            'nominee_dob': request.POST.get("nominee-dob"),
        }
        
        UserFamily.objects.filter(user_id=customer.user.id).update(**nominee_details)

        return redirect('profile')

    else:
        # Retrieve the customer profile and related data
        payment = get_object_or_404(SavingAccount, member=member_id)
        nominee = get_object_or_404(UserFamily, user=customer)

        return render(request, 'Customer/Profile.html', {
            'result': customer,
            'payment': payment,
            'nominee': nominee
        })





def customer_setting(request):
    # Fetching session data (if needed)
    customer_id = request.session.get('customer_id')
    
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            # Save the new password in the Django User model
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in

            # Optionally update the password in the Customer model
            if customer_id:
                try:
                    # Fetch the Customer record
                    customer = Customer.objects.get(id=customer_id)

                    # Get the new password from the form
                    new_password = form.cleaned_data['new_password1']
                    
                    

                    # Ensure the password is a string
                    if not isinstance(new_password, str):
                        raise TypeError("Password must be a string.")

                    # Hash the password
                    hashed_password = make_password(new_password)

                
                    # Update the password field with the hashed password
                    customer.password = hashed_password
                    customer.save()

                    
                except Customer.DoesNotExist:
                    messages.error(request, 'Customer profile not found.')
                except Exception as e:
                    messages.error(request, f'An error occurred: {e}')
    
            messages.success(request, 'Password successfully changed')
            return redirect('customer_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'Customer/Settings.html', {'form': form})


def interest_rate(request):
    id = request.GET.get('strUser')
    scheme = request.GET.get('scheme')
    rate = FD_scheme.objects.get(tenure=id, breakable=scheme)
    data = {'rate': rate.interest_rate}
    return JsonResponse(data)


    
def create_fd_account(self):
  
    if self.method == 'POST':
        try:
            member = self.POST.get('member_id')
            interest_rate_value = self.POST.get('interest_rate')
            start_date = self.POST.get('start_date')
            maturity_date = self.POST.get('maturity_date')
            total_amount = self.POST.get('total_amount')
            
            
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




def create_rd_account(self):
    
  
    if self.method == 'POST':
        try:
            member = self.POST.get('member_id')
            interest_rate_value = self.POST.get('interest_rate')
            start_date = self.POST.get('start_date')
            maturity_date = self.POST.get('maturity_date')
            total_amount = self.POST.get('total_amount')
            
            
            try:
                customer = Customer.objects.get(member=member)
            except Customer.DoesNotExist:
                message = "Invalid Member ID!"
                interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
                return render(self, 'admin/create_rd.html', {'message': message, 'interest_rates': interest_rates})
            interest_rate_qs = RD_scheme.objects.filter(interest_rate=interest_rate_value)
            if not interest_rate_qs.exists():
                message = "Invalid interest rate!"
                interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
                return render(self, 'admin/create_rd.html', {'message': message, 'interest_rates': interest_rates})
            interest_rate_obj = interest_rate_qs.first()
            account_number = "RD" + str(random.randint(1111111111, 9999999999))
                
            RD_account = RecurringDeposit(
                account_number=account_number,
                customer=customer,
                interest_rate=interest_rate_obj,
                total_amount=total_amount,
                status='Active',  # Default status
                start_date=start_date,
                maturity_date=maturity_date,
                )
            RD_account.save()
        
            
            message = "RD created successfully!"
            interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
            return render(self, 'customer/create_rd.html', {'message': message, 'interest_rates': interest_rates})
        except Exception as e:
            message = f"An error occurred: {e}"
            interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
            return render(self, 'customer/create_rd.html', {'message': message, 'interest_rates': interest_rates})
            
    else:
        interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
        return render(self, 'customer/create_rd.html', {'interest_rates': interest_rates})



def send_email_view(request):
    subject = "Test Subject"
    message = "This is a test email."
    recipient_list = ["priyalsinghal11@gmail.com"]
    # Call the Celery task
    send_email_task(subject, message, recipient_list)
    return HttpResponse("Email sent!")