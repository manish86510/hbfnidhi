import random

from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from masteradmin.models import *
import datetime


class Dashboard:
    def index(self):
        return render(self, 'admin/login.html')

    def login(self):
        if self.method == 'POST':
            try:
                email = self.POST.get('email')
                password = self.POST.get('password')
                result = Admin.objects.get(email=email, password=password, is_active=1)
                self.session['user_name'] = result.admin_name;
                self.session['user_id'] = result.id;
                self.session['user_role'] = result.role;
                return render(self, 'admin/index.html', {'result': result, 'username': result.admin_name})
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

    def create_saving_account(self):
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
                message = "Saving account created successfully !"
                return render(self, 'admin/create_saving.html', {'message': message})
            except:
                message = "Invalid Member Id !"
                return render(self, 'admin/create_saving.html', {'message': message})
        else:
            return render(self, 'admin/create_saving.html')

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
        credit = CreditTransaction.objects.all().order_by('-id')
        debit = DebitTransaction.objects.all().order_by('-id')
        return render(self, 'admin/saving_transaction.html', {'credit': credit, 'debit': debit})
