"""
Developer Platform models — API request logs, rate limiting tracking, and sandbox data.

APIRequestLog records every API call for debugging, auditing, and analytics.
RateLimitTracker tracks per-key request counts for rate limiting.
"""
import uuid

from django.db import models
from django.conf import settings

from common.constants.statuses import Environment


class APIRequestLog(models.Model):
    """
    Logs every API request for debugging, auditing, and analytics.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    request_id = models.CharField(max_length=100, unique=True, db_index=True, help_text="Unique request identifier")
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="api_request_logs",
    )
    api_key = models.ForeignKey(
        "accounts.APIKey",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_logs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="api_request_logs",
    )

    # Request details
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    query_params = models.JSONField(default=dict, blank=True)
    request_body = models.JSONField(default=dict, blank=True)
    request_headers = models.JSONField(default=dict, blank=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")

    # Response details
    status_code = models.IntegerField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True, help_text="Response time in milliseconds")
    response_body = models.JSONField(default=dict, blank=True)

    environment = models.CharField(
        max_length=20,
        choices=Environment.choices,
        default=Environment.PRODUCTION,
    )

    error_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "-created_at"]),
            models.Index(fields=["api_key", "-created_at"]),
            models.Index(fields=["request_id"]),
            models.Index(fields=["path", "method"]),
            models.Index(fields=["status_code"]),
        ]

    def __str__(self):
        return f"{self.request_id} — {self.method} {self.path} ({self.status_code})"


class RateLimitTracker(models.Model):
    """
    Tracks API request counts per key for rate limiting.
    Uses a sliding window approach.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    identifier = models.CharField(max_length=200, db_index=True, help_text="API key hash, user ID, or IP")
    window_start = models.DateTimeField()
    request_count = models.IntegerField(default=0)
    request_limit = models.IntegerField(default=1000, help_text="Max requests per window")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["identifier", "window_start"]),
        ]

    def __str__(self):
        return f"{self.identifier} — {self.request_count}/{self.request_limit}"

    @property
    def is_exceeded(self):
        return self.request_count >= self.request_limit
