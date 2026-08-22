"""
URL routes for transactions app.
"""
from django.urls import path

from .views import (
    TransactionListCreateView,
    TransactionDetailView,
    CustomerListCreateView,
    CustomerDetailView,
)

urlpatterns = [
    path("transactions/", TransactionListCreateView.as_view(), name="transaction-list"),
    path("transactions/<uuid:uuid>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("customers/", CustomerListCreateView.as_view(), name="customer-list"),
    path("customers/<uuid:uuid>/", CustomerDetailView.as_view(), name="customer-detail"),
]
