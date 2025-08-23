from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Item
from .forms import ItemForm

@login_required(login_url="/login")
def item_list(request):
    q = request.GET.get("q", "").strip()
    items = Item.objects.filter(user=request.user, is_active=True)
    if q:
        items = items.filter(Q(code__icontains=q) | Q(name__icontains=q))
    paginator = Paginator(items, 25)
    items_page = paginator.get_page(request.GET.get("page"))
    return render(request, "inventory/item_list.html", {"items": items_page, "q": q})

@login_required(login_url="/login")
def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.is_active = True
            item.save()
            return redirect("inventory:list")
    else:
        form = ItemForm()
    return render(request, "inventory/item_form.html", {"form": form, "is_create": True})

@login_required(login_url="/login")
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, "inventory/item_detail.html", {"item": item})

@login_required(login_url="/login")
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("inventory:list")
    else:
        form = ItemForm(instance=item)
    return render(request, "inventory/item_form.html", {"form": form, "item": item, "is_create": False})

@login_required(login_url="/login")
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    if request.method == "POST":
        item.is_active = False
        item.save()
        print("is active turned false",item)
        return redirect("inventory:list")
    return render(request, "inventory/item_confirm_delete.html", {"item": item})

@login_required(login_url="/login")
def api_search_items(request):
    q = request.GET.get("q", "").strip()
    gst = request.GET.get("gst", "").strip()
    limit = int(request.GET.get("limit") or 50)

    items = Item.objects.filter(user=request.user, active=True)
    if q:
        items = items.filter(Q(code__icontains=q) | Q(name__icontains=q))
    if gst:
        try:
            items = items.filter(gst_rate=float(gst))
        except Exception:
            pass

    items = items.order_by("code")[:limit]
    data = [
        {
            "id": it.id,
            "code": it.code,
            "name": it.name,
            "description": it.description,
            "gst_rate": float(it.gst_rate),
            "rate_incl": float(it.rate_incl),
            "unit": it.unit,
            "stock_quantity": float(it.stock_quantity),
        }
        for it in items
    ]
    return JsonResponse({"results": data})
