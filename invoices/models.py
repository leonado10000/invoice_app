from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from inventory.models import Item

User = settings.AUTH_USER_MODEL

class Company(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=100, blank=True)
    state_code = models.CharField(max_length=6, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    bank_account = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=100,default="")
    ifsc = models.CharField(max_length=30, blank=True)

    class Meta:
        unique_together = (('owner','name'),)

    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=100, blank=True)
    state_code = models.CharField(max_length=6, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    code = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price_inclusive_tax = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=30, default='pcs')
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.0)

    def __str__(self):
        return f"{self.code} — {self.name}" if self.code else self.name

class Invoice(models.Model):
    DRAFT = 'draft'
    SENT = 'sent'
    PAID = 'paid'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SENT, 'Sent'),
        (PAID, 'Paid'),
        (CANCELLED, 'Cancelled'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='invoices')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices')
    number = models.CharField(max_length=50)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    notes = models.TextField(blank=True)
    supplier_ref = models.CharField(max_length=100, blank=True)
    other_ref = models.CharField(max_length=100, blank=True)
    despatch_doc_no = models.CharField(max_length=100, blank=True)
    delivery_note_date = models.DateField(null=True, blank=True)
    despatched_through = models.CharField(max_length=100, blank=True)
    destination_other = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # Only the latest version is active

    def __str__(self):
        return f"Invoice {self.number} — {self.customer.name}"

    @property
    def subtotal(self):
        return sum(item.total_without_tax for item in self.items.all())

    @property
    def total_tax(self):
        return sum(item.tax_amount for item in self.items.all())

    @property
    def total(self):
        return round(self.subtotal + self.total_tax,2)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null=True, blank=True)
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, validators=[MinValueValidator(0)])
    rate_incl_tax = models.DecimalField(max_digits=12, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.0)
    rate_tax_ex = models.DecimalField(max_digits=12, decimal_places=2,default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def price_exclusive(self):
        # Convert rate inclusive -> exclusive of tax
        rate = float(self.rate_incl_tax)
        tax_factor = 1 + float(self.gst_rate or 0) / 100.0
        return rate / tax_factor

    @property
    def total_without_tax(self):
        return float(self.price_exclusive   ) * float(self.quantity) * (1 - float(self.discount_percent or 0)/100.0)

    @property
    def tax_amount(self):
        return self.total_without_tax * (float(self.gst_rate or 0)/100.0)

    @property
    def total_with_tax(self):
        return self.total_without_tax + self.tax_amount

    def __str__(self):
        return self.description[:50]
