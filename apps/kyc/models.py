"""
KYC models — applications and documents for verification.
KYC status determines what wallet operations are permitted.
"""
import uuid

from django.db import models
from django.conf import settings

from common.constants.statuses import KYCStatus, KYCType


class KYCApplication(models.Model):
    """
    A KYC submission from a business or individual.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="kyc_applications",
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kyc_applications",
    )
    type = models.CharField(
        max_length=20,
        choices=KYCType.choices,
        default=KYCType.BUSINESS,
    )
    status = models.CharField(
        max_length=20,
        choices=KYCStatus.choices,
        default=KYCStatus.PENDING,
    )
    rejection_reason = models.TextField(blank=True, default="")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kyc_reviews",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "status"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"KYC {self.business.name} — {self.status}"

    @property
    def is_verified(self):
        return self.status == KYCStatus.VERIFIED


class KYCDocument(models.Model):
    """
    Individual documents submitted as part of a KYC application.
    """
    class DocumentType(models.TextChoices):
        NATIONAL_ID = "national_id", "National ID"
        PASSPORT = "passport", "Passport"
        SELFIE = "selfie", "Selfie"
        BUSINESS_CERTIFICATE = "business_certificate", "Business Certificate"
        TIN_CERTIFICATE = "tin_certificate", "TIN Certificate"
        BUSINESS_LICENSE = "business_license", "Business License"
        BANK_STATEMENT = "bank_statement", "Bank Statement"
        UTILITY_BILL = "utility_bill", "Utility Bill"
        DIRECTOR_ID = "director_id", "Director ID"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    kyc_application = models.ForeignKey(
        KYCApplication,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
    )
    document_number = models.CharField(max_length=100, blank=True, default="")
    file = models.FileField(upload_to="kyc_documents/")
    status = models.CharField(
        max_length=20,
        choices=KYCStatus.choices,
        default=KYCStatus.PENDING,
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.document_type} — {self.kyc_application.business.name}"
