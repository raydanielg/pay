from django.urls import path
from .views import PaymentLinkListView, PaymentLinkDetailView

urlpatterns = [
    path("payment-links/", PaymentLinkListView.as_view(), name="payment-link-list"),
    path("payment-links/<uuid:uuid>/", PaymentLinkDetailView.as_view(), name="payment-link-detail"),
]
