from django.contrib import admin
from .models import Company, Customer, Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('pk','number', 'customer', 'date', 'status', 'owner','is_active')
    list_filter = ('status', 'date')
    search_fields = ('number', 'customer__name')
    inlines = [InvoiceItemInline]


admin.site.register(Company)
admin.site.register(Customer)