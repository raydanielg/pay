"""
Transaction model — the core record of every financial movement.

A transaction has a lifecycle (pending → processing → success/failed/etc).
Each transaction links to:
- The business it belongs to
- The wallet it affects
- The customer (optional)
- The provider reference (e.g. Selcom)
- The ledger transaction(s) that record the double-entry

IMPORTANT: Transaction status changes should go through TransactionService
to ensure ledger entries are created/reversed appropriately.
"""
import uuid
from decimal import Decimal

from django.db import models

from common.constants.statuses import TransactionStatus, TransactionType, Currency


class Transaction(models.Model):
    """
    The central transaction record for all financial movements.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    reference = models.CharField(max_length=100, unique=True, db_index=True, help_text="Internal reference e.g. SP-TXN-20260822-00009281")
    external_reference = models.CharField(max_length=100, blank=True, default="", db_index=True, help_text="Business's own reference e.g. ORDER-92882")
    provider_reference = models.CharField(max_length=100, blank=True, default="", db_index=True, help_text="Provider's reference e.g. SEL-XXXXXXXX")

    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    customer = models.ForeignKey(
        "transactions.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    amount = models.DecimalField(max_digits=18, decimal_places=2, help_text="Gross amount")
    fee = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), help_text="Total fee charged")
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), help_text="Amount after fees")
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )

    type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.PAYMENT,
    )
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )

    # Provider info
    provider = models.CharField(max_length=50, blank=True, default="", help_text="e.g. selcom")
    provider_metadata = models.JSONField(default=dict, blank=True, help_text="Provider-specific data")

    # Additional context
    description = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True, help_text="Business-provided metadata")
    failure_reason = models.TextField(blank=True, default="")

    # Idempotency
    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, help_text="Client-provided key to prevent duplicates")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "status"]),
            models.Index(fields=["reference"]),
            models.Index(fields=["external_reference"]),
            models.Index(fields=["provider_reference"]),
            models.Index(fields=["idempotency_key"]),
            models.Index(fields=["type", "status"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.amount} {self.currency} ({self.status})"

    @property
    def is_successful(self):
        return self.status == TransactionStatus.SUCCESS

    @property
    def is_terminal(self):
        """Terminal states cannot be changed."""
        return self.status in [
            TransactionStatus.SUCCESS,
            TransactionStatus.FAILED,
            TransactionStatus.CANCELLED,
            TransactionStatus.REFUNDED,
        ]


class Customer(models.Model):
    """
    A business's customer — not necessarily a SalamaPay user.
    Businesses use this to track payment history per customer.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="customers",
    )
    name = models.CharField(max_length=200, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    external_customer_id = models.CharField(max_length=100, blank=True, default="", help_text="Business's own customer ID")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("business", "external_customer_id")]
        indexes = [
            models.Index(fields=["business", "phone"]),
            models.Index(fields=["business", "email"]),
        ]

    def __str__(self):
        return f"{self.name or self.phone or self.email} — {self.business.name}"
