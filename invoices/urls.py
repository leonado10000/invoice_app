from django.urls import path
from .views import invoice_dashboard, invoice_view

urlpatterns = [
    path('', invoice_view, name='invoice'),
    # path("invoice/<int:invoice_id>/pdf/", invoice_pdf, name="invoice_pdf"),
    path('dashboard/', invoice_dashboard, name='dashboard'),
]