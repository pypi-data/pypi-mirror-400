"""
URL configuration for The Pay payment provider.

Defines routes for handling payment gateway callbacks:
- return: User redirect after payment completion
- notify: Server-to-server notification (IPN)
"""
from django.urls import path
from . import views

urlpatterns = [
    path('return/<str:order>/<int:payment>/<str:hash>/', views.ReturnView.as_view(), name='return'),
    path('notify/<str:order>/<int:payment>/<str:hash>/', views.NotifyView.as_view(), name='notify'),
]

