from django.urls import path
from .views import invoice_pdf, invoice_view, invoice_pos, invoice_detail, invoice_create_or_edit

urlpatterns = [
    path('', invoice_view, name='invoice'),
    # path("invoice/<int:invoice_id>/pdf/", invoice_pdf, name="invoice_pdf"),
    path('pos/<str:pk>', invoice_pos, name='pos'),
    path('details/<int:pk>', invoice_detail, name='detail'),
    path('edit/', invoice_create_or_edit, name='create'),
    path('pdf/<int:pk>', invoice_pdf, name='invoice_pdf'),
]