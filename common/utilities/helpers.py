"""
Utility functions for the payment platform.
"""
import uuid
from datetime import datetime
from decimal import Decimal


def generate_reference(prefix="SP", type_code="TXN"):
    """
    Generates a human-readable reference.
    Format: SP-TXN-20260822-00009281
    """
    now = datetime.utcnow()
    date_str = now.strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{type_code}-{date_str}-{random_part}"


def generate_uuid():
    """Returns a new UUID4 as a string."""
    return str(uuid.uuid4())


def generate_api_key(environment="test"):
    """
    Generates an API key string.
    Format: sp_test_xxxxx or sp_live_xxxxx
    """
    prefix = "sp_live_" if environment == "production" else "sp_test_"
    return f"{prefix}{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"


def generate_api_secret():
    """Generates a secret key string."""
    return f"sp_secret_{uuid.uuid4().hex}{uuid.uuid4().hex}"


def hash_token(token):
    """SHA-256 hash a token for secure storage."""
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()


def mask_string(value, visible_start=4, visible_end=4):
    """Masks a string for safe display. e.g. sp_live_xxxx...xxxx"""
    if not value or len(value) <= visible_start + visible_end:
        return value
    return f"{value[:visible_start]}...{value[-visible_end:]}"


def decimal_to_cents(amount):
    """Converts a Decimal amount to integer cents."""
    return int((Decimal(str(amount)) * Decimal("100")).quantize(Decimal("1")))


def cents_to_decimal(cents):
    """Converts integer cents to Decimal amount."""
    return Decimal(str(cents)) / Decimal("100")
