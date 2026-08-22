"""
Wallet model — the container for funds per business per currency.

IMPORTANT: `available_balance`, `pending_balance`, and `locked_balance`
are NOT the source of truth. They are projections derived from the ledger.
The ledger (apps.ledger) is the source of truth.

Balance updates must ONLY happen through the LedgerService, never directly.
"""
import uuid
from decimal import Decimal

from django.db import models

from common.constants.statuses import WalletStatus, Currency


class Wallet(models.Model):
    """
    A wallet holds funds for a business in a specific currency.
    Balances are projections from the ledger — never update directly.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="wallets",
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )
    label = models.CharField(max_length=100, blank=True, default="", help_text="Optional nickname for this wallet")
    status = models.CharField(
        max_length=20,
        choices=WalletStatus.choices,
        default=WalletStatus.PENDING,
    )
    available_balance = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00"),
    )
    pending_balance = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00"),
    )
    locked_balance = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("business", "currency")]
        indexes = [
            models.Index(fields=["business", "status"]),
        ]

    def __str__(self):
        return f"{self.business.name} — {self.currency} (avail: {self.available_balance})"

    @property
    def total_balance(self):
        return self.available_balance + self.pending_balance + self.locked_balance

    @property
    def is_active(self):
        return self.status == WalletStatus.ACTIVE

    @property
    def can_debit(self):
        """Check if wallet can be debited (active and has sufficient available balance)."""
        return self.is_active and self.available_balance > Decimal("0.00")
