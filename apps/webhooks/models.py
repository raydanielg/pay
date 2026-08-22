"""
Webhook model — manages webhook endpoints and delivery tracking.

Businesses register webhook endpoints to receive event notifications.
When an event occurs (payment.success, withdrawal.failed, etc.),
SalamaPay sends an HTTP POST to each registered endpoint.

Includes retry logic with exponential backoff.
"""
import uuid
import hashlib
import hmac
import json

from django.db import models
from django.conf import settings

from common.constants.statuses import WebhookStatus, Environment


class WebhookEndpoint(models.Model):
    """
    A business's webhook endpoint configuration.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="webhook_endpoints",
    )
    url = models.URLField(help_text="HTTPS endpoint to receive webhooks")
    secret = models.CharField(max_length=128, help_text="Used to sign webhook payloads")

    # Which events to send
    events = models.JSONField(default=list, help_text="List of event types e.g. ['payment.success', 'withdrawal.failed']")
    is_active = models.BooleanField(default=True)

    environment = models.CharField(
        max_length=20,
        choices=Environment.choices,
        default=Environment.PRODUCTION,
    )

    # Retry config
    max_retries = models.IntegerField(default=5)
    retry_interval_seconds = models.IntegerField(default=60, help_text="Base interval for exponential backoff")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "is_active"]),
        ]

    def __str__(self):
        return f"{self.business.name} — {self.url}"

    def should_receive(self, event_type):
        if not self.is_active:
            return False
        if not self.events:
            return True  # If no events specified, receive all
        return event_type in self.events

    def sign_payload(self, payload: str) -> str:
        """Generate HMAC-SHA256 signature for the payload."""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()


class WebhookEvent(models.Model):
    """
    A webhook event to be delivered to endpoints.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    event_type = models.CharField(max_length=50, db_index=True, help_text="e.g. payment.success")
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="webhook_events",
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="webhook_events",
    )

    payload = models.JSONField(default=dict, help_text="The event data sent to the endpoint")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "event_type"]),
            models.Index(fields=["event_type"]),
        ]

    def __str__(self):
        return f"{self.event_type} — {self.business.name}"


class WebhookDelivery(models.Model):
    """
    Tracks each delivery attempt of a webhook event to an endpoint.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    event = models.ForeignKey(
        WebhookEvent,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    endpoint = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )

    status = models.CharField(
        max_length=20,
        choices=WebhookStatus.choices,
        default=WebhookStatus.PENDING,
    )

    attempt_count = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)

    # Response info
    response_status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True, default="")
    response_headers = models.JSONField(default=dict, blank=True)

    # Signature sent
    signature = models.CharField(max_length=128, blank=True, default="")

    error_message = models.TextField(blank=True, default="")

    next_retry_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "next_retry_at"]),
            models.Index(fields=["endpoint", "status"]),
        ]

    def __str__(self):
        return f"{self.event.event_type} → {self.endpoint.url} ({self.status})"

    @property
    def should_retry(self):
        return (
            self.status in [WebhookStatus.FAILED, WebhookStatus.RETRYING]
            and self.attempt_count < self.max_attempts
        )
