"""
Custom permissions for role-based access control.

Uses the RBAC system: checks user's roles and their permissions.
Supports both internal staff roles (via UserRole) and business member roles (via BusinessMember).
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


def get_user_permissions(user):
    """
    Collect all permission codes for a user from:
    1. Internal roles (UserRole assignments)
    2. Business member roles (BusinessMember.role → Role)
    3. Superuser fallback (all permissions)
    """
    if not user or not user.is_authenticated:
        return set()

    if user.is_superuser:
        from apps.rbac.permissions import PERMISSION_CODES
        return set(PERMISSION_CODES)

    perms = set()

    from apps.rbac.models import UserRole
    for ur in UserRole.objects.filter(user=user, is_active=True, role__is_active=True):
        perms.update(ur.role.permissions.values_list("code", flat=True))

    from apps.businesses.models import BusinessMember
    for bm in BusinessMember.objects.filter(user=user, is_active=True, role__is_active=True):
        perms.update(bm.role.permissions.values_list("code", flat=True))

    return perms


def user_has_role(user, role_code):
    """Check if a user has a specific role (internal or business)."""
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    from apps.rbac.models import UserRole
    if UserRole.objects.filter(
        user=user, is_active=True, role__code=role_code, role__is_active=True
    ).exists():
        return True

    from apps.businesses.models import BusinessMember
    if BusinessMember.objects.filter(
        user=user, is_active=True, role__code=role_code, role__is_active=True
    ).exists():
        return True

    return False


def user_has_permission(user, permission_code):
    """Check if a user has a specific permission."""
    if not user or not user.is_authenticated:
        return False
    return permission_code in get_user_permissions(user)


class IsOwnerOrReadOnly(BasePermission):
    """Object-level permission: only the owner can modify."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "owner", None) or getattr(obj, "user", None)
        return owner == request.user


class IsBusinessOwner(BasePermission):
    """Only the business owner can access/modify."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [
            "business_owner", "staff",
        ]

    def has_object_permission(self, request, view, obj):
        business = getattr(obj, "business", None) or obj
        return business.owner == request.user


class IsStaffUser(BasePermission):
    """Only staff/superadmin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.user_type == "staff"
        )


class HasAPIKeyScope(BasePermission):
    """
    Checks if the authenticated API key has the required scope.
    Set `required_scope` on the view to use this permission.
    """
    def has_permission(self, request, view):
        required_scope = getattr(view, "required_scope", None)
        if not required_scope:
            return True

        api_key = request.auth
        if not api_key or not hasattr(api_key, "scopes"):
            return False

        return required_scope in api_key.scopes_list


class HasPermission(BasePermission):
    """
    Checks if the user has a specific permission code.

    Usage on a view:
        class MyView(APIView):
            permission_classes = [IsAuthenticated, HasPermission]
            required_permission = "withdrawal.approve"
    """
    def has_permission(self, request, view):
        required = getattr(view, "required_permission", None)
        if not required:
            return True
        return required in get_user_permissions(request.user)


class HasAnyPermission(BasePermission):
    """
    Checks if the user has any of the specified permissions.

    Usage:
        class MyView(APIView):
            permission_classes = [IsAuthenticated, HasAnyPermission]
            required_permissions = ["withdrawal.approve", "withdrawal.reject"]
    """
    def has_permission(self, request, view):
        required = getattr(view, "required_permissions", [])
        if not required:
            return True
        user_perms = get_user_permissions(request.user)
        return any(p in user_perms for p in required)


class HasAllPermissions(BasePermission):
    """
    Checks if the user has all of the specified permissions.
    """
    def has_permission(self, request, view):
        required = getattr(view, "required_permissions", [])
        if not required:
            return True
        user_perms = get_user_permissions(request.user)
        return all(p in user_perms for p in required)


class IsRole(BasePermission):
    """
    Checks if the user has a specific role code.

    Usage:
        class MyView(APIView):
            permission_classes = [IsAuthenticated, IsRole]
            required_role = "KYC_OFFICER"
    """
    def has_permission(self, request, view):
        required = getattr(view, "required_role", None)
        if not required:
            return True
        return user_has_role(request.user, required)


class IsReadOnly(BasePermission):
    """Only allows GET, HEAD, OPTIONS methods. For auditor/viewer roles."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
