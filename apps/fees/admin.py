from django.contrib import admin

from apps.fees.models import FeeRule


@admin.register(FeeRule)
class FeeRuleAdmin(admin.ModelAdmin):
    list_display = ("fee_type", "business", "transaction_type", "provider", "currency", "percentage", "fixed_amount", "minimum_fee", "maximum_fee", "payer", "is_active", "priority")
    list_filter = ("fee_type", "transaction_type", "currency", "payer", "is_active")
    search_fields = ("business__name", "provider")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-priority", "-created_at")
