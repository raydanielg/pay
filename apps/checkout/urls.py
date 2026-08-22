from django.urls import path
from .views import CheckoutCreateView, CheckoutDetailView

urlpatterns = [
    path("checkout/", CheckoutCreateView.as_view(), name="checkout-create"),
    path("checkout/<str:reference>/", CheckoutDetailView.as_view(), name="checkout-detail"),
]
