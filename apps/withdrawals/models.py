"""
Withdrawal model — handles all withdrawal requests from businesses.

Withdrawals go through a maker-checker approval workflow:
1. Business member creates a withdrawal request (maker)
2. Based on amount tier, auto-approve or require manual approval
3. A different user (checker) approves/rejects the withdrawal
4. The withdrawal is sent to the provider (e.g. Selcom) for processing
5. Provider callback updates the withdrawal status

The maker-checker control is enforced by apps.rbac.services.MakerCheckerService.
"""
import uuid
from decimal import Decimal

from django.db import models
from django.conf import settings

from common.constants.statuses import (
    WithdrawalStatus,
    WithdrawalType,
    Currency,
    PaymentMethod,
)


class Withdrawal(models.Model):
    """
    A withdrawal request from a business wallet to an external destination.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    reference = models.CharField(max_length=100, unique=True, db_index=True, help_text="Internal reference e.g. SP-WDR-20260822-00001")
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.PROTECT,
        related_name="withdrawals",
    )
    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.PROTECT,
        related_name="withdrawals",
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="withdrawals",
        help_text="Linked transaction record",
    )

    amount = models.DecimalField(max_digits=18, decimal_places=2)
    fee = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), help_text="Amount after fees")
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )

    type = models.CharField(
        max_length=10,
        choices=WithdrawalType.choices,
        default=WithdrawalType.MANUAL,
    )
    status = models.CharField(
        max_length=20,
        choices=WithdrawalStatus.choices,
        default=WithdrawalStatus.PENDING,
    )

    # Destination info
    destination_type = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MOBILE_MONEY,
        help_text="Where the money is being sent",
    )
    destination_account = models.CharField(max_length=100, help_text="Phone number, bank account, etc.")
    destination_name = models.CharField(max_length=200, blank=True, default="")
    destination_metadata = models.JSONField(default=dict, blank=True, help_text="Bank name, branch, etc.")

    # Provider info
    provider = models.CharField(max_length=50, blank=True, default="", help_text="e.g. selcom")
    provider_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    provider_metadata = models.JSONField(default=dict, blank=True)

    # Maker-checker
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="withdrawals_created",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="withdrawals_approved",
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="withdrawals_rejected",
    )
    approval_tier = models.CharField(max_length=20, blank=True, default="", help_text="auto, officer, senior")
    approval_note = models.TextField(blank=True, default="")
    rejection_reason = models.TextField(blank=True, default="")

    # Retry tracking
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    last_retry_at = models.DateTimeField(null=True, blank=True)

    description = models.TextField(blank=True, default="")
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
            models.Index(fields=["provider_reference"]),
            models.Index(fields=["status", "type"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.amount} {self.currency} ({self.status})"

    @property
    def is_pending(self):
        return self.status in [WithdrawalStatus.PENDING, WithdrawalStatus.APPROVED, WithdrawalStatus.PROCESSING, WithdrawalStatus.RETRYING]

    @property
    def is_terminal(self):
        return self.status in [WithdrawalStatus.SUCCESS, WithdrawalStatus.FAILED, WithdrawalStatus.CANCELLED, WithdrawalStatus.REJECTED]

    @property
    def requires_approval(self):
        return self.status == WithdrawalStatus.PENDING and self.approval_tier != "auto"
