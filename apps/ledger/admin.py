from django.contrib import admin

from apps.ledger.models import LedgerAccount, LedgerTransaction, LedgerEntry


@admin.register(LedgerAccount)
class LedgerAccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "account_type", "currency", "wallet", "is_system", "is_active", "created_at")
    list_filter = ("account_type", "currency", "is_system", "is_active")
    search_fields = ("code", "name")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("code",)


@admin.register(LedgerTransaction)
class LedgerTransactionAdmin(admin.ModelAdmin):
    list_display = ("reference", "currency", "status", "is_balanced", "total_amount", "posted_at", "reversed_at")
    list_filter = ("status", "currency")
    search_fields = ("reference", "description")
    readonly_fields = ("uuid", "reference", "posted_by", "posted_at", "reversed_at", "reversal_of", "created_at", "updated_at")
    ordering = ("-posted_at",)


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("ledger_transaction", "account", "entry_type", "amount", "currency", "created_at")
    list_filter = ("entry_type", "currency")
    search_fields = ("ledger_transaction__reference", "account__code")
    readonly_fields = ("uuid", "ledger_transaction", "account", "entry_type", "amount", "currency", "description", "created_at")
    ordering = ("-created_at",)
