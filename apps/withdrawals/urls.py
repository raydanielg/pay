from django.urls import path
from .views import (
    WithdrawalListView, WithdrawalDetailView,
    WithdrawalApproveView, WithdrawalRejectView,
)

urlpatterns = [
    path("withdrawals/", WithdrawalListView.as_view(), name="withdrawal-list"),
    path("withdrawals/<uuid:uuid>/", WithdrawalDetailView.as_view(), name="withdrawal-detail"),
    path("withdrawals/<uuid:uuid>/approve/", WithdrawalApproveView.as_view(), name="withdrawal-approve"),
    path("withdrawals/<uuid:uuid>/reject/", WithdrawalRejectView.as_view(), name="withdrawal-reject"),
]
