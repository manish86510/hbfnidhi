from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin', include('masteradmin.urls')),
    path('', admin.site.urls),
]
