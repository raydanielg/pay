"""
QR Code model — static and dynamic QR codes for payments.

Static QR: Fixed amount or open amount, reusable, tied to a business.
Dynamic QR: Generated per transaction, expires after a set time.
"""
import uuid
import secrets

from django.db import models

from common.constants.statuses import QRCodeType, QRCodeStatus, Currency


class QRCode(models.Model):
    """
    A QR code for accepting payments.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    code = models.CharField(max_length=20, unique=True, db_index=True, help_text="Short code encoded in the QR")
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="qr_codes",
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_codes",
        help_text="Linked transaction for dynamic QR codes",
    )

    type = models.CharField(
        max_length=10,
        choices=QRCodeType.choices,
        default=QRCodeType.STATIC,
    )
    status = models.CharField(
        max_length=20,
        choices=QRCodeStatus.choices,
        default=QRCodeStatus.ACTIVE,
    )

    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, help_text="Null for open-amount static QR")
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )
    title = models.CharField(max_length=200, blank=True, default="")

    # QR image data (base64 or URL)
    qr_image_url = models.URLField(blank=True, default="")
    qr_data = models.TextField(blank=True, default="", help_text="Raw data encoded in the QR")

    expires_at = models.DateTimeField(null=True, blank=True, help_text="For dynamic QR codes")
    scan_count = models.IntegerField(default=0)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "status"]),
            models.Index(fields=["code"]),
            models.Index(fields=["type", "status"]),
        ]

    def __str__(self):
        return f"{self.code} — {self.business.name} ({self.type})"

    @property
    def is_active(self):
        return self.status == QRCodeStatus.ACTIVE

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = secrets.token_urlsafe(6).upper()[:8]
        super().save(*args, **kwargs)
