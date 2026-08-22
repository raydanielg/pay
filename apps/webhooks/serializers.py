from rest_framework import serializers
from apps.webhooks.models import WebhookEndpoint, WebhookEvent, WebhookDelivery


class WebhookEndpointSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()

    class Meta:
        model = WebhookEndpoint
        fields = [
            "uuid", "business", "business_name", "url", "secret",
            "events", "is_active", "environment",
            "max_retries", "retry_interval_seconds",
            "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "secret", "created_at", "updated_at"]

    def get_business_name(self, obj):
        return obj.business.name


class WebhookEndpointCreateSerializer(serializers.Serializer):
    url = serializers.URLField()
    events = serializers.ListField(child=serializers.CharField(), required=False)
    is_active = serializers.BooleanField(default=True)
    environment = serializers.CharField(max_length=20, default="production")
    max_retries = serializers.IntegerField(default=5)
    retry_interval_seconds = serializers.IntegerField(default=60)


class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ["uuid", "event_type", "business", "transaction", "payload", "created_at"]
        read_only_fields = ["uuid", "created_at"]


class WebhookDeliverySerializer(serializers.ModelSerializer):
    event_type = serializers.SerializerMethodField()
    endpoint_url = serializers.SerializerMethodField()

    class Meta:
        model = WebhookDelivery
        fields = [
            "uuid", "event", "event_type", "endpoint", "endpoint_url",
            "status", "attempt_count", "max_attempts",
            "response_status_code", "response_body", "error_message",
            "next_retry_at", "created_at", "updated_at", "delivered_at",
        ]
        read_only_fields = ["uuid", "response_status_code", "response_body", "error_message", "next_retry_at", "created_at", "updated_at", "delivered_at"]

    def get_event_type(self, obj):
        return obj.event.event_type

    def get_endpoint_url(self, obj):
        return obj.endpoint.url
