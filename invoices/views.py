from django.shortcuts import render

# Create your views here.
def invoice_view(request):
    return render(request, 'invoice/main.html')