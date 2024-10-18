import csv
from django.contrib.auth.forms import PasswordChangeForm
import random
from django.contrib.auth.hashers import make_password
from django.forms import forms
from django.shortcuts import render, redirect
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
from django.urls import reverse
from django.db.models import Sum
import json



class Dashboard():
    def index(self):
        return render(self, 'Customer/login.html')




def Customer_Login(request):    
    if request.method == 'POST':
        data = json.loads(request.body)
        enter_email = data["username"]
        enter_password = data["pass"]
        try:
            customer = Customer.objects.get(email=enter_email, password=enter_password)
            if customer.is_verify == 0:  # 0 means verified
                request.session['customer_name'] = customer.first_name
                request.session['customer_id'] = customer.member
                saving_account = SavingAccount.objects.filter(member=customer.member).first()
                # Fetch SavingAccount object for the logged-in customer
                try:
                    saving_account = SavingAccount.objects.get(member=customer.member)
                    request.session['account_no'] = saving_account.account_no
                    request.session['branch_name'] = saving_account.branch_name
                    request.session['branch_code'] = saving_account.branch_code
                    request.session['ifsc'] = saving_account.ifsc
                    request.session['account_balance'] = str(saving_account.account_balance)  # Convert Decimal to string
                except SavingAccount.DoesNotExist:
                    request.session['account_no'] = None
                    request.session['branch_name'] = None
                    request.session['branch_code'] = None
                    request.session['ifsc']=None
                    request.session['account_balance']='None'
                context = {
                    'customer_id': customer.member, 
                    'customer_name': customer.first_name,
                    'account':saving_account.account_no,
                       }

                return  JsonResponse({"account_no":saving_account.account_no})
    
            else:
                return JsonResponse({"success": False, "message": "Account not verified by admin"})

        except Customer.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid credentials"})

    else:
        return render(request, 'Customer/login.html' )





def customer_account(request, account_no):
    account_no=request.session.get('account_no')
    member_id = request.session.get('customer_id')
    member = get_object_or_404(Customer, member=member_id)
    customer_name = member.first_name 
    try:
        saving_account = SavingAccount.objects.get(member=member_id, account_no=account_no)
        current_balance = Decimal(saving_account.account_balance)
    except SavingAccount.DoesNotExist:
        saving_account = None
        current_balance = Decimal(0)

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
            end_date = datetime.combine(end_date, dt_time.max)
            transfer_transactions = transfer_transactions.filter(transfer_date__range=(start_date, end_date))

    balances = []
    running_balance = current_balance
    for transfer in transfer_transactions:
        if transfer.from_account_no.account_no == account_no:
            running_balance = Decimal(transfer.remaining_balance)
            balances.append(running_balance)
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



