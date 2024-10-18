from django.contrib import admin
from django.urls import path, include
from customer.views import *

urlpatterns = [
    path('', Dashboard.index),
    path('login',Customer_Login, name='customer_login'),
    path('profile',customer_profile, name='profile'),
    path('edit',customer_edit,name='customer_edit'),
    path('setting',customer_setting),
    path('logout',customer_logout ,name='logout'),
    path('home/<str:account_no>/',customer_home, name='customer_home'),
    path('account/<str:account_no>/', customer_account, name='customer_account'),
    path('accountsdownload/', download_transactions,name='download_transactions'),    
    path('funds/', customer_funds, name='customer_funds'),
    path('bill/',customer_bill,name='customer_bill' ),
    path('services',customer_services),
    path('invest',customer_invest),
    path('create_fd',  create_fd_account, name='create_fd'),
    path('customer/fd/<str:account_number>/', customer_fd, name='customer_fd'),
    path('fd_home/', fd_home, name='fd_home'),
    path('Fd',customer_fd, name='Fd'),
    path('withdraw_fd/<int:fd_id>/', withdraw_fd, name='withdraw_fd'),
    path('create_rd',  create_rd_account, name='create_rd'),
    path('Rd',customer_rd, name='Rd'),
    path('rddownload/', rd_download_payment, name='rd_download_payment'),
    path('rd/deposit/<int:rd_id>/', mark_next_payment_completed, name='mark_next_payment_completed'),
    path('rd_home/', rd_home, name='rd_home'),
    path('loan',customer_loan, name='loan'),    
    path('create_loan',  create_user_loan, name='create_loan'),
    path('emii/<int:loan_id>/',loan_emipay, name='loan_emipay'),
    path('rate', interest_rate, name='rate'),
    # path('customer/fd/<int:fd_id>/withdraw/', withdraw_fd, name='withdraw_fd'),
    # path('send-email/', send_email_view, name='send_email'),
    # path('matured/', withdraw_fd, name='withdraw_fd'),
    # path('celery/',add_view,name='celery'),
   
]


