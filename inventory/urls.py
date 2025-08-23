from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.item_list, name="list"),
    path("create/", views.item_create, name="create"),
    path("<int:pk>/edit/", views.item_update, name="edit"),
    path("<int:pk>/delete/", views.item_delete, name="delete"),
    path("<int:pk>/", views.item_detail, name="detail"),
    # API
    path("api/search/", views.api_search_items, name="api_search"),
]
