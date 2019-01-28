from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import web

urlpatterns = [
    path('admin/', include('masteradmin.urls')),
    path('', include('web.urls')),
    path('customer/', include('customer.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
