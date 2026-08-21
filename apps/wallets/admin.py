from django.contrib import admin

from apps.wallets.models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("business", "currency", "status", "available_balance", "pending_balance", "locked_balance", "total_balance", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("business__name",)
    readonly_fields = ("uuid", "available_balance", "pending_balance", "locked_balance", "created_at", "updated_at")
    ordering = ("-created_at",)
