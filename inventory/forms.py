from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ["user", "created_at", "updated_at","is_active"]
