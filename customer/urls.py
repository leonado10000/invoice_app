from django.urls import path
from . import views

app_name = "customer"

urlpatterns = [
    path("", views.customer_list, name="list"),
    path("add/", views.customer_create, name="create"),
    path("<int:pk>/edit/", views.customer_update, name="update"),
    path("<int:pk>/delete/", views.customer_delete, name="delete"),
    path("api/search/", views.api_search_customers, name="api_search"),
]
