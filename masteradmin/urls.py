from django.contrib import admin
from django.urls import path, include
from masteradmin.views import Dashboard

urlpatterns = [
    path('', Dashboard.index),
    path('/dashboard', Dashboard.index),
]