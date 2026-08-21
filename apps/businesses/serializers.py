"""
Serializers for businesses app.
"""
from rest_framework import serializers

from apps.businesses.models import Business, BusinessMember


class BusinessSerializer(serializers.ModelSerializer):
    owner_email = serializers.SerializerMethodField()
    can_receive_payments = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = [
            "uuid",
            "owner",
            "owner_email",
            "name",
            "legal_name",
            "registration_number",
            "tin",
            "country",
            "currency",
            "status",
            "kyc_status",
            "website",
            "description",
            "can_receive_payments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "owner", "owner_email", "status", "kyc_status", "can_receive_payments", "created_at", "updated_at"]

    def get_owner_email(self, obj):
        return obj.owner.email

    def get_can_receive_payments(self, obj):
        return obj.can_receive_payments

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class BusinessMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = BusinessMember
        fields = [
            "uuid",
            "business",
            "user",
            "user_email",
            "user_name",
            "role",
            "is_active",
            "invited_at",
            "joined_at",
            "created_at",
        ]
        read_only_fields = ["uuid", "business", "user", "user_email", "user_name", "invited_at", "joined_at", "created_at"]

    def get_user_email(self, obj):
        return obj.user.email

    def get_user_name(self, obj):
        return obj.user.full_name
