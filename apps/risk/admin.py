from django.contrib import admin
from apps.risk.models import RiskRule, RiskEvent, BlacklistEntry


@admin.register(RiskRule)
class RiskRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "rule_type", "action", "risk_level", "is_active", "priority", "created_at")
    list_filter = ("risk_level", "is_active", "action")
    search_fields = ("name", "rule_type")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ["-priority", "-created_at"]


@admin.register(RiskEvent)
class RiskEventAdmin(admin.ModelAdmin):
    list_display = ("business", "event_type", "risk_level", "risk_score", "is_resolved", "created_at")
    list_filter = ("event_type", "risk_level", "is_resolved")
    search_fields = ("business__name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at", "resolved_at")
    ordering = ["-created_at"]


@admin.register(BlacklistEntry)
class BlacklistEntryAdmin(admin.ModelAdmin):
    list_display = ("entry_type", "value", "business", "is_active", "created_at")
    list_filter = ("entry_type", "is_active")
    search_fields = ("value", "reason")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ["-created_at"]
