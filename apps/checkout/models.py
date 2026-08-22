"""
Checkout model — hosted checkout sessions for businesses.

A checkout session is created when a business wants to collect payment
from a customer via a hosted page. The customer is redirected to the
checkout URL, selects a payment method, and completes the payment.
"""
import uuid

from django.db import models

from common.constants.statuses import CheckoutStatus, Currency, PaymentMethod


class CheckoutSession(models.Model):
    """
    A hosted checkout session for collecting payments.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    reference = models.CharField(max_length=100, unique=True, db_index=True, help_text="e.g. SP-CHK-20260822-00001")
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="checkout_sessions",
    )
    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checkout_sessions",
    )

    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )
    status = models.CharField(
        max_length=20,
        choices=CheckoutStatus.choices,
        default=CheckoutStatus.OPEN,
    )

    # Customer details
    customer_name = models.CharField(max_length=200, blank=True, default="")
    customer_email = models.EmailField(blank=True, default="")
    customer_phone = models.CharField(max_length=20, blank=True, default="")

    # Checkout config
    title = models.CharField(max_length=200, blank=True, default="", help_text="Checkout page title")
    description = models.TextField(blank=True, default="")
    success_url = models.URLField(blank=True, default="")
    cancel_url = models.URLField(blank=True, default="")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When the checkout session expires")

    # Allowed payment methods
    allowed_methods = models.JSONField(default=list, blank=True, help_text="List of PaymentMethod values allowed")

    # Branding
    logo_url = models.URLField(blank=True, default="")
    brand_color = models.CharField(max_length=20, blank=True, default="")

    # Selected method after customer chooses
    selected_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        blank=True,
        default="",
    )

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "status"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.amount} {self.currency} ({self.status})"

    @property
    def is_open(self):
        return self.status == CheckoutStatus.OPEN

    @property
    def checkout_url(self):
        return f"https://pay.salamapay.co.tz/checkout/{self.reference}"
