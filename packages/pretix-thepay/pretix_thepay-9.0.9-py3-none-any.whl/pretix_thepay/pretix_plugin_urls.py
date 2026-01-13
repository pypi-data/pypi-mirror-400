"""
URL configuration for pretix_thepay plugin.
This file is automatically discovered by Pretix.
"""
from django.urls import path, include

urlpatterns = [
    path('thepay/', include('pretix_thepay.urls')),
]

