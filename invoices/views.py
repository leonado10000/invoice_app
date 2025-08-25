import json
import math
import datetime
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Invoice, InvoiceItem, Customer, Company
from invoice_app.urls import dashboard
from inventory.models import Item
from .forms import InvoiceForm, InvoiceItemFormset
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from xhtml2pdf import pisa

_NUM_WORDS_0_19 = [
    'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six',
    'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve',
    'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen',
    'Eighteen', 'Nineteen'
]

_TENS_WORDS = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

_SCALE_UNITS = [
    (10**7, 'Crore'),
    (10**5, 'Lakh'),
    (10**3, 'Thousand'),
    (10**2, 'Hundred')
]

def number_to_indian_words(num: int) -> str:
    num = int(num)
    if num < 0:
        return 'Minus ' + number_to_indian_words(-num)
    if num < 20:
        return _NUM_WORDS_0_19[num]
    if num < 100:
        tens, rem = divmod(num, 10)
        tens = int(tens)
        rem = int(rem)
        return _TENS_WORDS[tens] + (f' {_NUM_WORDS_0_19[rem]}' if rem else '')
    
    for scale_val, scale_name in _SCALE_UNITS:
        if num >= scale_val:
            leading, rem = divmod(num, scale_val)
            words = number_to_indian_words(leading) + f' {scale_name}'
            if rem:
                words += ' ' + number_to_indian_words(rem)
            return words
    # Should not reach here
    return ''

def amount_to_words(num: int) -> str:
    return number_to_indian_words(num) + ' Only'


def parse_date_safe(value):
    """
    Convert YYYY-MM-DD string → date object.
    Returns None if invalid/empty.
    """
    if not value:
        return None
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

@login_required(login_url="/login")
def invoice_view(request):
    return render(request, "invoice/main.html")

@login_required(login_url="/login")
def invoice_pos(request, pk):
    cart = []
    invoice = None
    if pk.lower() != "new":
        invoice = get_object_or_404(Invoice.objects.select_related("customer"), pk=int(pk), owner=request.user, is_active=True)
        cart = [
            { 
                "id": item.item.id,
                "code": item.item.code, 
                "name": item.item.name, 
                "gst_rate": item.item.gst_rate, 
                "rate_incl": item.item.rate_incl, 
                "unit": item.item.unit,
                "qty": item.quantity
            } for item in InvoiceItem.objects.filter(invoice=invoice)
        ]
    d = [{ 
            "id": item.id,
            "code": item.code, 
            "name": item.name, 
            "gst_rate": item.gst_rate, 
            "rate_incl": item.rate_incl, 
            "unit": item.unit
        } for item in Item.objects.filter(user=request.user)
    ]
    buyers = Customer.objects.filter(is_active=True)
    return render(request, "invoice/pos.html", {
        "data":d,
        "buyers": buyers,
        "cart":cart,
        "invoice_pk":pk,
        "invoice":invoice,
        "status_list": [("DRAFT", 'draft'),
                        ("SENT", 'sent'),
                        ("PAID", 'paid'),
                        ("CANCELLED", 'cancelled'),
    ]
    })


