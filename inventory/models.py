from django.db import models
from django.conf import settings
from django.urls import reverse

class Item(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="items"
    )
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)  # percent
    rate_incl = models.DecimalField("Rate (incl. tax)", max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=32, default="pcs")
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code", "name"]

    def __str__(self):
        return f"{self.code} — {self.name}"

    def get_absolute_url(self):
        return reverse("inventory:detail", args=[self.pk])
