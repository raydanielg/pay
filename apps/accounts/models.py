"""
Custom User model and API Key model for the SalamaPay payment gateway.
"""
import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from common.constants.statuses import UserStatus, UserType, Environment


class UserManager(BaseUserManager):
    """Custom manager that uses email instead of username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatus.ACTIVE)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("user_type", UserType.STAFF)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model supporting individuals, business owners, developers, and staff.
    Uses email as the primary identifier instead of username.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.INDIVIDUAL,
    )
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.PENDING,
    )
    is_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Remove username as login field — use email
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.user_type})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active_user(self):
        return self.status == UserStatus.ACTIVE and self.is_active


class APIKey(models.Model):
    """
    API credentials for business/developer API access.
    Keys are hashed — the plain text is only shown once at creation time.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(max_length=100, help_text="Label for this API key")
    key_prefix = models.CharField(max_length=20, db_index=True, help_text="First 12 chars for identification")
    key_hash = models.CharField(max_length=64, unique=True, db_index=True, help_text="SHA-256 hash of the API key")
    secret_hash = models.CharField(max_length=64, help_text="SHA-256 hash of the secret key")
    environment = models.CharField(
        max_length=20,
        choices=Environment.choices,
        default=Environment.SANDBOX,
    )
    scopes = models.JSONField(default=list, blank=True, help_text="List of permitted scopes")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["key_hash", "environment"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.environment}) — {self.key_prefix}..."

    @property
    def scopes_list(self):
        return self.scopes if isinstance(self.scopes, list) else []

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
