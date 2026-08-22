"""
Payment Link model — shareable links that businesses create to collect payments.

A payment link can be reused (until disabled/expired) or single-use.
When a customer opens the link, a checkout session is created.
"""
import uuid
import secrets

from django.db import models

from common.constants.statuses import PaymentLinkStatus, Currency


class PaymentLink(models.Model):
    """
    A reusable or single-use payment link.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    link_code = models.CharField(max_length=20, unique=True, db_index=True, help_text="Short code in the URL")
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="payment_links",
    )

    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, help_text="Null means customer enters amount")
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )
    title = models.CharField(max_length=200, help_text="What the payment is for")
    description = models.TextField(blank=True, default="")

    status = models.CharField(
        max_length=20,
        choices=PaymentLinkStatus.choices,
        default=PaymentLinkStatus.ACTIVE,
    )

    is_single_use = models.BooleanField(default=False, help_text="If true, link becomes 'used' after one payment")
    max_uses = models.IntegerField(default=0, help_text="0 = unlimited")
    use_count = models.IntegerField(default=0)

    expires_at = models.DateTimeField(null=True, blank=True)

    # Tracking
    success_url = models.URLField(blank=True, default="")
    cancel_url = models.URLField(blank=True, default="")

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "status"]),
            models.Index(fields=["link_code"]),
        ]

    def __str__(self):
        return f"{self.link_code} — {self.title} ({self.status})"

    @property
    def url(self):
        return f"https://pay.salamapay.co.tz/pay/{self.link_code}"

    @property
    def is_available(self):
        if self.status != PaymentLinkStatus.ACTIVE:
            return False
        if self.is_single_use and self.use_count >= 1:
            return False
        if self.max_uses > 0 and self.use_count >= self.max_uses:
            return False
        return True

    def save(self, *args, **kwargs):
        if not self.link_code:
            self.link_code = secrets.token_urlsafe(8).upper()[:10]
        super().save(*args, **kwargs)
