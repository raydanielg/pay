from django.contrib import admin
from apps.checkout.models import CheckoutSession


@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    list_display = ("reference", "business", "amount", "currency", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("reference", "customer_email", "customer_phone")
    readonly_fields = ("uuid", "reference", "created_at", "updated_at", "completed_at")
    ordering = ["-created_at"]
