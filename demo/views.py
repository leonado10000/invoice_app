from django.shortcuts import render

def demo_invoice_view(request):
    return render(request, "demo/main.html")