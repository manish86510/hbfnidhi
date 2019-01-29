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


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(self):
    email = self.data.get('email')
    password = self.data.get('password')
    try:
        token = Customer.objects.get(email=email, password=password, is_active=1)
        username = token.first_name+' '+token.last_name
        account = SavingAccount.objects.get(member=token.member)
        return Response({'id': token.id, 'user_name': username, 'account_no': account.account_no, 'balance': account.account_balance},
                 status=HTTP_200_OK)
    except:
        result = "Invalid entry !"
        return Response({'result': result},
                 status=HTTP_400_BAD_REQUEST)
