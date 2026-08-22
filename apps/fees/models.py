"""
Fee model — configurable fee rules per business, transaction type, and provider.

Fees are NEVER hard-coded in business logic. All fee calculations go through
FeeService.calculate() which looks up the applicable FeeRule.
"""
import uuid
from decimal import Decimal

from django.db import models

from common.constants.statuses import FeeType, FeePayer, TransactionType, Currency


class FeeRule(models.Model):
    """
    A configurable fee rule.

    The fee for a transaction is calculated as:
        fee = max(minimum_fee, min(maximum_fee, amount * percentage + fixed_amount))

    Multiple fee rules can apply to a single transaction (platform fee + provider fee).
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="fee_rules",
        null=True,
        blank=True,
        help_text="If null, this rule applies to all businesses (default rule)",
    )
    fee_type = models.CharField(
        max_length=20,
        choices=FeeType.choices,
        default=FeeType.PLATFORM,
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.PAYMENT,
    )
    provider = models.CharField(max_length=50, blank=True, default="", help_text="e.g. selcom. If blank, applies to all providers.")
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )

    # Fee calculation parameters
    percentage = models.DecimalField(
        max_digits=6, decimal_places=4, default=Decimal("0.0000"),
        help_text="Percentage of the transaction amount (e.g. 0.0190 = 1.9%)",
    )
    fixed_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00"),
        help_text="Fixed fee amount added to the percentage",
    )
    minimum_fee = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00"),
        help_text="Minimum fee that will be charged",
    )
    maximum_fee = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00"),
        help_text="Maximum fee cap. 0 means no cap.",
    )

    payer = models.CharField(
        max_length=20,
        choices=FeePayer.choices,
        default=FeePayer.BUSINESS,
        help_text="Who pays the fee",
    )

    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority rules are evaluated first")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "-created_at"]
        indexes = [
            models.Index(fields=["business", "transaction_type", "is_active"]),
            models.Index(fields=["fee_type", "is_active"]),
            models.Index(fields=["provider", "transaction_type"]),
        ]

    def __str__(self):
        biz = self.business.name if self.business else "GLOBAL"
        return f"{self.fee_type} — {biz} — {self.transaction_type} ({self.percentage}% + {self.fixed_amount})"

    def calculate(self, amount: Decimal) -> Decimal:
        """
        Calculates the fee for a given amount.
        fee = max(minimum_fee, min(maximum_fee, amount * percentage + fixed_amount))
        """
        fee = (amount * self.percentage) + self.fixed_amount

        if self.minimum_fee > 0 and fee < self.minimum_fee:
            fee = self.minimum_fee

        if self.maximum_fee > 0 and fee > self.maximum_fee:
            fee = self.maximum_fee

        return fee.quantize(Decimal("0.01"))
