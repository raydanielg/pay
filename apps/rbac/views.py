"""
Views for RBAC — manage roles, permissions, user role assignments, and withdrawal limits.

Only Super Admin and users with role management permissions can access these endpoints.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.rbac.models import Permission, Role, UserRole, WithdrawalLimit
from apps.rbac.serializers import (
    PermissionSerializer,
    RoleSerializer,
    RoleCreateUpdateSerializer,
    UserRoleSerializer,
    UserRoleAssignSerializer,
    WithdrawalLimitSerializer,
)
from common.permissions.permissions import HasPermission, IsReadOnly
from common.utilities.responses import success_response, error_response


class PermissionListView(generics.ListAPIView):
    """List all available permissions."""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Permissions retrieved")


class RoleListView(generics.ListCreateAPIView):
    """List all roles or create a new role."""
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "role.view"
    queryset = Role.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RoleCreateUpdateSerializer
        return RoleSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Roles retrieved")

    def create(self, request, *args, **kwargs):
        from common.permissions.permissions import user_has_permission
        if not user_has_permission(request.user, "role.create"):
            return error_response(
                message="You do not have permission to create roles",
                error_code="PERMISSION_DENIED",
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        data = RoleSerializer(role).data
        return success_response(data=data, message="Role created", status=status.HTTP_201_CREATED)


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a role."""
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "role.view"
    lookup_field = "uuid"
    queryset = Role.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return RoleCreateUpdateSerializer
        return RoleSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Role retrieved")

    def update(self, request, *args, **kwargs):
        from common.permissions.permissions import user_has_permission
        if not user_has_permission(request.user, "role.update"):
            return error_response(
                message="You do not have permission to update roles",
                error_code="PERMISSION_DENIED",
                status=status.HTTP_403_FORBIDDEN,
            )
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if instance.is_system and "code" in request.data:
            return error_response(
                message="Cannot change code of a system role",
                error_code="SYSTEM_ROLE_LOCKED",
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Role updated")

    def destroy(self, request, *args, **kwargs):
        from common.permissions.permissions import user_has_permission
        if not user_has_permission(request.user, "role.delete"):
            return error_response(
                message="You do not have permission to delete roles",
                error_code="PERMISSION_DENIED",
                status=status.HTTP_403_FORBIDDEN,
            )
        instance = self.get_object()
        if instance.is_system:
            return error_response(
                message="Cannot delete a system role",
                error_code="SYSTEM_ROLE_LOCKED",
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        return success_response(message="Role deactivated")


class UserRoleListView(generics.ListAPIView):
    """List all user role assignments."""
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "user.view"
    queryset = UserRole.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="User roles retrieved")


class UserRoleAssignView(APIView):
    """Assign a role to a user."""
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "user.assign_role"

    def post(self, request):
        serializer = UserRoleAssignSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user_role = serializer.save()
        data = UserRoleSerializer(user_role).data
        return success_response(data=data, message="Role assigned", status=status.HTTP_201_CREATED)


class UserRoleRevokeView(APIView):
    """Revoke a role from a user."""
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "user.assign_role"

    def post(self, request, uuid):
        try:
            user_role = UserRole.objects.get(uuid=uuid)
        except UserRole.DoesNotExist:
            return error_response(message="User role assignment not found", error_code="NOT_FOUND", status=404)

        user_role.is_active = False
        user_role.save(update_fields=["is_active", "updated_at"])
        return success_response(message="Role revoked")


class MyPermissionsView(APIView):
    """Returns the current user's permissions and roles."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from common.permissions.permissions import get_user_permissions, user_has_role
        from apps.rbac.models import UserRole
        from apps.businesses.models import BusinessMember

        perms = sorted(get_user_permissions(request.user))

        internal_roles = list(
            UserRole.objects.filter(user=request.user, is_active=True, role__is_active=True)
            .values_list("role__code", flat=True)
        )
        business_roles = list(
            BusinessMember.objects.filter(user=request.user, is_active=True, role__is_active=True)
            .values_list("role__code", flat=True)
        )

        data = {
            "permissions": perms,
            "internal_roles": internal_roles,
            "business_roles": business_roles,
            "is_superuser": request.user.is_superuser,
        }
        return success_response(data=data, message="Your permissions and roles")


class WithdrawalLimitListView(generics.ListCreateAPIView):
    """List or create withdrawal limits."""
    serializer_class = WithdrawalLimitSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "risk.set_limits"
    queryset = WithdrawalLimit.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Withdrawal limits retrieved")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        limit = serializer.save()
        data = WithdrawalLimitSerializer(limit).data
        return success_response(data=data, message="Withdrawal limit created", status=status.HTTP_201_CREATED)


class WithdrawalLimitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a withdrawal limit."""
    serializer_class = WithdrawalLimitSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "risk.set_limits"
    lookup_field = "uuid"
    queryset = WithdrawalLimit.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Withdrawal limit retrieved")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Withdrawal limit updated")
