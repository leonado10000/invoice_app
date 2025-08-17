from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
# from weasyprint import HTML

# Create your views here.
def invoice_view(request):
    return render(request, 'invoice/main.html')

# def invoice_pdf(request, invoice_id):
#     template = get_template("invoice/main.html")
#     context = {"invoice_id": invoice_id}  # pass dynamic data if needed
#     html = template.render(context)

#     response = HttpResponse(content_type="application/pdf")
#     response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_id}.pdf"'

#     HTML(string=html).write_pdf(response)
#     return response
