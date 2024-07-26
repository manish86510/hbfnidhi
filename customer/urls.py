from django.contrib import admin
from django.urls import path, include
from customer.views import *

urlpatterns = [
    path('', Dashboard.index),
    path('home',customer_home),
    path('account/', customer_account, name='customer_account'),
    path('download/', download_transactions,name='download_transactions'),    
    # path('funds',customer_funds),
    path('funds/', customer_funds, name='customer_funds'),
    path('bill',customer_bill),
    path('services',customer_services),
    path('invest',customer_invest),
    path('customer',Customer_Login),
    path('profile',customer_profile, name='profile'),
    path('setting',customer_setting),
    path('logout',customer_logout ,name='logout'),
    path('Fd',customer_fd, name='Fd'),
    path('Rd',customer_rd, name='Rd'),
    path('loan',customer_loan),
    path('rate', interest_rate, name='rate'),
    path('get_bank_statement/', get_bank_statement, name='get_bank_statement'),

]

