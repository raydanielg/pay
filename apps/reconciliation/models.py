"""
Reconciliation models — compare SalamaPay transactions with provider (Selcom) records.

Reconciliation runs in batches. Each batch fetches transactions for a date range,
fetches the corresponding provider records, and matches them.

Matched: Both SalamaPay and provider agree on the transaction.
Unmatched: Transaction exists in one system but not the other.
Flagged: Amount mismatch or status mismatch.
"""
import uuid

from django.db import models
from django.conf import settings

from common.constants.statuses import ReconciliationStatus, ReconciliationBatchStatus, Currency


class ReconciliationBatch(models.Model):
    """
    A batch reconciliation run for a specific date range.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    batch_reference = models.CharField(max_length=100, unique=True, db_index=True, help_text="e.g. SP-REC-20260822-001")
    provider = models.CharField(max_length=50, default="selcom")

    status = models.CharField(
        max_length=20,
        choices=ReconciliationBatchStatus.choices,
        default=ReconciliationBatchStatus.PENDING,
    )

    date_from = models.DateField()
    date_to = models.DateField()
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )

    # Summary stats
    total_salama_records = models.IntegerField(default=0)
    total_provider_records = models.IntegerField(default=0)
    matched_count = models.IntegerField(default=0)
    unmatched_count = models.IntegerField(default=0)
    flagged_count = models.IntegerField(default=0)
    total_matched_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_unmatched_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reconciliation_batches",
    )

    error_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["provider", "status"]),
            models.Index(fields=["date_from", "date_to"]),
        ]

    def __str__(self):
        return f"{self.batch_reference} — {self.provider} ({self.status})"


class ReconciliationRecord(models.Model):
    """
    A single reconciliation comparison between a SalamaPay transaction and a provider record.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    batch = models.ForeignKey(
        ReconciliationBatch,
        on_delete=models.CASCADE,
        related_name="records",
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reconciliation_records",
    )

    status = models.CharField(
        max_length=20,
        choices=ReconciliationStatus.choices,
        default=ReconciliationStatus.UNMATCHED,
    )

    # SalamaPay side
    salama_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    salama_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    salama_status = models.CharField(max_length=20, blank=True, default="")

    # Provider side
    provider_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    provider_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    provider_status = models.CharField(max_length=20, blank=True, default="")

    # Mismatch details
    mismatch_type = models.CharField(max_length=50, blank=True, default="", help_text="amount_mismatch, status_mismatch, missing_in_provider, missing_in_salama")
    mismatch_details = models.TextField(blank=True, default="")

    # Resolution
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_reconciliation_records",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["batch", "status"]),
            models.Index(fields=["salama_reference"]),
            models.Index(fields=["provider_reference"]),
        ]

    def __str__(self):
        return f"{self.batch.batch_reference} — {self.salama_reference} ({self.status})"
