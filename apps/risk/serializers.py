from rest_framework import serializers
from apps.risk.models import RiskRule, RiskEvent, BlacklistEntry


class RiskRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskRule
        fields = [
            "uuid", "name", "description", "rule_type", "parameters",
            "action", "risk_level", "business", "currency",
            "is_active", "priority", "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]


class RiskEventSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()

    class Meta:
        model = RiskEvent
        fields = [
            "uuid", "business", "business_name", "transaction", "risk_rule",
            "event_type", "risk_level", "risk_score",
            "description", "metadata",
            "is_resolved", "resolved_by", "resolution", "resolved_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "resolved_by", "resolved_at", "created_at", "updated_at"]

    def get_business_name(self, obj):
        return obj.business.name


class BlacklistEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlacklistEntry
        fields = [
            "uuid", "business", "entry_type", "value", "reason",
            "is_active", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "created_by", "created_at", "updated_at"]
