import random

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from masteradmin.models import *



@api_view(["POST"])
@permission_classes((AllowAny,))
def login(self):
    email = self.data.get('email')
    password = self.data.get('password')
    try:
        token = Customer.objects.get(email=email, password=password, is_active=1)
        username = token.first_name+' '+token.last_name
        account = SavingAccount.objects.get(member=token.member)
        return Response({'id': token.member, 'user_name': username, 'account_no': account.account_no, 'balance': account.account_balance},
                 status=HTTP_200_OK)
    except:
        result = "Invalid entry !"
        return Response({'result': result}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def profile(self):
    data = self.data.get('member')
    try:
        profile_info = Customer.objects.get(member=data)
        id = profile_info.id
        first_name = profile_info.first_name
        last_name = profile_info.last_name
        email = profile_info.email
        contact = profile_info.mobile
        gender = profile_info.gender
        personal = {'first_name': first_name, 'last_name': last_name, 'email': email, 'contact': contact, 'gender': gender}
        try:
            family = UserFamily.objects.get(user=id)
            nominee_name = family.nominee_name
            nrelation = family.nominee_relationship
            ndob = family.nominee_dob
            guardian = family.guardian_name
            guardian_relation = family.guardian_relation
            guardian_dob = family.nominee_dob
            family_info = {'nominee_name': nominee_name, 'nrelation': nrelation, 'ndob': ndob, 'guardian': guardian, 'grelation': guardian_relation, 'gdob': guardian_dob}
        except:
            family_info = None
        return Response({'profile': personal, 'family': family_info}, status=HTTP_200_OK)
    except:
        result = "Member not found!"
        return Response({'result': result}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def saving(self):
    data = self.data.get('member')
    try:
        saving = SavingAccount.objects.get(member=data)
        account_no = saving.account_no
        ifsc = saving.ifsc
        branch_code = saving.branch_code
        balance = saving.account_balance
        saving_info = {'account': account_no, 'ifsc': ifsc, 'branch_code': branch_code, 'balance': balance}
        return Response({'saving_info': saving_info}, status=HTTP_200_OK)
    except:
        return Response({'result': "error"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def fd(self):
    data = self.data.get('member')
    try:
        fd = FD.objects.get(associated_member=data, is_active=1)
        account_no = fd.account_number
        amount = fd.amount
        tenure = fd.tenure
        rate = fd.rate_of_interest
        maturity = fd.maturity_amount
        date = fd.created_date
        status = fd.status
        fd_info = {'account': account_no, 'tenure': tenure, 'rate': rate, 'amount': amount, 'maturity': maturity, 'created': date, 'status': status}
        return Response({'fd_info': fd_info}, status=HTTP_200_OK)
    except:
        return Response({'result': "error"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def rd(self):
    data = self.data.get('member')
    try:
        rd = RD.objects.get(associated_member=data, is_active=1)
        account_no = rd.account_number
        amount = rd.amount
        tenure = rd.tenure
        rate = rd.rate_of_interest
        maturity = rd.maturity_amount
        date = rd.created_date
        status = rd.status
        rd_info = {'account': account_no, 'tenure': tenure, 'rate': rate, 'amount': amount, 'maturity': maturity, 'created': date, 'status': status}
        return Response({'fd_info': rd_info}, status=HTTP_200_OK)
    except:
        return Response({'result': "error"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def change_password(self):
    email = self.data.get('email')
    password = self.data.get('old_pass')
    new_pass = self.data.get('new_pass')
    try:
        Customer.objects.filter(email=email, password=password).update(password=new_pass)
        return Response({'result': "success"}, status=HTTP_200_OK)
    except:
        return Response({'result': "error"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def fd_apply(self):
    member = self.data.get('member')
    tenure = self.data.get('tenure')
    amount = self.data.get('amount')
    breakable = self.data.get('breakable')
    interest = self.data.get('interest')
    maturity_amount = self.data.get('maturity_amount')
    created_date = models.DateTimeField(auto_now_add=True)
    status = "pending"
    account = random.randint(11111111, 99999999)
    scheme_info = FD_scheme.objects.get(tenure=tenure, breakable=breakable)
    try:
        FD.objects.create(
            account_number="FD" + str(account),
            tenure=tenure,
            amount=amount,
            rate_of_interest=interest,
            maturity_amount=maturity_amount,
            status="Pending",
            is_active=0,
            scheme=scheme_info.id,
            created_date=models.DateTimeField(auto_now_add=True),
            associated_member=member,
        ).save()
        return Response({'result': "FD Account Created Successfully !"}, status=HTTP_200_OK)
    except:
        return Response({'result': "error"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def rd_apply(self):
    member = self.data.get('member')
    tenure = self.data.get('tenure')
    amount = self.data.get('amount')
    interest = self.data.get('interest')
    maturity_amount = self.data.get('maturity_amount')
    created_date = models.DateTimeField(auto_now_add=True)
    status = "pending"
    account = random.randint(11111111, 99999999)
    try:
        RD.objects.create(
            account_number="RD" + str(account),
            tenure=tenure,
            amount=amount,
            rate_of_interest=interest,
            maturity_amount=maturity_amount,
            status="Pending",
            is_active=0,
            created_date=models.DateTimeField(auto_now_add=True),
            associated_member=member,
        ).save()
        return Response({'result': "RD Account Created Successfully !"}, status=HTTP_200_OK)
    except:
        return Response({'result': "error"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def calculate_fd(self):
    amount = self.data.get('amount')
    tenure = self.data.get('tenure')
    breakable = self.data.get('breakable')
    try:
        scheme_info = FD_scheme.objects.get(tenure=tenure, breakable=breakable)
        interest = scheme_info.interest_rate
        irate = interest / 400
        maturity_amount = (1 + irate)
        time = (tenure / 12)
        power = pow(time, maturity_amount)
        mat_amount = amount * power
        fd_data = {'interest': interest, 'maturity_amount': mat_amount}
        return Response({'result': fd_data}, status=HTTP_200_OK)
    except:
        return Response({'result': "error"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def calculate_rd(self):
    amount = self.data.get('amount')
    tenure = self.data.get('tenure')
    try:
        interest = 8
        irate = interest / 100
        maturity_amount = (1 + irate)
        time = (tenure / 12)
        power = pow(time, maturity_amount)
        mat_amount = amount * power
        rd_data = {'interest': interest, 'maturity_amount': mat_amount}
        return Response({'result': rd_data}, status=HTTP_200_OK)
    except:
        return Response({'result': "error"}, status=HTTP_400_BAD_REQUEST)
