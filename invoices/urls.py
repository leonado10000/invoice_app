from django.urls import path
from .views import invoice_view
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML

def invoice_pdf(request, invoice_id):
    template = get_template("invoice/main.html")
    context = {"invoice_id": invoice_id}  # pass dynamic data if needed
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_id}.pdf"'

    HTML(string=html).write_pdf(response)
    return response

urlpatterns = [
    path('', invoice_view, name='invoice'),
    path("invoice/<int:invoice_id>/pdf/", invoice_pdf, name="invoice_pdf"),
]