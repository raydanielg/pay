from rest_framework import serializers
from apps.developer.models import APIRequestLog, RateLimitTracker


class APIRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequestLog
        fields = [
            "uuid", "request_id", "business", "api_key", "user",
            "method", "path", "query_params", "request_body", "request_headers",
            "client_ip", "user_agent",
            "status_code", "response_time_ms", "response_body",
            "environment", "error_message", "created_at",
        ]
        read_only_fields = "__all__"


class RateLimitTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateLimitTracker
        fields = [
            "uuid", "identifier", "window_start", "request_count",
            "request_limit", "is_exceeded", "created_at", "updated_at",
        ]
        read_only_fields = "__all__"
