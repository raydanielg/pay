from django.contrib import admin
from apps.refunds.models import Refund


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("reference", "business", "amount", "currency", "status", "type", "created_by", "created_at")
    list_filter = ("status", "type", "currency")
    search_fields = ("reference", "provider_reference", "transaction__reference")
    readonly_fields = ("uuid", "reference", "created_at", "updated_at", "approved_at", "processed_at", "completed_at")
    ordering = ["-created_at"]
