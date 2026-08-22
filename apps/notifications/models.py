"""
Notification model — tracks all notifications sent to users and businesses.

Supports SMS, Email, In-App, and Webhook notification channels.
Each notification tracks its delivery status and retry attempts.
"""
import uuid

from django.db import models
from django.conf import settings

from common.constants.statuses import NotificationType, NotificationStatus


class Notification(models.Model):
    """
    A notification sent to a user or business.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.IN_APP,
    )
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )

    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    event_type = models.CharField(max_length=50, blank=True, default="", help_text="e.g. payment.success, withdrawal.failed")

    # Delivery targets
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")

    # Metadata for the event
    metadata = models.JSONField(default=dict, blank=True)

    # Delivery tracking
    provider_message_id = models.CharField(max_length=200, blank=True, default="", help_text="SMS/email provider message ID")
    attempt_count = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    error_message = models.TextField(blank=True, default="")

    # Read tracking for in-app
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient_user", "is_read"]),
            models.Index(fields=["business", "notification_type"]),
            models.Index(fields=["status", "notification_type"]),
        ]

    def __str__(self):
        return f"{self.notification_type} — {self.title} ({self.status})"
