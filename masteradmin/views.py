import random
from django.contrib import messages
from django.shortcuts import render
from masteradmin.models import * 
from django.http import JsonResponse
from django.utils import timezone    
from datetime import timedelta   
from django.shortcuts import render, get_object_or_404 
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import datetime
     
     
     
     
 

class Dashboard:
    def index(self):
        if self.session['user_name']:
            cust = Customer.objects.count()
            fd = FixedDeposit.objects.count()
            rd = RecurringDeposit.objects.count()
            loan=Personal_loan.objects.count()
            try:
                customer = Customer.objects.filter(is_active=0).all().order_by('-id')
            except:
                customer = None
            return render(self, 'admin/index.html', {'cust': cust, 'fd': fd, 'rd': rd, 'loan':loan, 'customer': customer })
        else:
            return render(self, 'admin/login.html')
        
        
    def fd_plan(self):
        if self.method == 'POST':
            fd = FD_scheme(
                scheme=self.POST.get('scheme'),
                interest_rate=self.POST.get('interest_rate'),
                tenure =self.POST.get('tenure'),
                breakable = self.POST.get('breakable'),
                is_applicable = 1,
                created_date = models.DateTimeField(auto_now_add=True),
            )
            fd.save()
            message = "Scheme Created Successfully !"
            return render(self, 'admin/fd_plans.html', {'message': message})
        else:
            return render(self, 'admin/fd_plans.html')


        
        
        
        
    def rd_plan(self):
        if self.method == 'POST':
            rd = RD_scheme(
                scheme=self.POST.get('scheme'),
                interest_rate=self.POST.get('interest_rate'),
                tenure=self.POST.get('tenure'),
                breakable=self.POST.get('breakable'),
                is_applicable=1,
                created_date=models.DateTimeField(auto_now_add=True),
            )
            rd.save()
            messages.success(self, "Scheme Created Successfully !")
            return render(self, 'admin/rd_plans.html')
        else:
            return render(self, 'admin/rd_plans.html')

    def login(self):
        if self.method == 'POST':
            try:
                email = self.POST.get('email')
                password = self.POST.get('password')
                result = Admin.objects.get(email=email, password=password, is_active=1)
                self.session['user_name'] = result.admin_name
                self.session['user_id'] = result.id
                self.session['user_role'] = result.role
                cust = Customer.objects.count()
                fd = FixedDeposit.objects.count()
                rd = RecurringDeposit.objects.count()
                try:
                    customer = Customer.objects.filter(is_active=0).all().order_by('-id')
                except:
                    customer = None
                return render(self, 'admin/index.html', {'cust': cust, 'fd': fd, 'rd': rd, 'customer': customer, 'result': result})
            except Exception:
                message = "Email Id & Password is invalid !"
                return render(self, 'admin/login.html', {'message': message})
        else:
            return render(self, 'admin/login.html')

    def member_form(self):
        if self.method == 'POST':
            try:
                member = self.POST.get('member')
                email = self.POST.get('email')
                
                Admin.objects.get(admin_name=member, email=email)
                message = "Member Already Created !"
                return render(self, 'admin/add_member.html', {'message': message})
            except Exception:
                admin = Admin(
                    role=self.POST.get('role'),
                    admin_name=self.POST.get('member'),
                    position=self.POST.get('designation'),
                    email=self.POST.get('email'),
                    password=self.POST.get('password'),
                    contact=self.POST.get('contact'),
                    address=self.POST.get('address'),
                    description=self.POST.get('description'),
                    facebook=self.POST.get('facebook'),
                    twitter=self.POST.get('twitter'),
                    linkedin=self.POST.get('linkedin'),
                    is_active=1,
                    created_date=models.DateTimeField(auto_now_add=True),
                )
                admin.save()
                message = "Member Created Successfully !"
                return render(self, 'admin/add_member.html', {'message': message})
        else:
            return render(self, 'admin/add_member.html')

    def members(self):
        if self.method == 'POST':
            try:
                render(self, 'admin/add_member.html')
            except Exception:
                return render(self, 'admin/add_member.html')
        else:
            admin = Admin.objects.all()
            return render(self, 'admin/member.html', {'admin': admin})

    def customers(self):
        customer_data = Customer.objects.all().order_by('-id')
        return render(self, 'admin/customer.html', {'customer': customer_data})

    def view_customers(self, member):
        try:
            customer_data = Customer.objects.get(member=member)
        except:
            customer_data = None

        try:
            customer_payment = UserPayment.objects.get(user=customer_data.id)
        except:
            customer_payment = None

        try:
            nominee = UserFamily.objects.get(user=customer_data.id)
        except:
            nominee = None

        try:
            document = UserDocument.objects.get(user=customer_data.id)
        except:
            document = None

        try:
            other = UserOther.objects.get(user=customer_data.id)
        except:
            other = None

        context = {'customer': customer_data, 'payment': customer_payment, 'nominee': nominee, 'document': document, 'other': other}
        return render(self, 'admin/customer_details.html', context)

    def verify_cust(self, verify, member):
        if verify == 0:
            Customer.objects.filter(member=member).update(is_verify=1)
        else:
            Customer.objects.filter(member=member).update(is_verify=0)
        customer_data = Customer.objects.all().order_by('-id')
        return render(self, 'admin/customer.html', {'customer': customer_data})

    def active_cust(self, active, member):
        if active==0:
            Customer.objects.filter(member=member).update(is_active=1)
        else:
            Customer.objects.filter(member=member).update(is_active=0)
        customer_data = Customer.objects.all().order_by('-id')
        return render(self, 'admin/customer.html', {'customer': customer_data})

    def sactive(self, active, member):
        if active == 0:
            SavingAccount.objects.filter(member=member).update(is_active=1)
        else:
            SavingAccount.objects.filter(member=member).update(is_active=0)
        member = SavingAccount.objects.all().order_by('-id')
        return render(self, 'admin/saving_account.html', {'member': member})

    def create_saving_account(self):
        if self.method == 'POST':
            try:
                member = self.POST.get('member_id')
                account = random.randint(1111111111, 9999999999)
                SavingAccount.objects.exclude(member=member)
                saving_account = SavingAccount(
                    member=member,
                    account_no="SA"+str(account),
                    ifsc="HBFN900000009",
                    branch_code=self.POST.get('branch_code'),
                    branch_name=self.POST.get('branch_name'),
                    account_balance=self.POST.get('balance'),
                    status="success",
                    is_active=1,
                    created_date=models.DateTimeField(auto_now_add=True),
                )
                saving_account.save()
                trans = random.randint(1111111111, 9999999999)
                credit = CreditTransaction(
                    member=self.POST.get('member_id'),
                    transaction=trans,
                    amount=self.POST.get('balance'),
                    type_of_transaction="cash",
                    sender_account_no="SA9000000000",
                    sender_bank_name="HBFNIDHI",
                    debit_type="NO",
                    created_date=models.DateTimeField(auto_now_add=True),
                    status=1,
                )
                credit.save()
                message = "Saving account created successfully !"
                return render(self, 'admin/create_saving.html', {'message': message})
            except:
                message = "Invalid Member Id !"
                return render(self, 'admin/create_saving.html', {'message': message})
        else:
            return render(self, 'admin/create_saving.html')

    def account_transfer(self):
        if self.method == 'POST':
            sender_account = self.POST.get('sender_account')
            receiver_account = self.POST.get('receiver_account')
            try:
                debit_data = SavingAccount.objects.get(account_no=receiver_account)
                credit_data = SavingAccount.objects.get(account_no=sender_account)
                if int(credit_data.account_balance) > int(self.POST.get('amount')):
                    bal_remain = int(credit_data.account_balance)-int(self.POST.get('amount'))
                else:
                    message = "You have insufficient balance !"
                    return render(self, 'admin/account_transfer.html', {'message': message})
                try:
                    transaction = CreditTransaction.objects.last()
                    trans = int(transaction.transaction) + 1
                except:
                    trans = 1200090990
                credit = CreditTransaction(
                    member=debit_data.member,
                    transaction=trans,
                    amount=self.POST.get('amount'),
                    type_of_transaction=self.POST.get('transaction_type'),
                    sender_account_no=sender_account,
                    sender_bank_name="HBFNIDHI",
                    remark=self.POST.get('remark'),
                    debit_type="NO",
                    created_date=models.DateTimeField(auto_now_add=True),
                    status=1,
                )
                credit.save()
                try:
                    Beneficiary.objects.get(associated_member=debit_data.member, account_no=sender_account)
                except:
                    beneficiary = Beneficiary(
                        associated_member=debit_data.member,
                        account_no=sender_account,
                        ifsc="HBFN900000009",
                        branch_code="HBFN67346450",
                        bank_name="HBFNIDHI",
                        contact_no="9090009090",
                        type_of_account="saving",
                        remark=self.POST.get('remark'),
                        created_date=models.DateTimeField(auto_now_add=True),
                    )
                    beneficiary.save()
                try:
                    transaction = CreditTransaction.objects.last()
                    trans1 = int(transaction.transaction) + 1
                except:
                    trans1 = 9200090990
                debit = DebitTransaction(
                    member=credit_data.member,
                    transaction=trans1,
                    beneficiary=1,
                    amount=self.POST.get('amount'),
                    transaction_charge="no",
                    bal_before_transaction=credit_data.account_balance,
                    bal_after_transaction=bal_remain,
                    type_of_transaction=self.POST.get('transaction_type'),
                    debit_type="Other",
                    remark=self.POST.get('remarks'),
                    created_date=models.DateTimeField(auto_now_add=True),
                    status=1,
                )
                debit.save()
                SavingAccount.objects.filter(member=credit_data.member).update(account_balance=bal_remain)
                return render(self, 'admin/account_transfer.html', {'message': "Money Transferred Successfully!"})
            except:
                return render(self, 'admin/account_transfer.html', {'message': "Invalid Member Id !"})
        else:
            return render(self, 'admin/account_transfer.html')

    def saving_account(self):
        member = SavingAccount.objects.all().order_by('-id')
        return render(self, 'admin/saving_account.html', {'member': member})
            
   
   

    def next_payment_date(request, rd_account):
        rd_account = RecurringDeposit.objects.get(id=rd_account)
    
        last_payment = PaymentSchedule.objects.filter(
        rd_account=rd_account,
        status='Completed'
    ).order_by('-payment_date').first()
       
        if last_payment:
            next_payment_date = last_payment.payment_date + timedelta(days=30)  # Assuming monthly payments
        else:
            next_payment_date = rd_account.start_date + timedelta(days=30)
       
        next_payment = PaymentSchedule.objects.filter(
            rd_account=rd_account,
            payment_date=next_payment_date,
            status='Pending'
            )
        
        if not next_payment.exists():
            print(f"No PaymentSchedule found for rd_account: {rd_account} on date: {next_payment_date} with status: 'Pending'")
        else:
            print(f"Next Payment: {next_payment}")
               
        context = {
        'payment': next_payment,
        'next_payment_date': next_payment_date
    }
        
        return render(request, 'admin/payment_schedule.html', context)
        
    
    def saving_account_transaction(self):
        return render(self, 'admin/transaction.html')

    def show_account_transaction(self):
        return render(self, 'admin/saving_transaction.html')
    
         
    def loan(self):
        loans = Personal_loan.objects.all().prefetch_related('loanemipayment_set')
        return render(self, 'admin/loans.html', {'loans': loans})
        
   
    def edit_loan(request,account):
        loan_data = get_object_or_404(Personal_loan, user__member=account)
        user = loan_data.user
        loan_accounts = Personal_loan.objects.filter(user=user)
        return render(request,'admin/edit_loan.html/',{'loan_accounts': loan_accounts})

    def logout(self):
        del self.session['user_id']
        del self.session['user_name']
        return render(self, 'admin/login.html')


    
    def create_rd_account(self):           
        if self.method == 'POST':
            try: 
                
                member = self.POST.get('member_id')
                # memberid = Customer.objects.get(member=member)
                monthly_installment = self.POST.get('monthly_installment')
                interest_rate_value = self.POST.get('interest_rate')
                start_date = self.POST.get('start_date')
                maturity_date = self.POST.get('maturity_date')
            
                try:
                    customer = Customer.objects.get(member=member)
                except Customer.DoesNotExist:
                    message = "Invalid Member ID!"
                    interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
                    return render(self, 'admin/create_Rd.html', {'message': message, 'interest_rates': interest_rates})
                
                interest_rate_qs = RD_scheme.objects.filter(interest_rate=interest_rate_value)
                if not interest_rate_qs.exists():
                    message = "Invalid interest rate!"
                    interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
                    return render(self, 'admin/create_rd.html', {'message': message, 'interest_rates': interest_rates})
                interest_rate_obj = interest_rate_qs.first()
                
                account_number = "RD" + str(random.randint(1111111111, 9999999999))

            # Calculate initial total amount, if required
                total_amount = 0.0
                
                RD_account = RecurringDeposit(
                    account_number=account_number,
                    customer=customer,
                    interest_rate=interest_rate_obj,
                    total_amount=total_amount,
                    status='Active',  # Default status
                    start_date=start_date,
                    maturity_date=maturity_date,
                    monthly_installment=monthly_installment,
                    )
                RD_account.save()
                
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                maturity_date_obj = datetime.strptime(maturity_date, '%Y-%m-%d').date()
            
            # Calculate tenure in months
                tenure_months = (maturity_date_obj.year - start_date_obj.year) * 12 + (maturity_date_obj.month - start_date_obj.month)
            
                
           
                
                current_payment_date = start_date_obj
                # Generate payment schedule
                for i in range(tenure_months):
                    
                    PaymentSchedule.objects.create(
                    rd_account=RD_account,
                    payment_date=current_payment_date,
                    amount=monthly_installment,
                    status='Pending'  
                )
                    
                    current_payment_date = current_payment_date + relativedelta(months=1)
                
            
                message = "RD created successfully!"
                interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
                return render(self, 'admin/create_rd.html', {'message': message,'interest_rates': interest_rates})
            
            except Exception as e:
                message = f"An error occurred: {e}"
                interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
                return render(self, 'admin/create_rd.html', {'message': message, 'interest_rates': interest_rates})
        else:
            interest_rates = RD_scheme.objects.values_list('interest_rate', flat=True)
            return render(self, 'admin/create_rd.html',  {'interest_rates': interest_rates})
        


    def rd_account(self):
        rd_data = RecurringDeposit.objects.all()
        for obj in rd_data: 
            return render(self, 'admin/rd_account.html', {'rd_data': rd_data})
        
  
   
    def edit_rd(request,account):
        rd_data = get_object_or_404(RecurringDeposit, account_number=account)
        customer = rd_data.customer
        rd_accounts = RecurringDeposit.objects.filter(customer=customer, account_number=account)
        return render(request, 'admin/edit_rd.html', {'rd_accounts': rd_accounts})
        
     
    def fd_account(self):
        fd_data = FixedDeposit.objects.all()  
        for obj in fd_data:
            return render(self, 'admin/fd_account.html', {'fd_data': fd_data})
    
    
    def all_fd_plans(self):
        fd_scheme = FD_scheme.objects.all().order_by('-id')
        return render(self, 'admin/all_fd_scheme.html', {'rd_scheme': fd_scheme})
    
    
    def active_fd(self, active, account):
        
        if active == 1:
            FixedDeposit.objects.filter(account_number=account).update(is_active=1)
            
        else:
            FixedDeposit.objects.filter(account_number=account).update(is_active=0) 
            
        fd_data = FixedDeposit.objects.all()
        return render(self, 'admin/fd_account.html', {'fd_data': fd_data})
    
    
    def active_rd(self, active, account):
        if active == 1:
            RecurringDeposit.objects.filter(account_number=account).update(is_active=1)
            
        else:
            RecurringDeposit.objects.filter(account_number=account).update(is_active=0) 
            
        rd_data = RecurringDeposit.objects.all()
        return render(self, 'admin/rd_account.html', {'rd_data': rd_data})
    
    
    def active_loan(self, active, account):
        try:
            customer = Customer.objects.get(member=account)  # account is the ID of the user (Customer)
            member_value = customer.member
        except Customer.DoesNotExist:
            print(f"No customer found with ID: {account}")
            return
            
        if active == 1:
            Personal_loan.objects.filter(user=customer).update(is_active=1) 
        else:
            Personal_loan.objects.filter(user=customer).update(is_active=0)     
        loans = Personal_loan.objects.all().order_by('-id')
        return render(self, 'admin/loans.html', {'loans': loans})
     
    
    
    
   
    def edit_fd(request,account):
        fd_data = get_object_or_404(FixedDeposit, account_number=account)
        customer = fd_data.customer
        fd_accounts = FixedDeposit.objects.filter(customer=customer)
        return render(request,'admin/edit_fd.html/',{'fd_accounts': fd_accounts})

  
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
                return render(self, 'admin/create_fd.html', {'message': message, 'interest_rates': interest_rates})
            
            except Exception as e:
                message = f"An error occurred: {e}"
                interest_rates = FD_scheme.objects.values_list('interest_rate', flat=True)
                return render(self, 'admin/create_fd.html', {'message': message, 'interest_rates': interest_rates})
            
        else:
            interest_rates = FD_scheme.objects.values_list('interest_rate', flat=True)
            return render(self, 'admin/create_fd.html', {'interest_rates': interest_rates})



    def create_loan_account(self):
        if self.method == 'POST':
            try:
                user = self.POST.get('user_id')
                tenure = self.POST.get('tenure')
                amount = self.POST.get('amount')
                interest_rate = self.POST.get('interest_rate')

                try:
                    customer = Customer.objects.get(member=user)
                except Customer.DoesNotExist:
                    message = "Invalid Member ID!"
                    return render(request, 'admin/create_loan.html', {'message': message})

                # If customer exists, create the loan
                loan = Personal_loan(
                    user=customer,
                    tenure=tenure,
                    amount=amount,
                    interest_rate=interest_rate,
                )
                loan.save()  # Save the loan to the database
                
            
                message = f"Loan created successfully! "
                return render(self, 'admin/create_loan.html', {'message': message})
                
                
            except Exception as e:
                message = f"An error occurred: {str(e)}"
                return render(self, 'admin/create_loan.html', {'message': message})

        return render(self, 'admin/create_loan.html')



