from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index),
    path('our_company/', views.about),
    path('team/', views.team),
    path('shareholder/', views.shareholder),
    path('enquiry/', views.enquiry),
    path('saving/', views.saving),
    path('fixed/', views.fixed),
    path('recurring/', views.recurring),
    path('loans/', views.loans),
    path('registration/', views.registration),
    path('lockers/', views.lockers),
    path('contact/', views.contact),
    path('create_account/', views.create_account),
    path('doorstep/', views.doorstap),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
