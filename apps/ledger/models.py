"""
Double-entry ledger models.

The ledger is the SOURCE OF TRUTH for all financial movements.
Wallet balances are projections derived from ledger entries.

Key rules:
1. Every LedgerTransaction has at least 2 LedgerEntry records.
2. Total debits MUST equal total credits for each transaction.
3. Entries are immutable once posted — corrections are reversal transactions.
4. Each entry references a LedgerAccount (chart of accounts).
"""
import uuid
from decimal import Decimal

from django.db import models
from django.conf import settings

from common.constants.statuses import LedgerEntryType, LedgerAccountType, Currency


class LedgerAccount(models.Model):
    """
    Chart of accounts — each wallet, fee account, clearing account, etc.
    has its own ledger account.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True, help_text="e.g. WALLET-BIZ-001, FEE-PLATFORM, CLEARING-MNO")
    name = models.CharField(max_length=200)
    account_type = models.CharField(
        max_length=20,
        choices=LedgerAccountType.choices,
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )
    # Link to wallet if this is a wallet account
    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_accounts",
    )
    is_system = models.BooleanField(default=False, help_text="System accounts like clearing, fee accounts")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code", "is_active"]),
            models.Index(fields=["account_type"]),
        ]

    def __str__(self):
        return f"{self.code} — {self.name} ({self.account_type})"

    @property
    def balance(self):
        """Calculate current balance from entries."""
        debits = self.entries.filter(entry_type=LedgerEntryType.DEBIT).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")
        credits = self.entries.filter(entry_type=LedgerEntryType.CREDIT).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")

        # For asset/expense accounts, debit increases balance
        if self.account_type in [LedgerAccountType.ASSET, LedgerAccountType.EXPENSE]:
            return debits - credits
        # For liability/equity/revenue accounts, credit increases balance
        return credits - debits


class LedgerTransaction(models.Model):
    """
    A single financial event that contains balanced debit/credit entries.
    This is immutable once posted.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    reference = models.CharField(max_length=100, unique=True, db_index=True, help_text="Human-readable reference e.g. SP-LED-20260822-00009281")
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ledger_transactions",
        help_text="Link to the business transaction that triggered this ledger entry",
    )
    description = models.TextField(blank=True, default="")
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )
    status = models.CharField(
        max_length=20,
        choices=[("posted", "Posted"), ("reversed", "Reversed")],
        default="posted",
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posted_ledger_transactions",
    )
    posted_at = models.DateTimeField(auto_now_add=True)
    reversed_at = models.DateTimeField(null=True, blank=True)
    reversal_of = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reversals",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.reference} ({self.status})"

    @property
    def is_balanced(self):
        """Verify that total debits equal total credits."""
        debits = self.entries.filter(entry_type=LedgerEntryType.DEBIT).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")
        credits = self.entries.filter(entry_type=LedgerEntryType.CREDIT).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")
        return debits == credits

    @property
    def total_amount(self):
        """The total value being moved (debit side or credit side, they're equal)."""
        return self.entries.filter(entry_type=LedgerEntryType.DEBIT).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")


class LedgerEntry(models.Model):
    """
    A single debit or credit entry within a ledger transaction.
    Immutable once created.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    ledger_transaction = models.ForeignKey(
        LedgerTransaction,
        on_delete=models.PROTECT,
        related_name="entries",
    )
    account = models.ForeignKey(
        LedgerAccount,
        on_delete=models.PROTECT,
        related_name="entries",
    )
    entry_type = models.CharField(
        max_length=10,
        choices=LedgerEntryType.choices,
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["account", "entry_type"]),
            models.Index(fields=["ledger_transaction"]),
        ]

    def __str__(self):
        return f"{self.entry_type} {self.amount} {self.currency} — {self.account.code}"

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Ledger entries are immutable and cannot be modified.")
        super().save(*args, **kwargs)
