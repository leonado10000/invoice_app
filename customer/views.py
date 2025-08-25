from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from invoices.models import Customer
from .forms import CustomerForm

@login_required(login_url="/login")
def customer_list(request):
    q = request.GET.get("q", "").strip()
    customers = Customer.objects.filter(user=request.user, is_active=True)
    if q:
        customers = customers.filter(Q(name__icontains=q) | Q(gstin__icontains=q))
    paginator = Paginator(customers, 25)
    page = request.GET.get("page")
    customers_page = paginator.get_page(page)
    return render(request, "customer/customer_list.html", {"customers": customers_page, "q": q})

@login_required(login_url="/login")
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.is_active = True
            customer.save()
            return redirect("customer:list")
    else:
        form = CustomerForm()
    return render(request, "customer/customer_form.html", {"form": form, "is_create": True})

@login_required(login_url="/login")
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer:list")
    else:
        form = CustomerForm(instance=customer)
    return render(request, "customer/customer_form.html", {"form": form, "is_create": False})

@login_required(login_url="/login")
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    if request.method == "POST":
        customer.is_active = False
        customer.save()
        return redirect("customer:list")
    return render(request, "customer/customer_confirm_delete.html", {"customer": customer})

@login_required(login_url="/login")
def api_search_customers(request):
    q = request.GET.get("q", "").strip()
    limit = int(request.GET.get("limit") or 50)
    customers = Customer.objects.filter(user=request.user, is_active=True)
    if q:
        customers = customers.filter(Q(name__icontains=q) | Q(gstin__icontains=q))
    customers = customers.order_by("name")[:limit]
    data = [
        {
            "id": c.id,
            "name": c.name,
            "gstin": c.gstin,
            "state": c.state,
            "state_code": c.state_code,
            "phone": c.phone,
        }
        for c in customers
    ]
    return JsonResponse({"results": data})
