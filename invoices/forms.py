from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['company','customer','number','date','due_date','status','notes']
        widgets = {
        'date': forms.DateInput(attrs={'type':'date'}),
        'due_date': forms.DateInput(attrs={'type':'date'}),
        'notes': forms.Textarea(attrs={'rows':3})
        }


InvoiceItemFormset = inlineformset_factory(Invoice, InvoiceItem,
        fields=['item','description','quantity','rate_incl_tax','gst_rate','discount_percent'],
        extra=1, can_delete=True
    )