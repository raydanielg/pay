"""
Serializers for KYC app.
"""
from rest_framework import serializers

from apps.kyc.models import KYCApplication, KYCDocument


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = [
            "uuid",
            "kyc_application",
            "document_type",
            "document_number",
            "file",
            "status",
            "verified_at",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "kyc_application", "status", "verified_at", "rejection_reason", "created_at", "updated_at"]


class KYCApplicationSerializer(serializers.ModelSerializer):
    documents = KYCDocumentSerializer(many=True, read_only=True)
    business_name = serializers.SerializerMethodField()

    class Meta:
        model = KYCApplication
        fields = [
            "uuid",
            "business",
            "business_name",
            "applicant",
            "type",
            "status",
            "rejection_reason",
            "reviewed_by",
            "submitted_at",
            "reviewed_at",
            "documents",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "applicant", "status", "rejection_reason", "reviewed_by", "submitted_at", "reviewed_at", "documents", "created_at", "updated_at"]

    def get_business_name(self, obj):
        return obj.business.name

    def create(self, validated_data):
        validated_data["applicant"] = self.context["request"].user
        return super().create(validated_data)


class KYCReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for staff to review/approve/reject KYC applications.
    """
    class Meta:
        model = KYCApplication
        fields = ["status", "rejection_reason"]

    def validate(self, attrs):
        if attrs.get("status") == "rejected" and not attrs.get("rejection_reason"):
            raise serializers.ValidationError({"rejection_reason": "Rejection reason is required when rejecting."})
        return attrs
