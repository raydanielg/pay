"""
Refund model — handles full and partial refunds for transactions.

Refunds go through an approval workflow similar to withdrawals.
A refund reverses a previously successful payment, crediting the customer
and debiting the business wallet.
"""
import uuid
from decimal import Decimal

from django.db import models
from django.conf import settings

from common.constants.statuses import RefundStatus, RefundType, Currency


class Refund(models.Model):
    """
    A refund request for a previously successful transaction.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    reference = models.CharField(max_length=100, unique=True, db_index=True, help_text="Internal reference e.g. SP-RFD-20260822-00001")
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.PROTECT,
        related_name="refunds",
        help_text="The original transaction being refunded",
    )
    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.PROTECT,
        related_name="refunds",
    )

    amount = models.DecimalField(max_digits=18, decimal_places=2, help_text="Refund amount (may be partial)")
    fee = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )

    type = models.CharField(
        max_length=10,
        choices=RefundType.choices,
        default=RefundType.FULL,
    )
    status = models.CharField(
        max_length=20,
        choices=RefundStatus.choices,
        default=RefundStatus.PENDING,
    )

    reason = models.TextField(help_text="Why the refund is being requested")
    rejection_reason = models.TextField(blank=True, default="")

    # Provider info
    provider = models.CharField(max_length=50, blank=True, default="")
    provider_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    provider_metadata = models.JSONField(default=dict, blank=True)

    # Maker-checker
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="refunds_created",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds_approved",
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds_rejected",
    )

    metadata = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "status"]),
            models.Index(fields=["reference"]),
            models.Index(fields=["transaction", "status"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.amount} {self.currency} ({self.status})"

    @property
    def is_full_refund(self):
        return self.type == RefundType.FULL

    @property
    def is_pending(self):
        return self.status in [RefundStatus.PENDING, RefundStatus.APPROVED, RefundStatus.PROCESSING]

    @property
    def is_terminal(self):
        return self.status in [RefundStatus.SUCCESS, RefundStatus.FAILED, RefundStatus.CANCELLED, RefundStatus.REJECTED]
