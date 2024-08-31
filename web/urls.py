from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from web.views import *

urlpatterns = [
    path('', views.index),
    path('contact/', contact_view, name='contact_view'),
    path('our_company/', views.about),
    path('team/', views.team),
    path('shareholder/', views.shareholder),
    path('enquiry/', views.enquiry),
    path('saving/', views.saving),
    path('fixed/', views.fixed),
    path('recurring/', views.recurring),
    path('loans/', views.loans),
    path('monthly-income-plan/',views.monthlyincome),
    path('registration/', views.registration),
    # path('lockers/', views.lockers),
    path('contact/', views.contact),
    path('gold-loan/',views.goldloan),
    path('loan-against-insurance-policy/',views.loanagainstinsurancepolicy),
    path('loan-against-govt-bond/',views.loanagainstgovtbond),
    path('deposit-receipt/',views.loanagainstdepositreceipt),
    path('create_account/', views.create_account),
    # path('doorstep/', views.doorstap),
    # path(''/,)
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
