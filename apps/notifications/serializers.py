from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "uuid", "recipient_user", "business",
            "notification_type", "status",
            "title", "message", "event_type",
            "phone", "email", "metadata",
            "is_read", "read_at",
            "created_at", "updated_at", "sent_at", "delivered_at",
        ]
        read_only_fields = ["uuid", "status", "provider_message_id", "attempt_count", "error_message", "created_at", "updated_at", "sent_at", "delivered_at"]
