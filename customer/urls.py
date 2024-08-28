from django.contrib import admin
from django.urls import path, include
from customer.views import *

urlpatterns = [
    # path('create_rd_account/', Dashboard.create_rd_account),
    path('', Dashboard.index),
    path('home',customer_home, name='customer_home'),
    path('account/<str:account_no>/', customer_account, name='customer_account'),
    path('download/', download_transactions,name='download_transactions'),    
    path('funds/', customer_funds, name='customer_funds'),
    path('bill/',customer_bill,name='customer_bill' ),
    path('services',customer_services),
    path('invest',customer_invest),
    path('customer',Customer_Login),
    path('profile',customer_profile, name='profile'),
    path('setting',customer_setting),
    path('logout',customer_logout ,name='logout'),
    path('Fd',customer_fd, name='Fd'),
    path('Rd',customer_rd, name='Rd'),
    path('loan',customer_loan, name='loan'),
    path('create_loan',  create_user_loan, name='create_loan'),
    path('rate', interest_rate, name='rate'),
    path('get_bank_statement/', get_bank_statement, name='get_bank_statement'),
    path('download/', download_payment, name='download_payment'),
    # path('customer/fd/<int:fd_id>/withdraw/', withdraw_fd, name='withdraw_fd'),
    path('create_fd',  create_fd_account, name='create_fd'),
    path('create_rd',  create_rd_account, name='create_rd'),
    path('send-email/', send_email_view, name='send_email'),
    # path('matured/', withdraw_fd, name='withdraw_fd'),
    path('withdraw_fd/<int:fd_id>/', withdraw_fd, name='withdraw_fd'),
    path('home/', fd_home, name='fd_home'),
    
]

