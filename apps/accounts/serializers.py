"""
Serializers for accounts app — User registration, profile, and API key management.
"""
from rest_framework import serializers

from apps.accounts.models import User, APIKey
from common.constants.statuses import UserType, Environment
from common.utilities.helpers import generate_api_key, generate_api_secret, hash_token


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "uuid",
            "email",
            "phone",
            "first_name",
            "last_name",
            "user_type",
            "password",
            "password_confirm",
        ]
        read_only_fields = ["uuid"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.status = "pending"
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "uuid",
            "email",
            "phone",
            "first_name",
            "last_name",
            "full_name",
            "user_type",
            "status",
            "is_verified",
            "two_factor_enabled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "email", "user_type", "status", "is_verified", "created_at", "updated_at"]

    def get_full_name(self, obj):
        return obj.full_name


class APIKeySerializer(serializers.ModelSerializer):
    """
    Serializer for displaying API keys (masked).
    Never exposes the actual key or secret.
    """
    class Meta:
        model = APIKey
        fields = [
            "uuid",
            "name",
            "key_prefix",
            "environment",
            "scopes",
            "is_active",
            "expires_at",
            "last_used_at",
            "created_at",
        ]
        read_only_fields = ["uuid", "key_prefix", "last_used_at", "created_at"]


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating API keys.
    Returns the plain-text key and secret only once at creation.
    """
    class Meta:
        model = APIKey
        fields = ["name", "environment", "scopes", "expires_at"]

    def create(self, validated_data):
        business = self.context["business"]
        environment = validated_data.get("environment", Environment.SANDBOX)

        plain_key = generate_api_key(environment)
        plain_secret = generate_api_secret()

        api_key = APIKey.objects.create(
            business=business,
            name=validated_data["name"],
            key_prefix=plain_key[:12],
            key_hash=hash_token(plain_key),
            secret_hash=hash_token(plain_secret),
            environment=environment,
            scopes=validated_data.get("scopes", []),
            expires_at=validated_data.get("expires_at"),
        )

        api_key._plain_key = plain_key
        api_key._plain_secret = plain_secret
        return api_key

    def to_representation(self, instance):
        data = APIKeySerializer(instance).data
        data["api_key"] = getattr(instance, "_plain_key", None)
        data["secret_key"] = getattr(instance, "_plain_secret", None)
        data["warning"] = "Store these credentials securely. They will not be shown again."
        return data
