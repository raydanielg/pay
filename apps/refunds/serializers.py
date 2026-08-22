from rest_framework import serializers
from apps.refunds.models import Refund
from common.constants.statuses import RefundType


class RefundSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    transaction_reference = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    approved_by_email = serializers.SerializerMethodField()

    class Meta:
        model = Refund
        fields = [
            "uuid", "reference", "business", "business_name", "transaction", "transaction_reference",
            "wallet", "amount", "fee", "currency", "type", "status",
            "reason", "rejection_reason",
            "provider", "provider_reference", "provider_metadata",
            "created_by", "created_by_email", "approved_by", "approved_by_email",
            "metadata", "failure_reason",
            "created_at", "updated_at", "approved_at", "processed_at", "completed_at",
        ]
        read_only_fields = [
            "uuid", "reference", "fee", "provider_reference", "provider_metadata",
            "approved_by", "rejected_by",
            "created_at", "updated_at", "approved_at", "processed_at", "completed_at",
        ]

    def get_business_name(self, obj):
        return obj.business.name

    def get_transaction_reference(self, obj):
        return obj.transaction.reference if obj.transaction else None

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else None

    def get_approved_by_email(self, obj):
        return obj.approved_by.email if obj.approved_by else None


class RefundCreateSerializer(serializers.Serializer):
    transaction_uuid = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    type = serializers.ChoiceField(choices=RefundType.choices, default=RefundType.FULL)
    reason = serializers.CharField()
