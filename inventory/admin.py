from django.contrib import admin
from .models import Item

admin.site.register(Item)
# class ItemAdmin(admin.ModelAdmin):
#     list_display = ('pk','user', 'code','name','gst_rate','is_active')
#     list_filter = ('is_active', 'date')
#     search_fields = ('user', 'code','name','gst_rate')