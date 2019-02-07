import random

from django.contrib import messages
from django.shortcuts import render
from masteradmin.models import *


class Dashboard:
    def index(self):
        if self.session['user_name']:
            cust = Customer.objects.count()
            fd = FD.objects.count()
            rd = RD.objects.count()
            try:
                customer = Customer.objects.filter(is_active=0).all().order_by('-id')
            except:
                customer = None
            return render(self, 'admin/index.html', {'cust': cust, 'fd': fd, 'rd': rd, 'customer': customer})
        else:
            return render(self, 'admin/login.html')

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
                fd = FD.objects.count()
                rd = RD.objects.count()
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

    def saving_account_transaction(self):
        return render(self, 'admin/transaction.html')

    def show_account_transaction(self):
        return render(self, 'admin/saving_transaction.html')

    def logout(self):
        del self.session['user_id']
        del self.session['user_name']
        return render(self, 'admin/login.html')

    def create_rd_account(self):
        if self.method == 'POST':
            try:
                member = self.POST.get('member_id')
                memberid = Customer.objects.get(member=member)
                account = random.randint(1111111111, 9999999999)
                saving_account = SavingAccount(
                    member=self.POST.get('member_id'),
                    account_no="SA"+str(account),
                    ifsc=self.POST.get('ifsc'),
                    branch_code=self.POST.get('branch_code'),
                    branch_name=self.POST.get('branch_name'),
                    account_balance=self.POST.get('balance'),
                    status="success",
                    is_active=1,
                    created_date=models.DateTimeField(auto_now_add=True),
                )
                saving_account.save()
                message = "RD created successfully !"
                return render(self, 'admin/create_rd.html', {'message': message})
            except:
                message = "Invalid Member Id !"
                return render(self, 'admin/create_rd.html', {'message': message})
        else:
            return render(self, 'admin/create_rd.html')

    def create_fd_account(self):
        if self.method == 'POST':
            try:
                member = self.POST.get('member_id')
                memberid = Customer.objects.get(member=member)
                account = random.randint(1111111, 9999999)
                saving_account = SavingAccount(
                    member=self.POST.get('member_id'),
                    account_no="FD"+str(account),
                    tenure=self.POST.get('tenure'),
                    rate_of_interest=self.POST.get('rate_of_interest'),
                    maturity_amount=self.POST.get('branch_name'),
                    status="success",
                    is_active=1,
                    created_date=models.DateTimeField(auto_now_add=True),
                )
                saving_account.save()
                message = "FD created successfully !"
                return render(self, 'admin/create_fd.html', {'message': message})
            except:
                message = "Invalid Member Id !"
                return render(self, 'admin/create_fd.html', {'message': message})
        else:
            return render(self, 'admin/create_fd.html')

    def fd_account(self):
        fd_data = FD.objects.all()
        return render(self, 'admin/fd_account.html', {'fd_data': fd_data})

    def rd_account(self):
        rd_data = RD.objects.all()
        return render(self, 'admin/rd_account.html', {'rd_data': rd_data})

    def active_fd(self, active, account):
        FD.objects.filter(account_number=account).update(is_active=active)
        fd_data = FD.objects.all()
        return render(self, 'admin/fd_account.html', {'fd_data': fd_data})

    def active_rd(self, active, account):
        RD.objects.filter(account_number=account).update(is_active=active)
        rd_data = RD.objects.all()
        return render(self, 'admin/rd_account.html', {'rd_data': rd_data})

    def transfer(self):
        try:
            credit = CreditTransaction.objects.all().order_by('-id')
        except:
            credit = None
        try:
            debit = DebitTransaction.objects.all().order_by('-id')
        except:
            debit = None
        return render(self, 'admin/saving_transaction.html', {'credit': credit, 'debit': debit})

    def saving_info(self, member, account):
        try:
            customer = Customer.objects.get(member=member, is_active=1)
            saving_info = SavingAccount.objects.get(account_no=account, is_active=1)
        except:
            customer = None
            saving_info = None
        try:
            credit = CreditTransaction.objects.all(member=member).order_by('-id')
        except:
            credit = None
        try:
            debit = DebitTransaction.objects.all(member=member).order_by('-id')
        except:
            debit = None
        return render(self, 'admin/transaction_info.html', {'credit': credit, 'debit': debit, 'saving': saving_info, 'customer': customer})

    def fd_info(self, account_number, associated_member):
        try:
            customer = Customer.objects.get(member=associated_member)
            fd_info = FD.objects.get(account_number=account_number)
        except:
            customer = None
            fd_info = None
        return render(self, 'admin/fd_info.html', {'fd': fd_info, 'customer': customer})

    def rd_info(self, account_number, associated_member):
        try:
            customer = Customer.objects.get(member=associated_member)
            rd_info = RD.objects.get(account_number=account_number)
        except:
            customer = None
            rd_info = None
        return render(self, 'admin/rd_info.html', {'rd': rd_info, 'customer': customer})

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

    def all_rd_plans(self):
        rd_scheme = RD_scheme.objects.all().order_by('-id')
        return render(self, 'admin/all_rd_scheme.html', {'rd_scheme': rd_scheme})

    def all_fd_plans(self):
        fd_scheme = FD_scheme.objects.all().order_by('-id')
        return render(self, 'admin/all_fd_scheme.html', {'rd_scheme': fd_scheme})