#Accounts Statement download transaction
def download_transactions(request):
    member_id = request.session.get('customer_id')
    member = get_object_or_404(Customer, member=member_id)

    try:
        saving_account = SavingAccount.objects.get(member=member_id)
    except SavingAccount.DoesNotExist:
        saving_account = None

    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None
    
    if end_date:
        end_date = end_date + timedelta(days=1)
    
    transactions = TransferTransactions.objects.filter(from_account_no=saving_account)
    
    if start_date and end_date:
        transactions = transactions.filter(transfer_date__range=[start_date, end_date])
    elif start_date:
        transactions = transactions.filter(transfer_date__gte=start_date)
    elif end_date:
        transactions = transactions.filter(transfer_date__lte=end_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Transaction ID', 'Beneficiary', 'Amount', 'Balance After Transaction', 'Date', 'Type'])

    for transaction in transactions: 
        writer.writerow([
            transaction.transfer_id,
            transaction.to_account_no.account_no if transaction.to_account_no else '',
            transaction.amount,
            transaction.remaining_balance, 
            transaction.transfer_date,
            transaction.description,
        ])

    return response





def customer_logout(request):
        del request.session['customer_name']
        del request.session['customer_id']
        return render(request, 'Customer/login.html')




def customer_bill(self):
    return render(self,'Customer/Bill.html')



# def create_fd_view(request):
#     return render(request, 'Customer/create_fd.html')



def customer_fd(request):
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    fd_accounts = FixedDeposit.objects.filter(customer=customer)

    if not fd_accounts.exists():
        return render(request, 'Customer/fd_Home.html')

    fd_with_details = []
    for fd in fd_accounts:
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
    if any(fd.status == 'Active' for fd in fd_accounts):
        return render(request, 'Customer/FD.html', {'fd_accounts': fd_with_details})

    return render(request, 'Customer/fd_Home.html')


    


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




def withdraw_fd(request, fd_id):
    fd = get_object_or_404(FixedDeposit, pk=fd_id)
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    saving_account = SavingAccount.objects.filter(member=member_id).first()
   
    if saving_account is None:
        return render(request, 'Customer/FD.html', {'error': 'No saving account found for the customer.'})
   
    if fd.status != 'Active':
        return render(request, 'Customer/FD.html', {'error': 'FD status is not active.'})

    balance = Decimal(saving_account.account_balance) 
    balance += fd.maturity_amount
    saving_account.account_balance = str(balance)
    saving_account.save() 

    fd.status = 'Matured'
    fd.save()
    
    
    TransferTransactions.objects.create(
                from_account_no=saving_account,
                to_account_no=None, 
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
    


def fd_home(request): 
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    fd_accounts = FixedDeposit.objects.filter(customer=customer)
    if not fd_accounts.exists():
        return render(request, 'Customer/fd_Home.html')
    fd_with_details = []    
    for fd in fd_accounts:
        if fd.is_active == 1: 
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
        else:
            fd_with_details.append({
                'fd_account': fd,
                'status_message': 'Not active FD by admin',
            })
            
    context = {
        'fd_accounts': fd_with_details
        }
       
    fd_status = fd_accounts.values_list('status', flat=True).distinct()
    
    if 'Matured' in fd_status:
        return render(request, 'Customer/fd_matured.html', {'fd_accounts': fd_accounts})
    elif 'Active' in fd_status:
        context = {'fd_accounts': fd_accounts}
        return render(request, 'Customer/FD.html', context)
    else:
        return render(request, 'Customer/fd_Home.html')





def rd_home(request):
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    rd_accounts = RecurringDeposit.objects.filter(customer=customer)
    rd_with_next_payment = []
    start_date = None
    end_date = None
    filtered_payments = None
    page_obj = None 
    total_amount_paid = 0  

    for rd in rd_accounts:
        if rd.is_active == 1: 
            last_payment = PaymentSchedule.objects.filter(
                rd_account=rd,
                status='pending'
            ).first()

            completed_payments = PaymentSchedule.objects.filter(
                rd_account=rd,
                status='completed'
            )
            total_paid_for_rd = completed_payments.aggregate(total_paid=Sum('amount'))['total_paid'] or 0
            total_amount_paid += total_paid_for_rd 

            
            if last_payment:
                next_payment_date = last_payment.payment_date 
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
                    'maturity_amount': maturity_amount,
                    'total_paid_for_rd': total_paid_for_rd
                })
                
                start_date = request.GET.get('startDate')
                end_date = request.GET.get('endDate')
                if start_date and end_date:
                    start_date = parse_date(start_date)
                    end_date = parse_date(end_date)

                if start_date and end_date:
                    end_date = datetime.combine(end_date, dt_time.max)
                    filtered_payments = PaymentSchedule.objects.filter(rd_account__in=rd_accounts, payment_date__range=(start_date, end_date))
                
            paginator = Paginator(rd_with_next_payment, 10)  # Show 10 items per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
                    
        else:
            # RD not active
            rd_with_next_payment.append({
                'rd_account': rd,
                'status_message': 'RD is not active by admin',
            })
                
    context = {
        'rd_with_next_payment': rd_with_next_payment,
        'filtered_payments': filtered_payments,  
        'start_date': start_date or '',  
        'end_date': end_date or '',  
        'page_obj': page_obj,
        'total_amount_paid': total_amount_paid 
    }
    
    rd_status = rd_accounts.values_list('status', flat=True).distinct()
    
    if 'Matured' in rd_status:
        return render(request, 'Customer/rd_matured.html', {'rd_accounts': rd_accounts})
    elif 'Active' in rd_status:
        return render(request, 'Customer/RD.html', context)
    else:
        return render(request, 'Customer/rd_Home.html')




# RD Downlaod statement 
def rd_download_payment(request):
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    rd_accounts = RecurringDeposit.objects.filter(customer=customer)
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    # Convert start_date and end_date to datetime objects
    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None
    
    if end_date:
        end_date = end_date + timedelta(days=1)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payment.csv"'

    writer = csv.writer(response)
    writer.writerow([	'Payment Date',	'Amount',	'Status'])
    
    for rd in rd_accounts:
        payments = PaymentSchedule.objects.filter(
            rd_account=rd,
            payment_date__gte=start_date if start_date else None,
            payment_date__lte=end_date if end_date else None
            )
        for payment in payments:
            writer.writerow([
                payment.payment_date,
                payment.amount,
                payment.status,
            ])
    return response

 


