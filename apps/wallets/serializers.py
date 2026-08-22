"""
Wallet serializers.
"""
from rest_framework import serializers
from decimal import Decimal

from apps.wallets.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    total_balance = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = [
            "uuid",
            "business",
            "business_name",
            "currency",
            "label",
            "status",
            "available_balance",
            "pending_balance",
            "locked_balance",
            "total_balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "available_balance", "pending_balance", "locked_balance", "total_balance", "created_at", "updated_at"]

    def get_business_name(self, obj):
        return obj.business.name

    def get_total_balance(self, obj):
        return str(obj.total_balance)

    def create(self, validated_data):
        from common.exceptions.handlers import KYCRequiredError
        business = validated_data["business"]
        if not business.is_kyc_verified:
            raise KYCRequiredError("Business KYC must be verified before creating a wallet")
        wallet = Wallet.objects.create(
            business=business,
            currency=validated_data.get("currency", "TZS"),
            status="active",
        )
        return wallet
