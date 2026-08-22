"""
URL routes for RBAC app.
"""
from django.urls import path

from .views import (
    PermissionListView,
    RoleListView,
    RoleDetailView,
    UserRoleListView,
    UserRoleAssignView,
    UserRoleRevokeView,
    MyPermissionsView,
    WithdrawalLimitListView,
    WithdrawalLimitDetailView,
)

urlpatterns = [
    path("rbac/permissions/", PermissionListView.as_view(), name="permission-list"),
    path("rbac/roles/", RoleListView.as_view(), name="role-list"),
    path("rbac/roles/<uuid:uuid>/", RoleDetailView.as_view(), name="role-detail"),
    path("rbac/user-roles/", UserRoleListView.as_view(), name="user-role-list"),
    path("rbac/user-roles/assign/", UserRoleAssignView.as_view(), name="user-role-assign"),
    path("rbac/user-roles/<uuid:uuid>/revoke/", UserRoleRevokeView.as_view(), name="user-role-revoke"),
    path("rbac/me/permissions/", MyPermissionsView.as_view(), name="my-permissions"),
    path("rbac/withdrawal-limits/", WithdrawalLimitListView.as_view(), name="withdrawal-limit-list"),
    path("rbac/withdrawal-limits/<uuid:uuid>/", WithdrawalLimitDetailView.as_view(), name="withdrawal-limit-detail"),
]