def create_rd_account(self):
    if self.method == 'POST':
        try:
            member = self.POST.get('member_id')
            interest_rate_value = self.POST.get('interest_rate')
            start_date = self.POST.get('start_date')
            maturity_date = self.POST.get('maturity_date')
            monthly_installment=self.POST.get('monthly_installment')
      
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
                monthly_installment=monthly_installment,
                status='Active',  
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

   
    

def mark_next_payment_completed(request, rd_id):
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    saving_account = SavingAccount.objects.filter(member=member_id).first()
   
    rd_account = get_object_or_404(RecurringDeposit, id=rd_id, customer=customer)
    
    balance = Decimal(saving_account.account_balance) 
    balance -= rd_account.monthly_installment
    saving_account.account_balance = str(balance)
    saving_account.save()
    
    
    next_payment = PaymentSchedule.objects.filter(
            rd_account=rd_account,
            status='Pending' 
        ).order_by('payment_date').first()

    if next_payment:
            next_payment.status = 'Completed'
            next_payment.save()

            TransferTransactions.objects.create(
                amount=Decimal(rd_account.monthly_installment),
                transfer_date=datetime.now().date(),
                description="RD Payment",
                from_account_no=saving_account,
                to_account_no=None, 
                remaining_balance=saving_account.account_balance,
            )

            # Create a general transaction record
            Transactions.objects.create(
                transaction_type='Transfer',
                amount=Decimal(rd_account.monthly_installment),
                description="RD Payment",
                account_no=saving_account,
                member_id=customer.id,
            )

    return redirect('rd_home') 



def calculate_rd_maturity_amount(rd):
    # P: Monthly installment
    P = Decimal(rd.monthly_installment)
 
    annual_rate_str = rd.interest_rate.interest_rate.strip().replace('%', '')
    annual_rate = Decimal(annual_rate_str)
    
    r = annual_rate / Decimal('1200')  # 12 * 100
  
    start_date = rd.start_date
    maturity_date = rd.maturity_date
    n = ((maturity_date.year - start_date.year) * 12) + (maturity_date.month - start_date.month)
   
    maturity_amount = P * (((1 + r)**n - 1) / r) * (1 + r)
    
    return round(maturity_amount, 2)




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
            else:
                next_payment_date = rd.start_date + timedelta(days=30)
            
           
            maturity_amount = calculate_rd_maturity_amount(rd)
            rd.maturity_amount = maturity_amount
            rd.save()
            
            
            rd_with_next_payment.append({
                'rd_account': rd,
                'next_payment_date': next_payment_date,
                # 'current_payments': current_payments,
                'interest_rate': rd.interest_rate.interest_rate,
                'maturity_amount': maturity_amount
            })
                   
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




def calculate_amortization_schedule(amount, annual_rate, tenure_months, start_date):
    monthly_rate = Decimal(annual_rate) / Decimal(12 * 100)  # Convert annual rate to monthly rate
    tenure_months = Decimal(tenure_months)
    
    if monthly_rate == 0:
        monthly_payment = amount / tenure_months
    else:
        numerator = monthly_rate * (Decimal(1) + monthly_rate) ** tenure_months
        denominator = (Decimal(1) + monthly_rate) ** tenure_months - 1
        monthly_payment = amount * numerator / denominator
    
    schedule = []
    balance = Decimal(amount)
    current_date = start_date

    for month in range(1, int(tenure_months) + 1):
        interest = balance * monthly_rate
        principal = monthly_payment - interest
        balance -= principal
        
        due_date = current_date
        current_date += timedelta(days=30)  # Increment date by 30 days

        schedule.append({
            'payment_date': due_date.strftime('%Y-%m-%d'),  # Format date to YYYY-MM-DD
            'principal': round(principal, 2),
            'interest': round(interest, 2),
            'total_payment': round(monthly_payment, 2),
            'balance': round(balance, 2) if balance > 0 else 0,
        })

    return schedule