@login_required(login_url="/login")
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user)

    items = invoice.items.select_related('item').all()
    total_wo_tax = 0
    cgst = 0
    sgst = 0
    tax_list = {}

    # Row calculations
    for i, it in enumerate(items, start=1):
        qty = float(it.quantity or 0)
        total_of_item_wo_tax = float(it.total_without_tax or 0)
        total_wo_tax += total_of_item_wo_tax 

        rate = float(it.rate_incl_tax or 0)
        it.amount = qty * rate
        tax_list[int(it.gst_rate//2)] = {
            "taxable_value":tax_list.get(int(it.gst_rate//2),{"taxable_value":0})["taxable_value"] + total_of_item_wo_tax,
            "taxed_amount":tax_list.get(int(it.gst_rate//2),{"taxed_amount":0})["taxed_amount"] + (it.amount - total_of_item_wo_tax)/2,
            "total_taxed":tax_list.get(int(it.gst_rate//2),{"total_taxed":0})["total_taxed"] + (it.amount - total_of_item_wo_tax)
        }

        cgst += (it.amount - total_of_item_wo_tax)/2
    
    sgst = cgst
    total = total_wo_tax + cgst + sgst
    round_off = total - math.floor(total)
    total_with_tax = math.floor(total)
    context = {
        'invoice': invoice,
        'items': items,
        'total_wo_tax': total_wo_tax,
        'total_tax_amount_words':amount_to_words(int(cgst*2)),
        'cgst': cgst,
        'sgst': sgst,
        'total_tax': cgst*2,
        'round_off': round_off,
        'total': total_with_tax,
        'total_full':total,
        'total_full_words':amount_to_words(total),
        'pdf': True,
        'tax_list':tax_list
    }
    items = InvoiceItem.objects.filter(invoice=invoice).select_related('item')
    return render(request, 'invoice/main.html', context)


@login_required(login_url="/login")
def invoice_create_or_edit(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            invoice_data = data.get("invoiceData", {})
            items_data = data.get("items", [])

            # --- CUSTOMER ---
            customer_name = invoice_data.get("buyer_name")
            customer, _ = Customer.objects.get_or_create(
                user=request.user,
                name=customer_name,
                defaults={
                    "address": invoice_data.get("buyer_address", ""),
                    "gstin": invoice_data.get("buyer_gstin", ""),
                    "state": invoice_data.get("buyer_state", ""),
                    "state_code": invoice_data.get("buyer_state_code", ""),
                    "phone": invoice_data.get("buyer_phone", "")
                }
            )
            

            # --- EDIT MODE: create new version ---
            old_invoice = None
            if invoice_data.get("invoice_pk") and invoice_data.get("invoice_pk").lower() != "new":
                old_invoice = get_object_or_404(Invoice, pk=invoice_data["invoice_pk"], owner=request.user)
                old_invoice.is_active = False
                old_invoice.save()
            
            # --- CREATE NEW INVOICE ---
            company = old_invoice.company if old_invoice else Company.objects.filter(owner=request.user).first()
            if not company:
                return JsonResponse({"error": "No company found for user"}, status=400)
            invoice_obj = Invoice.objects.create(
                owner=request.user,
                company=company,
                customer=customer,
                number=old_invoice.number if old_invoice else invoice_data.get("invoice_number"),
                date=parse_date_safe(invoice_data.get("invoice_date")),
                due_date=parse_date_safe(invoice_data.get("due_date")),
                notes=invoice_data.get("notes", ""),
                supplier_ref=invoice_data.get("supplier_ref", ""),
                other_ref=invoice_data.get("other_ref", ""),
                despatch_doc_no=invoice_data.get("despatch_doc_no", ""),
                delivery_note_date=parse_date_safe(invoice_data.get("delivery_note_date")),
                despatched_through=invoice_data.get("despatched_through", ""),
                destination_other=invoice_data.get("destination_other", ""),
                status=invoice_data.get("status", Invoice.DRAFT),
                is_active=True
            )
            
            # --- INVOICE ITEMS ---
            for item_data in items_data:
                linked_item = None
                if "id" in item_data:
                    linked_item = Item.objects.filter(pk=item_data["id"]).first()

                InvoiceItem.objects.create(
                    invoice=invoice_obj,
                    item=linked_item,
                    description=item_data.get("name", ""),
                    quantity=item_data.get("qty", 1),
                    rate_incl_tax=item_data.get("rate_incl", 0),
                    rate_tax_ex=(item_data.get("rate_incl", 0) / (1 + (item_data.get("gst_rate", 18) / 100))),
                    gst_rate=item_data.get("gst_rate", 18),
                    discount_percent=item_data.get("discount", 0)
                )
            

        except Exception as e:
            print("Error processing invoice:", str(e))
            return JsonResponse({"error": str(e)}, status=400)

    return dashboard(request)

def pdf_test(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user)

    items = invoice.items.select_related('item').all()
    total_wo_tax = 0

    # Row calculations
    for i, it in enumerate(items, start=1):
        qty = float(it.quantity or 0)
        rate = float(it.rate_incl_tax or 0)
        it.amount = qty * rate  # equivalent to JS row amount
        total_wo_tax += it.amount

    # Tax calculations (same as JS)
    cgst = total_wo_tax * 0.09
    sgst = total_wo_tax * 0.09
    total = total_wo_tax + cgst + sgst
    round_off = round(total) - total
    total_with_tax = round(total)

    context = {
        'invoice': invoice,
        'items': items,
        'total_wo_tax': total_wo_tax,
        'cgst': cgst,
        'sgst': sgst,
        'round_off': round_off,
        'total': total_with_tax,
        'pdf': True
    }

    # Render HTML
    return render(request,'invoice_pdf/main.html', context)
    
@login_required(login_url="/login")
def link_callback(uri, rel):
    """
    Convert HTML URIs from {% static %} or MEDIA_URL to absolute system paths
    so xhtml2pdf can access them.
    """
    from django.conf import settings
    from django.contrib.staticfiles import finders
    import os

    if uri.startswith(settings.STATIC_URL):
        path = uri.replace(settings.STATIC_URL, '')
        absolute_path = finders.find(path)
        if absolute_path:
            if isinstance(absolute_path, (list, tuple)):
                absolute_path = absolute_path[0]
            return absolute_path

    if settings.MEDIA_URL and uri.startswith(settings.MEDIA_URL):
        path = uri.replace(settings.MEDIA_URL, '')
        return os.path.join(settings.MEDIA_ROOT, path)

    return uri  # leave absolute URLs as-is

@login_required(login_url="/login")
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user)

    items = invoice.items.select_related('item').all()
    total_wo_tax = 0
    cgst = 0
    sgst = 0
    tax_list = {}

    # Row calculations
    for i, it in enumerate(items, start=1):
        qty = float(it.quantity or 0)
        total_of_item_wo_tax = float(it.total_without_tax or 0)
        total_wo_tax += total_of_item_wo_tax 

        rate = float(it.rate_incl_tax or 0)
        it.amount = qty * rate
        tax_list[int(it.gst_rate//2)] = {
            "taxable_value":tax_list.get(int(it.gst_rate//2),{"taxable_value":0})["taxable_value"] + total_of_item_wo_tax,
            "taxed_amount":tax_list.get(int(it.gst_rate//2),{"taxed_amount":0})["taxed_amount"] + (it.amount - total_of_item_wo_tax)/2,
            "total_taxed":tax_list.get(int(it.gst_rate//2),{"total_taxed":0})["total_taxed"] + (it.amount - total_of_item_wo_tax)
        }

        cgst += (it.amount - total_of_item_wo_tax)/2
    
    sgst = cgst
    total = total_wo_tax + cgst + sgst
    round_off = total - math.floor(total)
    total_with_tax = math.floor(total)
    context = {
        'invoice': invoice,
        'items': items,
        'total_wo_tax': total_wo_tax,
        'total_tax_amount_words':amount_to_words(int(cgst*2)),
        'cgst': cgst,
        'sgst': sgst,
        'total_tax': cgst*2,
        'round_off': round_off,
        'total': total_with_tax,
        'total_full':total,
        'total_full_words':amount_to_words(total),
        'pdf': True,
        'tax_list':tax_list
    }

    # Render HTML
    html = render_to_string('invoice_pdf/main.html', context, request=request)

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{invoice.number}_{invoice.date}.pdf'
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response
