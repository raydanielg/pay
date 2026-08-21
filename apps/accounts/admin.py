from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import User, APIKey


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "user_type", "status", "is_verified", "created_at")
    list_filter = ("user_type", "status", "is_verified", "is_staff", "is_superuser")
    search_fields = ("email", "phone", "first_name", "last_name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "phone", "uuid")}),
        ("Account", {"fields": ("user_type", "status", "is_verified", "two_factor_enabled")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "user_type"),
        }),
    )
    readonly_fields = ("uuid",)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "key_prefix", "environment", "is_active", "last_used_at", "created_at")
    list_filter = ("environment", "is_active")
    search_fields = ("name", "key_prefix", "business__name")
    readonly_fields = ("uuid", "key_prefix", "key_hash", "secret_hash", "last_used_at", "created_at", "updated_at")
    ordering = ("-created_at",)
