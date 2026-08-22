from django.urls import path
from .views import QRCodeListView, QRCodeDetailView

urlpatterns = [
    path("qr-codes/", QRCodeListView.as_view(), name="qr-code-list"),
    path("qr-codes/<uuid:uuid>/", QRCodeDetailView.as_view(), name="qr-code-detail"),
]
