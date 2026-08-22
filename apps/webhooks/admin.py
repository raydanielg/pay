from django.contrib import admin
from apps.webhooks.models import WebhookEndpoint, WebhookEvent, WebhookDelivery


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("business", "url", "is_active", "environment", "created_at")
    list_filter = ("is_active", "environment")
    search_fields = ("url", "business__name")
    readonly_fields = ("uuid", "secret", "created_at", "updated_at")
    ordering = ["-created_at"]


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "business", "created_at")
    list_filter = ("event_type",)
    search_fields = ("event_type", "business__name")
    readonly_fields = ("uuid", "created_at")
    ordering = ["-created_at"]


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("event", "endpoint", "status", "attempt_count", "created_at")
    list_filter = ("status",)
    search_fields = ("endpoint__url",)
    readonly_fields = ("uuid", "created_at", "updated_at", "delivered_at")
    ordering = ["-created_at"]
