"""
Business and BusinessMember models.
A user can own multiple businesses. Each business has its own wallet, API keys, etc.
"""
import uuid

from django.db import models
from django.conf import settings

from common.constants.statuses import BusinessStatus, KYCStatus, Currency


class Business(models.Model):
    """
    A business entity that uses SalamaPay as a payment gateway.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="businesses",
    )
    name = models.CharField(max_length=200, db_index=True)
    legal_name = models.CharField(max_length=300, blank=True, default="")
    registration_number = models.CharField(max_length=100, blank=True, default="")
    tin = models.CharField(max_length=50, blank=True, default="", help_text="Tax Identification Number")
    country = models.CharField(max_length=50, default="Tanzania")
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.TZS,
    )
    status = models.CharField(
        max_length=20,
        choices=BusinessStatus.choices,
        default=BusinessStatus.PENDING,
    )
    kyc_status = models.CharField(
        max_length=20,
        choices=KYCStatus.choices,
        default=KYCStatus.NOT_STARTED,
    )
    website = models.URLField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    logo = models.ImageField(upload_to="business_logos/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["kyc_status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def is_kyc_verified(self):
        return self.kyc_status == KYCStatus.VERIFIED

    @property
    def can_receive_payments(self):
        return self.status == BusinessStatus.ACTIVE and self.is_kyc_verified


class BusinessMember(models.Model):
    """
    Members/employees of a business with role-based access.
    """
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        DEVELOPER = "developer", "Developer"
        FINANCE = "finance", "Finance"
        SUPPORT = "support", "Support"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DEVELOPER,
    )
    is_active = models.BooleanField(default=True)
    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("business", "user")]
        indexes = [
            models.Index(fields=["business", "role"]),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.role} @ {self.business.name}"
