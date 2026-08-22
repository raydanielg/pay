from django.contrib import admin
from apps.reconciliation.models import ReconciliationBatch, ReconciliationRecord


@admin.register(ReconciliationBatch)
class ReconciliationBatchAdmin(admin.ModelAdmin):
    list_display = ("batch_reference", "provider", "status", "date_from", "date_to", "matched_count", "unmatched_count", "flagged_count", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("batch_reference",)
    readonly_fields = ("uuid", "batch_reference", "created_at", "updated_at", "completed_at")
    ordering = ["-created_at"]


@admin.register(ReconciliationRecord)
class ReconciliationRecordAdmin(admin.ModelAdmin):
    list_display = ("batch", "status", "salama_reference", "provider_reference", "mismatch_type", "created_at")
    list_filter = ("status", "mismatch_type")
    search_fields = ("salama_reference", "provider_reference")
    readonly_fields = ("uuid", "created_at", "updated_at", "resolved_at")
    ordering = ["-created_at"]
