"""
Custom permissions for role-based access control.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


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
