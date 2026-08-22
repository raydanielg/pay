from django.urls import path
from .views import (
    RefundListView, RefundDetailView,
    RefundApproveView, RefundRejectView,
)

urlpatterns = [
    path("refunds/", RefundListView.as_view(), name="refund-list"),
    path("refunds/<uuid:uuid>/", RefundDetailView.as_view(), name="refund-detail"),
    path("refunds/<uuid:uuid>/approve/", RefundApproveView.as_view(), name="refund-approve"),
    path("refunds/<uuid:uuid>/reject/", RefundRejectView.as_view(), name="refund-reject"),
]
