from django.urls import path
from .views import demo_invoice_view

urlpatterns = [
    path('', demo_invoice_view, name='demo'),
]