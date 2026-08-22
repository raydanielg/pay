from django.contrib import admin

from apps.transactions.models import Transaction, Customer


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("reference", "business", "type", "status", "amount", "fee", "net_amount", "currency", "provider", "created_at", "completed_at")
    list_filter = ("status", "type", "currency", "provider")
    search_fields = ("reference", "external_reference", "provider_reference", "business__name")
    readonly_fields = ("uuid", "reference", "fee", "net_amount", "provider_metadata", "created_at", "updated_at", "completed_at")
    ordering = ("-created_at",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "business", "external_customer_id", "created_at")
    list_filter = ("business",)
    search_fields = ("name", "phone", "email", "external_customer_id", "business__name")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)
