from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login),
    path('profile', views.profile),
    path('saving', views.saving),
    path('fd', views.fd),
    path('rd', views.rd),
    path('change_password', views.change_password),
    path('apply_fd', views.fd_apply),
    path('apply_rd', views.rd_apply),
    path('calculate_fd', views.calculate_fd),
    path('calculate_rd', views.calculate_rd),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
