from django.contrib import admin
from django.urls import path
from masteradmin.views import Dashboard
from django.conf import settings
from django.conf.urls.static import static

app_name = "admin"

urlpatterns = [
    path('', Dashboard.login),
    path('dashboard/', Dashboard.login),
    path('login/', Dashboard.login),
    path('logout/', Dashboard.logout),
    path('members/', Dashboard.members),
    path('customers/', Dashboard.customers),
    path('profile/<str:member>/', Dashboard.view_customers),
    path('verify/<int:verify>/<str:member>/', Dashboard.verify_cust),
    path('active/<int:active>/<str:member>/', Dashboard.active_cust),
    path('create_saving_account/', Dashboard.create_saving_account),
    path('saving_account/', Dashboard.saving_account),
    path('saving_account_transaction/',Dashboard.saving_account_transaction),
    path('show_account_transaction/',Dashboard.show_account_transaction),
    path('create_rd_account/', Dashboard.create_rd_account),
    path('create_fd_account/', Dashboard.create_fd_account),
    path('rd_account/', Dashboard.rd_account),
    path('fd_account/', Dashboard.fd_account),
    path('add_member/', Dashboard.member_form),
    path('fd/active/<int:active>/<str:account>/', Dashboard.active_fd),
    path('rd/active/<int:active>/<str:account>/', Dashboard.active_rd),
    path('transfer/', Dashboard.transfer),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
