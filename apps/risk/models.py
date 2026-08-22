"""
Risk & Fraud models — transaction limits, velocity checks, blacklists, and risk events.

RiskRules define configurable thresholds that trigger risk checks.
RiskEvents log suspicious activity for review.
Blacklists prevent transactions from flagged entities.
"""
import uuid

from django.db import models
from django.conf import settings

from common.constants.statuses import RiskLevel, RiskEventType, BlacklistType, Currency


class RiskRule(models.Model):
    """
    A configurable risk rule that triggers on certain conditions.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    # Condition
    rule_type = models.CharField(max_length=50, help_text="e.g. velocity_check, amount_threshold, time_window")
    parameters = models.JSONField(default=dict, help_text="Rule-specific parameters")

    # Action
    action = models.CharField(max_length=50, default="flag", help_text="flag, block, manual_review")
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.MEDIUM,
    )

    # Scope
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="risk_rules",
        help_text="If null, applies to all businesses",
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )

    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "-created_at"]
        indexes = [
            models.Index(fields=["business", "is_active"]),
            models.Index(fields=["rule_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.rule_type}) — {self.risk_level}"


class RiskEvent(models.Model):
    """
    A triggered risk event — logged for review and action.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="risk_events",
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="risk_events",
    )
    risk_rule = models.ForeignKey(
        RiskRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    event_type = models.CharField(
        max_length=50,
        choices=RiskEventType.choices,
        default=RiskEventType.MANUAL_REVIEW,
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.MEDIUM,
    )
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100 risk score")

    description = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_risk_events",
    )
    resolution = models.TextField(blank=True, default="")
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "is_resolved"]),
            models.Index(fields=["risk_level", "is_resolved"]),
        ]

    def __str__(self):
        return f"{self.event_type} — {self.business.name} ({self.risk_level})"


class BlacklistEntry(models.Model):
    """
    A blacklisted entity (phone, email, account, IP).
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="blacklist_entries",
        help_text="If null, global blacklist",
    )
    entry_type = models.CharField(
        max_length=20,
        choices=BlacklistType.choices,
    )
    value = models.CharField(max_length=200, db_index=True, help_text="The phone, email, account, or IP to block")
    reason = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blacklist_entries_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entry_type", "value", "is_active"]),
            models.Index(fields=["business", "is_active"]),
        ]

    def __str__(self):
        return f"{self.entry_type}: {self.value} ({'active' if self.is_active else 'inactive'})"
