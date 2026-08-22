"""
URL routes for ledger app.
"""
from django.urls import path

from .views import (
    LedgerAccountListView,
    LedgerTransactionListView,
    LedgerTransactionDetailView,
)

urlpatterns = [
    path("ledger/accounts/", LedgerAccountListView.as_view(), name="ledger-account-list"),
    path("ledger/transactions/", LedgerTransactionListView.as_view(), name="ledger-transaction-list"),
    path("ledger/transactions/<uuid:uuid>/", LedgerTransactionDetailView.as_view(), name="ledger-transaction-detail"),
]
