from django.contrib import admin
from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "notification_type", "status", "recipient_user", "business", "is_read", "created_at")
    list_filter = ("notification_type", "status", "is_read")
    search_fields = ("title", "message", "phone", "email")
    readonly_fields = ("uuid", "created_at", "updated_at", "sent_at", "delivered_at")
    ordering = ["-created_at"]
