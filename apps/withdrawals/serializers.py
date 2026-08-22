from rest_framework import serializers
from apps.withdrawals.models import Withdrawal
from common.constants.statuses import WithdrawalStatus, WithdrawalType, Currency, PaymentMethod


class WithdrawalSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    approved_by_email = serializers.SerializerMethodField()

    class Meta:
        model = Withdrawal
        fields = [
            "uuid", "reference", "business", "business_name", "wallet", "transaction",
            "amount", "fee", "net_amount", "currency", "type", "status",
            "destination_type", "destination_account", "destination_name", "destination_metadata",
            "provider", "provider_reference", "provider_metadata",
            "created_by", "created_by_email", "approved_by", "approved_by_email",
            "approval_tier", "approval_note", "rejection_reason",
            "retry_count", "max_retries", "last_retry_at",
            "description", "metadata", "failure_reason",
            "created_at", "updated_at", "approved_at", "processed_at", "completed_at",
        ]
        read_only_fields = [
            "uuid", "reference", "net_amount", "provider_reference", "provider_metadata",
            "approved_by", "rejected_by", "approval_tier", "retry_count", "last_retry_at",
            "created_at", "updated_at", "approved_at", "processed_at", "completed_at",
        ]

    def get_business_name(self, obj):
        return obj.business.name

    def get_created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else None

    def get_approved_by_email(self, obj):
        return obj.approved_by.email if obj.approved_by else None


class WithdrawalCreateSerializer(serializers.Serializer):
    wallet_uuid = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    destination_type = serializers.ChoiceField(choices=PaymentMethod.choices, default=PaymentMethod.MOBILE_MONEY)
    destination_account = serializers.CharField(max_length=100)
    destination_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    type = serializers.ChoiceField(choices=WithdrawalType.choices, default=WithdrawalType.MANUAL)


class WithdrawalApproveSerializer(serializers.Serializer):
    approval_note = serializers.CharField(required=False, allow_blank=True)


class WithdrawalRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField()
