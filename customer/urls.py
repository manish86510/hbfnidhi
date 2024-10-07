from django.contrib import admin
from django.urls import path, include
from customer.views import *

urlpatterns = [
    path('', Dashboard.index),
    path('home/<str:account_no>/',customer_home, name='customer_home'),
    path('account/<str:account_no>/', customer_account, name='customer_account'),
    # path('home/<str:account_no>/', customer_dashboard, name='customer_dashboard'),
    path('download/', download_transactions,name='download_transactions'),    
    path('funds/', customer_funds, name='customer_funds'),
    path('bill/',customer_bill,name='customer_bill' ),
    path('services',customer_services),
    path('invest',customer_invest),
    path('customer',Customer_Login, name='customer_login'),
    path('profile',customer_profile, name='profile'),
    path('profile',customer_edit,name='customer_edit'),
    path('setting',customer_setting),
    path('logout',customer_logout ,name='logout'),
    path('customer/fd/<str:account_number>/', customer_fd, name='customer_fd'),
    path('Fd',customer_fd, name='Fd'),
    path('Rd',customer_rd, name='Rd'),
    path('loan',customer_loan, name='loan'),
    path('create_loan',  create_user_loan, name='create_loan'),
    path('rate', interest_rate, name='rate'),
    path('rddownload/', rd_download_payment, name='rd_download_payment'),
    # path('customer/fd/<int:fd_id>/withdraw/', withdraw_fd, name='withdraw_fd'),
    path('create_fd',  create_fd_account, name='create_fd'),
    path('create_rd',  create_rd_account, name='create_rd'),
    path('send-email/', send_email_view, name='send_email'),
    # path('matured/', withdraw_fd, name='withdraw_fd'),
    path('withdraw_fd/<int:fd_id>/', withdraw_fd, name='withdraw_fd'),
    path('fd_home/', fd_home, name='fd_home'),
    path('rd_home/', rd_home, name='rd_home'),
    path('emii/<int:loan_id>/',loan_emipay, name='loan_emipay'),
    path('celery/',add_view,name='celery'),
    path('rd/deposit/<int:rd_id>/', mark_next_payment_completed, name='mark_next_payment_completed'),
]


