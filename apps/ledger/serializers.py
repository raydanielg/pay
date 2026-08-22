"""
Ledger serializers.
"""
from rest_framework import serializers

from apps.ledger.models import LedgerAccount, LedgerTransaction, LedgerEntry


class LedgerAccountSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = LedgerAccount
        fields = [
            "uuid",
            "code",
            "name",
            "account_type",
            "currency",
            "wallet",
            "is_system",
            "is_active",
            "balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "balance", "created_at", "updated_at"]

    def get_balance(self, obj):
        return str(obj.balance)


class LedgerEntrySerializer(serializers.ModelSerializer):
    account_code = serializers.SerializerMethodField()

    class Meta:
        model = LedgerEntry
        fields = [
            "uuid",
            "ledger_transaction",
            "account",
            "account_code",
            "entry_type",
            "amount",
            "currency",
            "description",
            "created_at",
        ]
        read_only_fields = ["uuid", "created_at"]

    def get_account_code(self, obj):
        return obj.account.code


class LedgerTransactionSerializer(serializers.ModelSerializer):
    entries = LedgerEntrySerializer(many=True, read_only=True)
    is_balanced = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = LedgerTransaction
        fields = [
            "uuid",
            "reference",
            "transaction",
            "description",
            "currency",
            "status",
            "posted_by",
            "posted_at",
            "reversed_at",
            "reversal_of",
            "entries",
            "is_balanced",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "reference", "posted_by", "posted_at", "reversed_at", "reversal_of", "entries", "is_balanced", "total_amount", "created_at", "updated_at"]

    def get_is_balanced(self, obj):
        return obj.is_balanced

    def get_total_amount(self, obj):
        return str(obj.total_amount)
