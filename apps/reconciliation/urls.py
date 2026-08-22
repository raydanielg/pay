from django.urls import path
from .views import (
    ReconciliationBatchListView, ReconciliationBatchDetailView,
    ReconciliationRecordListView,
)

urlpatterns = [
    path("reconciliation/batches/", ReconciliationBatchListView.as_view(), name="reconciliation-batch-list"),
    path("reconciliation/batches/<uuid:uuid>/", ReconciliationBatchDetailView.as_view(), name="reconciliation-batch-detail"),
    path("reconciliation/batches/<uuid:batch_uuid>/records/", ReconciliationRecordListView.as_view(), name="reconciliation-record-list"),
]