def customer_loan(request):
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    
    personal_loans = list(Personal_loan.objects.filter(user=customer)) 

    personal_loan_data = []
    start_date = datetime.now().date()
    
    for loan in personal_loans:
        if loan.is_active == 1:
            try:
                loan_amount = Decimal(loan.amount)
                loan_tenure = int(loan.tenure)
                annual_rate = Decimal(loan.interest_rate.replace('%', '').strip())  
                loan.schedule = calculate_amortization_schedule(loan_amount, annual_rate, loan_tenure, start_date)
                
                total_completed_payment = Decimal(0) 

                for entry in loan.schedule:
                    payment_date = entry['payment_date']  # Use due_date for payment_date
                    
                    emi_record, created = LOANEMIPayment.objects.get_or_create(
                        user=customer,
                        loan=loan,
                        payment_date=payment_date,  # Ensure payment_date is provided
                        defaults={
                            'principal': entry['principal'],
                            'interest': entry['interest'],
                            'total_payment': entry['total_payment'],
                            'balance': entry['balance'],
                            'status': 'pending',  # Default status as 'pending'
                        }
                    )
                    
                    # Fetch status and update total_payment
                    emi_record = LOANEMIPayment.objects.filter(
                        user=customer, 
                        loan=loan, 
                        payment_date=payment_date  # Match by payment_date
                    ).first()
                    
                    if emi_record:
                        entry['status'] = emi_record.status  # Fetch status from the database

                        # Add total payment for completed payments
                        if emi_record.status == 'Completed':
                            total_completed_payment += emi_record.total_payment
                            
                        loan.total_completed_payment = total_completed_payment
                        loan.total_payment = LOANEMIPayment.objects.filter(user=customer, loan=loan, status='pending').first()
                        loan.payment_date = LOANEMIPayment.objects.filter(user=customer, loan=loan, status='pending').first()
                
                # Append the loan details with its schedule to the display list
                personal_loan_data.append(loan)
            
            except InvalidOperation:
                loan.schedule = []
        
        else:
            personal_loan_data.append({
                'status_message': 'Loan is not activate by admin',
                'loan': loan
            })
    
    context = {
        'customer': customer,
        'personal_loans': personal_loan_data  # Use the modified list with loan data and status messages
    }
    return render(request, 'Customer/Loan.html', context)





def loan_emipay(request, loan_id):
    # Fetch member ID from session
    member_id = request.session.get('customer_id')
    # Get customer and saving account
    customer = get_object_or_404(Customer, member=member_id)
    
    saving_account = SavingAccount.objects.filter(member=member_id).first()
   
    loan_account = get_object_or_404(Personal_loan, id=loan_id, user=customer)
    loan_queryset = LOANEMIPayment.objects.filter(user=customer)

    next_payment = loan_queryset.filter(status='Pending').order_by('payment_date').first()

    if next_payment:
        print("Total Payment:", next_payment.total_payment)

  
    balance = Decimal(saving_account.account_balance) 
    balance -= next_payment.total_payment
    saving_account.account_balance = str(balance)
    saving_account.save()

    next_payment = LOANEMIPayment.objects.filter(
            loan=loan_account.id,
            status='Pending'  # Assuming 'Pending' is the status for unpaid payments
        ).order_by('payment_date').first()

    if next_payment:
            # Mark as completed
            next_payment.status = 'Completed'
            next_payment.save()

            # Create transfer transaction record
            TransferTransactions.objects.create(
                amount=Decimal(next_payment.total_payment),
                transfer_date=datetime.now().date(),
                description="EMI LOAN",
                from_account_no=saving_account,
                to_account_no=None,  # Add actual value if needed
                remaining_balance=saving_account.account_balance,
            )

            # Create a general transaction record
            Transactions.objects.create(
                transaction_type='Transfer',
                amount=Decimal(next_payment.total_payment),
                description="EMI LOAN",
                account_no=saving_account,
                member_id=customer.id,
            )

    return redirect('loan') 




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
            
            
        except Exception as e:
            message = f"An error occurred: {str(e)}"
            return render(request, 'customer/create_loan.html', {'message': message})

    return render(request, 'customer/create_loan.html')





def calculate_emi(amount, interest_rate, tenure):
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
            source_account = SavingAccount.objects.get(member=member_id)
            destination_account = SavingAccount.objects.get(account_no=account_no)
            if(source_account.account_balance>=amount):
                source_account.account_balance-=amount
                destination_account.account_balance+=amount
            else:   
                raise Exception("not sufficient balance to transfer")
            Transactions.objects.create(
                member_id=source_account.id,
                transaction_type='Transfer',
                amount=amount,
                description='Fund Transfer',
                account_no=destination_account,
               
            ) 
    
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
                amount=amount,  
                description='Fund Transfer',
                remaining_balance=destination_account.account_balance,
               
            )
         
            source_account.save()
            destination_account.save()
            
        except SavingAccount.DoesNotExist:
            return render(request, 'Customer/Funds.html', {'error': 'Destination account not found.'})
        except Exception as e:
            return render(request, 'Customer/Funds.html', {'error': str(e)})
       
        transactions = Transactions.objects.all()
        for transaction in transactions:
           print(transaction.transaction_type)

    return render(request, 'Customer/Funds.html', { 'customer_name': customer_name})








