from django.contrib import admin
from apps.payment_links.models import PaymentLink


@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    list_display = ("link_code", "business", "title", "amount", "currency", "status", "use_count", "created_at")
    list_filter = ("status", "currency", "is_single_use")
    search_fields = ("link_code", "title", "business__name")
    readonly_fields = ("uuid", "link_code", "use_count", "created_at", "updated_at")
    ordering = ["-created_at"]
