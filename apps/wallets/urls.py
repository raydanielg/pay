"""
URL routes for wallets app.
"""
from django.urls import path

from .views import WalletListCreateView, WalletDetailView

urlpatterns = [
    path("wallets/", WalletListCreateView.as_view(), name="wallet-list"),
    path("wallets/<uuid:uuid>/", WalletDetailView.as_view(), name="wallet-detail"),
]