def customer_home(request, account_no):
    member_id = request.session.get('customer_id')
    account_no= request.session.get('account_no')
 
    member = get_object_or_404(Customer, member=member_id)
    customer_name = member.first_name 
    user_name=request.session['customer_name']
    member_id=request.session['customer_id']

    total_rd_paid = 0  
    total_completed_loan_payments = Decimal(0)
    
    
    if user_name and member_id:
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
    rd_accounts = RecurringDeposit.objects.filter(customer=member)

    # Calculate total amount paid for all RD accounts
    for rd in rd_accounts:
        completed_payments = PaymentSchedule.objects.filter(
            rd_account=rd,
            status='completed'
        )
        total_paid_for_rd = completed_payments.aggregate(total_paid=Sum('amount'))['total_paid'] or 0
        total_rd_paid += total_paid_for_rd  # Add to the total amount paid

    loans = Personal_loan.objects.filter(user=member)
   
        # Calculate total completed loan payments
    for loan in loans:

        completed_payments = LOANEMIPayment.objects.filter(
            loan=loan,
            status='Completed'
        )
        
        
        total_completed_loan_payments += completed_payments.aggregate(total_paid=Sum('total_payment'))['total_paid'] or 0

    # Fetch FD accounts related to the customer
    fd_accounts = FixedDeposit.objects.filter(customer=member)
    fd_details = []
   
    for fd in fd_accounts:

        fd_details.append({
            'total_amount': fd.total_amount,
        })
    form = BankStatementForm()
    
    context = {
        'page_obj': page_obj,
        'saving_account': saving_account,
        'form': form,
        'start_date': request.GET.get('startDate', ''),
        'end_date': request.GET.get('endDate', ''),
        'customer_name': customer_name,
        'current_balance':current_balance,
        'fd_details': fd_details,
        'total_rd_paid': total_rd_paid,
        'total_completed_loan_payments': total_completed_loan_payments,
      
    }

    return render(request,'Customer/Home.html', context)
   



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
            'status': request.POST.get("account-holder", 'success'),  
            
        }
        SavingAccount.objects.filter(member=member_id).update(**bank_details)

        # Updating nominee details
        nominee_details = {
            'nominee_name': request.POST.get("nominee-name"),
            'nominee_relationship': request.POST.get("relation"),
            'nominee_dob': request.POST.get("nominee-dob"),
        }
        
 
        UserFamily.objects.filter(user_id=customer.id).update(**nominee_details)

        return redirect('profile')

    else:
        payment = get_object_or_404(SavingAccount, member=member_id)
        nominee = get_object_or_404(UserFamily, user=customer)

        return render(request, 'Customer/Profile.html', {
            'result': customer,
            'payment': payment,
            'nominee': nominee
        })



def customer_edit(request):
    member_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, member=member_id)
    if request.method == "POST":
        customer.first_name = request.POST.get("name")
        customer.last_name = request.POST.get("lname")
        customer.father_name = request.POST.get("fname")
        customer.gender = request.POST.get("gender")
        customer.dob = request.POST.get("dob")        
        customer.save()
        return redirect('profile')
    edit_mode = request.GET.get('edit_mode', 'false') == 'true'
    return render(request, 'customer/profile.html', {'customer': customer, 'edit_mode': edit_mode})


def customer_setting(request):
    customer_id = request.session.get('customer_id') 
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  

            if customer_id:
                try:
                    customer = Customer.objects.get(id=customer_id)
                    new_password = form.cleaned_data['new_password1']
            
                   
                    if not isinstance(new_password, str):
                        raise TypeError("Password must be a string.")

                    
                    hashed_password = make_password(new_password)
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



# def send_email_view(request):
#     subject = "Test Subject"
#     message = "This is a test email."
#     recipient_list = ["priyalsinghal11@gmail.com"]
#     # Call the Celery task
#     send_email_task(subject, message, recipient_list)
#     return HttpResponse("Email sent!")