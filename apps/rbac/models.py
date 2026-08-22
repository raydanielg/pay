"""
RBAC models — Role, Permission, RolePermission, UserRole.

This is a flexible role-based access control system:
- Permission: granular action (e.g. 'wallet.view', 'withdrawal.approve')
- Role: named collection of permissions (e.g. 'SUPER_ADMIN', 'KYC_OFFICER')
- RolePermission: many-to-many linking roles to permissions
- UserRole: assigns roles to internal staff users
- BusinessMember.role: links business members to roles

Roles are categorized as 'internal' (SalamaPay staff) or 'business' (client staff).
"""
import uuid

from django.db import models
from django.conf import settings


class Permission(models.Model):
    """
    A granular permission like 'wallet.view' or 'withdrawal.approve'.
    Permissions are seeded from apps.rbac.permissions.ALL_PERMISSIONS.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    code = models.CharField(max_length=100, unique=True, db_index=True, help_text="e.g. wallet.view")
    name = models.CharField(max_length=200, help_text="Human-readable name")
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, default="general", help_text="e.g. wallet, payment, kyc")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "code"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Role(models.Model):
    """
    A named role that groups permissions together.

    Categories:
    - internal: SalamaPay staff roles (Super Admin, KYC Officer, etc.)
    - business: Business-side roles (Business Owner, Developer, etc.)
    - system: System roles (API Service Account, Customer)
    """
    class Category(models.TextChoices):
        INTERNAL = "internal", "Internal"
        BUSINESS = "business", "Business"
        SYSTEM = "system", "System"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True, help_text="e.g. SUPER_ADMIN, KYC_OFFICER")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.INTERNAL,
    )
    is_system = models.BooleanField(default=False, help_text="System roles cannot be deleted")
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        related_name="roles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "code"]

    def __str__(self):
        return f"{self.code} ({self.category})"


class RolePermission(models.Model):
    """
    Through model linking roles to permissions.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_permissions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("role", "permission")]
        ordering = ["role", "permission__category", "permission__code"]

    def __str__(self):
        return f"{self.role.code} → {self.permission.code}"


class UserRole(models.Model):
    """
    Assigns a role to an internal SalamaPay staff user.
    For business members, use BusinessMember.role instead.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_assignments_made",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "role")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} → {self.role.code}"


class WithdrawalLimit(models.Model):
    """
    Configurable withdrawal approval tiers.
    Controls maker-checker / four-eyes principle based on amount.

    Tiers:
    - Below auto_approve_max: auto-approved (no manual review)
    - Between auto_approve_max and officer_approve_max: withdrawal officer approves
    - Above officer_approve_max: senior approval required (finance admin or super admin)
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=100, default="Default Withdrawal Limits")
    currency = models.CharField(max_length=3, default="TZS")
    auto_approve_max = models.DecimalField(
        max_digits=18, decimal_places=2, default=500000,
        help_text="Amounts below this are auto-approved (0 = no auto-approve)",
    )
    officer_approve_max = models.DecimalField(
        max_digits=18, decimal_places=2, default=5000000,
        help_text="Amounts up to this require withdrawal officer approval",
    )
    senior_approve_roles = models.JSONField(
        default=list, blank=True,
        help_text="Role codes that can approve amounts above officer_approve_max",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.currency})"

    @property
    def senior_roles_list(self):
        return self.senior_approve_roles if isinstance(self.senior_approve_roles, list) else []

    def get_approval_tier(self, amount):
        """
        Returns the approval tier for a given amount.
        - 'auto': below auto_approve_max
        - 'officer': between auto_approve_max and officer_approve_max
        - 'senior': above officer_approve_max
        """
        from decimal import Decimal
        amount = Decimal(str(amount))

        if self.auto_approve_max > 0 and amount <= self.auto_approve_max:
            return "auto"
        elif amount <= self.officer_approve_max:
            return "officer"
        else:
            return "senior"
