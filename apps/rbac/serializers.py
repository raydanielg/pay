"""
Serializers for RBAC app.
"""
from rest_framework import serializers

from apps.rbac.models import Permission, Role, RolePermission, UserRole, WithdrawalLimit


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["uuid", "code", "name", "description", "category", "created_at"]
        read_only_fields = ["uuid", "created_at"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "uuid",
            "code",
            "name",
            "description",
            "category",
            "is_system",
            "is_active",
            "permissions",
            "permission_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "is_system", "created_at", "updated_at"]

    def get_permission_count(self, obj):
        return obj.permissions.count()


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating roles with permission codes.
    """
    permission_codes = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Role
        fields = [
            "uuid",
            "code",
            "name",
            "description",
            "category",
            "is_active",
            "permission_codes",
        ]
        read_only_fields = ["uuid"]

    def create(self, validated_data):
        perm_codes = validated_data.pop("permission_codes", [])
        role = Role.objects.create(**validated_data)
        if perm_codes:
            perms = Permission.objects.filter(code__in=perm_codes)
            role.permissions.set(perms)
        return role

    def update(self, instance, validated_data):
        perm_codes = validated_data.pop("permission_codes", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if perm_codes is not None:
            perms = Permission.objects.filter(code__in=perm_codes)
            instance.permissions.set(perms)
        return instance

    def to_representation(self, instance):
        return RoleSerializer(instance).data


class UserRoleSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    role_code = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()
    assigned_by_email = serializers.SerializerMethodField()

    class Meta:
        model = UserRole
        fields = [
            "uuid",
            "user",
            "user_email",
            "role",
            "role_code",
            "role_name",
            "assigned_by",
            "assigned_by_email",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "assigned_by", "created_at", "updated_at"]

    def get_user_email(self, obj):
        return obj.user.email

    def get_role_code(self, obj):
        return obj.role.code

    def get_role_name(self, obj):
        return obj.role.name

    def get_assigned_by_email(self, obj):
        return obj.assigned_by.email if obj.assigned_by else None


class UserRoleAssignSerializer(serializers.Serializer):
    """
    Serializer for assigning a role to a user.
    """
    user_email = serializers.EmailField()
    role_code = serializers.CharField(max_length=50)

    def validate_role_code(self, value):
        if not Role.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(f"Role {value} does not exist or is inactive.")
        return value

    def validate_user_email(self, value):
        from apps.accounts.models import User
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(f"User {value} does not exist.")
        return value

    def create(self, validated_data):
        from apps.accounts.models import User
        user = User.objects.get(email=validated_data["user_email"])
        role = Role.objects.get(code=validated_data["role_code"])
        assigned_by = self.context["request"].user

        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={"assigned_by": assigned_by, "is_active": True},
        )
        if not created:
            user_role.is_active = True
            user_role.assigned_by = assigned_by
            user_role.save(update_fields=["is_active", "assigned_by", "updated_at"])
        return user_role


class WithdrawalLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalLimit
        fields = [
            "uuid",
            "name",
            "currency",
            "auto_approve_max",
            "officer_approve_max",
            "senior_approve_roles",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]
