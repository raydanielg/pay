"""
Serializers for fees app.
"""
from rest_framework import serializers

from apps.fees.models import FeeRule


class FeeRuleSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()

    class Meta:
        model = FeeRule
        fields = [
            "uuid",
            "business",
            "business_name",
            "fee_type",
            "transaction_type",
            "provider",
            "currency",
            "percentage",
            "fixed_amount",
            "minimum_fee",
            "maximum_fee",
            "payer",
            "is_active",
            "priority",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]

    def get_business_name(self, obj):
        return obj.business.name if obj.business else "GLOBAL"


class FeeCalculationSerializer(serializers.Serializer):
    """
    Serializer for fee calculation requests/responses.
    """
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    currency = serializers.CharField(max_length=3, default="TZS")
    transaction_type = serializers.CharField(max_length=20, default="payment")
    provider = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")

    def validate_currency(self, value):
        from django.conf import settings
        if value not in settings.SUPPORTED_CURRENCIES:
            raise serializers.ValidationError(f"Currency {value} not supported")
        return value
