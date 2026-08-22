from django.contrib import admin
from apps.withdrawals.models import Withdrawal


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ("reference", "business", "amount", "currency", "status", "type", "approval_tier", "created_by", "created_at")
    list_filter = ("status", "type", "approval_tier", "currency")
    search_fields = ("reference", "provider_reference", "destination_account")
    readonly_fields = ("uuid", "reference", "created_at", "updated_at", "approved_at", "processed_at", "completed_at")
    ordering = ["-created_at"]
