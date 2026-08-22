from django.contrib import admin
from apps.qr_payments.models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "business", "type", "status", "amount", "currency", "scan_count", "created_at")
    list_filter = ("type", "status", "currency")
    search_fields = ("code", "business__name")
    readonly_fields = ("uuid", "code", "scan_count", "created_at", "updated_at")
    ordering = ["-created_at"]
