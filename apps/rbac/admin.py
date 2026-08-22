from django.contrib import admin

from apps.rbac.models import Permission, Role, RolePermission, UserRole, WithdrawalLimit


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("code", "name", "description")
    readonly_fields = ("uuid", "created_at")
    ordering = ("category", "code")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "is_system", "is_active", "created_at")
    list_filter = ("category", "is_system", "is_active")
    search_fields = ("code", "name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("category", "code")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission", "created_at")
    list_filter = ("role__category",)
    search_fields = ("role__code", "permission__code")
    readonly_fields = ("uuid", "created_at")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_by", "is_active", "created_at")
    list_filter = ("role__category", "is_active", "role__code")
    search_fields = ("user__email", "role__code")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ["-created_at"]


@admin.register(WithdrawalLimit)
class WithdrawalLimitAdmin(admin.ModelAdmin):
    list_display = ("name", "currency", "auto_approve_max", "officer_approve_max", "is_active", "created_at")
    list_filter = ("currency", "is_active")
    search_fields = ("name",)
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ["-created_at"]
