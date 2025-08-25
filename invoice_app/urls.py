"""
URL configuration for invoice_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required
from invoices.models import Invoice

@login_required(login_url="/login")
def dashboard(request):
    invoices = Invoice.objects.filter(owner=request.user, is_active=True).order_by('-date', '-created_at')
    return render(request, 'dashboard.html', {
        "invoices": invoices
    })

def login_page(request):
    return render(request, 'login_page.html')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("demo/", include("demo.urls")),
    path("invoices/", include("invoices.urls")),
    path("inventory/", include("inventory.urls", namespace="inventory")),
    path("customer/",include("customer.urls")),
    path("", dashboard, name='dashboard'),
    path("login/", login_page, name='login'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
