"""
Management command to seed permissions, roles, and withdrawal limits.

Usage:
    python manage.py seed_roles
"""
from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction

from apps.rbac.models import Permission, Role, RolePermission, WithdrawalLimit
from apps.rbac.permissions import ALL_PERMISSIONS
from apps.rbac.role_definitions import ALL_ROLES


class Command(BaseCommand):
    help = "Seed all permissions, roles, and default withdrawal limits into the database"

    @db_transaction.atomic
    def handle(self, *args, **options):
        # ── Seed permissions ──────────────────────────────
        perm_count = 0
        for code, name in ALL_PERMISSIONS:
            category = code.split(".")[0]
            obj, created = Permission.objects.get_or_create(
                code=code,
                defaults={"name": name, "category": category},
            )
            if created:
                perm_count += 1
            else:
                obj.name = name
                obj.category = category
                obj.save(update_fields=["name", "category"])

        self.stdout.write(self.style.SUCCESS(f"Permissions: {perm_count} created, {len(ALL_PERMISSIONS) - perm_count} updated"))

        # ── Seed roles ────────────────────────────────────
        role_count = 0
        for role_def in ALL_ROLES:
            role, created = Role.objects.get_or_create(
                code=role_def["code"],
                defaults={
                    "name": role_def["name"],
                    "description": role_def["description"],
                    "category": role_def["category"],
                    "is_system": role_def.get("is_system", False),
                },
            )
            if created:
                role_count += 1
            else:
                role.name = role_def["name"]
                role.description = role_def["description"]
                role.category = role_def["category"]
                role.is_system = role_def.get("is_system", False)
                role.save(update_fields=["name", "description", "category", "is_system"])

            # Sync permissions
            perm_codes = role_def["permissions"]
            existing_perms = set(role.permissions.values_list("code", flat=True))
            desired_perms = set(perm_codes)

            # Add missing permissions
            to_add = desired_perms - existing_perms
            for perm_code in to_add:
                perm = Permission.objects.get(code=perm_code)
                RolePermission.objects.get_or_create(role=role, permission=perm)

            # Remove extra permissions (only for system roles to keep them clean)
            if role.is_system:
                to_remove = existing_perms - desired_perms
                for perm_code in to_remove:
                    perm = Permission.objects.get(code=perm_code)
                    RolePermission.objects.filter(role=role, permission=perm).delete()

        self.stdout.write(self.style.SUCCESS(f"Roles: {role_count} created, {len(ALL_ROLES) - role_count} updated"))

        # ── Seed default withdrawal limits ────────────────
        limit, created = WithdrawalLimit.objects.get_or_create(
            currency="TZS",
            defaults={
                "name": "Default Withdrawal Limits",
                "auto_approve_max": 500000,
                "officer_approve_max": 5000000,
                "senior_approve_roles": ["FINANCE_ADMIN", "SUPER_ADMIN"],
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Withdrawal limits created: auto≤{limit.auto_approve_max}, officer≤{limit.officer_approve_max}"))
        else:
            self.stdout.write(self.style.WARNING(f"Withdrawal limits already exist for {limit.currency}"))

        # ── Summary ───────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS(f"  Permissions: {Permission.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Roles:       {Role.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Role-Perm links: {RolePermission.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        # List roles with permission counts
        for role in Role.objects.all().order_by("category", "code"):
            perm_count = role.permissions.count()
            self.stdout.write(f"  {role.code:30s} [{role.category:8s}] {perm_count:3d} permissions")
