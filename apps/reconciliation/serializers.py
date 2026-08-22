from rest_framework import serializers
from apps.reconciliation.models import ReconciliationBatch, ReconciliationRecord


class ReconciliationBatchSerializer(serializers.ModelSerializer):
    initiated_by_email = serializers.SerializerMethodField()

    class Meta:
        model = ReconciliationBatch
        fields = [
            "uuid", "batch_reference", "provider", "status",
            "date_from", "date_to", "currency",
            "total_salama_records", "total_provider_records",
            "matched_count", "unmatched_count", "flagged_count",
            "total_matched_amount", "total_unmatched_amount",
            "initiated_by", "initiated_by_email",
            "error_message", "created_at", "updated_at", "completed_at",
        ]
        read_only_fields = [
            "uuid", "batch_reference", "status",
            "total_salama_records", "total_provider_records",
            "matched_count", "unmatched_count", "flagged_count",
            "total_matched_amount", "total_unmatched_amount",
            "initiated_by", "error_message", "created_at", "updated_at", "completed_at",
        ]

    def get_initiated_by_email(self, obj):
        return obj.initiated_by.email if obj.initiated_by else None


class ReconciliationBatchCreateSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=50, default="selcom")
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    currency = serializers.CharField(max_length=3, default="TZS")


class ReconciliationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconciliationRecord
        fields = [
            "uuid", "batch", "transaction",
            "status", "salama_reference", "salama_amount", "salama_status",
            "provider_reference", "provider_amount", "provider_status",
            "mismatch_type", "mismatch_details",
            "resolved_by", "resolved_at", "resolution_note",
            "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "batch", "transaction", "salama_reference", "salama_amount", "salama_status", "provider_reference", "provider_amount", "provider_status", "mismatch_type", "mismatch_details", "resolved_by", "resolved_at", "created_at", "updated_at"]
