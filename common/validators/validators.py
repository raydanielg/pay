"""
Custom validators for phone numbers, currency, and reference formats.
"""
import re
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.conf import settings


def validate_phone_number(value):
    """Validates Tanzanian/East African phone numbers."""
    pattern = r"^\+?(\d{9,15})$"
    if not re.match(pattern, value):
        raise ValidationError(
            "Invalid phone number format. Use international format e.g. +255712345678"
        )


def validate_currency(value):
    """Ensures currency is in the supported list."""
    if value not in settings.SUPPORTED_CURRENCIES:
        raise ValidationError(
            f"Currency '{value}' is not supported. Supported: {', '.join(settings.SUPPORTED_CURRENCIES)}"
        )


def validate_amount(value):
    """Ensures amount is positive and within reasonable bounds."""
    if value <= 0:
        raise ValidationError("Amount must be greater than zero.")
    if value > Decimal("999999999999.99"):
        raise ValidationError("Amount exceeds maximum allowed value.")


def validate_reference(value):
    """Validates reference format — alphanumeric with hyphens."""
    if not re.match(r"^[A-Za-z0-9\-_]+$", value):
        raise ValidationError(
            "Reference can only contain letters, numbers, hyphens, and underscores."
        )
