"""
Transaction serializers.
"""
from rest_framework import serializers

from apps.transactions.models import Transaction, Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "uuid",
            "business",
            "name",
            "email",
            "phone",
            "external_customer_id",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "business", "created_at", "updated_at"]


class TransactionSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    customer_detail = CustomerSerializer(source="customer", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "uuid",
            "reference",
            "external_reference",
            "provider_reference",
            "business",
            "business_name",
            "wallet",
            "customer",
            "customer_detail",
            "amount",
            "fee",
            "net_amount",
            "currency",
            "type",
            "status",
            "provider",
            "provider_metadata",
            "description",
            "metadata",
            "failure_reason",
            "idempotency_key",
            "is_successful",
            "is_terminal",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = [
            "uuid", "reference", "provider_reference", "fee", "net_amount",
            "status", "provider_metadata", "failure_reason", "is_successful",
            "is_terminal", "created_at", "updated_at", "completed_at",
        ]

    def get_business_name(self, obj):
        return obj.business.name


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new transaction (payment).
    Only accepts business-facing fields — internal fields are computed.
    """
    class Meta:
        model = Transaction
        fields = [
            "external_reference",
            "wallet",
            "customer",
            "amount",
            "currency",
            "type",
            "description",
            "metadata",
            "idempotency_key",
        ]

    def validate_amount(self, value):
        from decimal import Decimal
        if value <= Decimal("0"):
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_idempotency_key(self, value):
        if value:
            existing = Transaction.objects.filter(idempotency_key=value).first()
            if existing:
                raise serializers.ValidationError({
                    "idempotency_key": f"Duplicate request. Transaction {existing.reference} already exists.",
                    "existing_reference": existing.reference,
                })
        return value
