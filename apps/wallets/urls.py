"""
URL routes for wallets app.
"""
from django.urls import path

from .views import WalletListCreateView, WalletDetailView
from .views_extra import (
    WalletFreezeView,
    WalletUnfreezeView,
    WalletTransferView,
    WalletDepositView,
)

urlpatterns = [
    path("wallets/", WalletListCreateView.as_view(), name="wallet-list"),
    path("wallets/<uuid:uuid>/", WalletDetailView.as_view(), name="wallet-detail"),
    path("wallets/<uuid:uuid>/freeze/", WalletFreezeView.as_view(), name="wallet-freeze"),
    path("wallets/<uuid:uuid>/unfreeze/", WalletUnfreezeView.as_view(), name="wallet-unfreeze"),
    path("wallets/<uuid:uuid>/transfer/", WalletTransferView.as_view(), name="wallet-transfer"),
    path("wallets/<uuid:uuid>/deposit/", WalletDepositView.as_view(), name="wallet-deposit"),
]
