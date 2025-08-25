from django import forms
from invoices.models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ["user", "is_active", "created_at", "updated_at"]
