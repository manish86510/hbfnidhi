import random

from django.forms import forms
from django.shortcuts import render, redirect
from masteradmin.models import *
from django.http import HttpResponse, JsonResponse
import datetime
from django.db import models
from rest_framework.views import APIView
from customer.serializer import CustomerSerializer
from rest_framework.response import Response
from rest_framework import status
from masteradmin.models import SavingAccount
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth import authenticate



class Dashboard():
    def index(self):
        return render(self, 'Customer/login.html')


# import ipdb
def Customer_Login(request):
     if request.method == 'POST':
         enter_email = request.POST.get('username')
         enter_password = request.POST.get('pass')
        #  ipdb.set_trace()
         if Customer.objects.filter(email=enter_email,password=enter_password):
             result = Customer.objects.get(email=enter_email)
             request.session['customer_name'] = result.first_name
             request.session['customer_id'] = result.id
             return render(request, 'Customer/Home.html')
         else:
             message = "Invalid Credentials"
             return render(request,'Customer/login.html', {'message': message})
     else:
         return render(request,'Customer/login.html')



        




def customer_logout(request):
        del request.session['customer_name']
        del request.session['customer_id']
        return render(request, 'Customer/login.html')


def customer_account(request):
    # Assuming you want to pass some context data to the template
    context = {
        'title': 'Customer Account Information',
        'message': 'Welcome to the customer account page!',
        # Add more context data as needed
    }
    return render(request, 'Customer/Accounts.html', context)


def customer_bill(self):
    return render(self,'Customer/Bill.html')



# class CustomerAccountInfoView(View):
#     def get(self, request, member):
#         try:
#             account = get_object_or_404(SavingAccount, member=member)
#             context = {
#                 'title': 'Customer Account Information',
#                 'account': account,
                
#             }
#             return render(request, 'Customer/Accounts.html', context)
#         except SavingAccount.DoesNotExist:
#             return render(request, 'Customer/account_not_found.html', status=404)

# class CustomerAccountInfoView(View):
#     def get(self, request):
#         # Get customer_id from session
#         customer_id = request.session.get('customer_id')

#         if customer_id:
#             try:
#                 account = get_object_or_404(SavingAccount, member=customer_id)
#                 context = {
#                     'title': 'Customer Account Information',
#                     'account': account,
#                 }
#                 return render(request, 'Customer/Accounts.html', context)
#             except SavingAccount.DoesNotExist:
#                 return render(request, 'Customer/account_not_found.html', status=404)
#         else:
#             # Handle case where customer_id is not in session (user not logged in)
#             return redirect('customer-login')  


class CustomerAccountInfoView(View):
    def get(self, request):
        # Get customer_id from session
        customer_id = request.session.get('customer_id')

        if customer_id:
            try:
                account = get_object_or_404(SavingAccount, member=customer_id)
                context = {
                    'title': 'Customer Account Information',
                    'account': account,
                }
                return render(request, 'Customer/Accounts.html', context)
            except SavingAccount.DoesNotExist:
                return render(request, 'Customer/account_not_found.html', status=404)
        else:
            # Handle case where customer_id is not in session (user not logged in)
            return redirect('customer-login')
        

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


def customer_funds(self):
    return render(self, 'Customer/Funds.html')


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
