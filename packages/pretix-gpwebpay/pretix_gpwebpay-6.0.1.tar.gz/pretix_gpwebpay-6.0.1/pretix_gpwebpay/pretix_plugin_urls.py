"""
URL configuration for pretix_gpwebpay plugin.
This file is automatically discovered by Pretix.
"""
from django.urls import path, include

urlpatterns = [
    path('gpwebpay/', include('pretix_gpwebpay.urls')),
]

