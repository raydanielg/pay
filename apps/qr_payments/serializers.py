from rest_framework import serializers
from apps.qr_payments.models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = [
            "uuid", "code", "business", "business_name", "transaction",
            "type", "status", "amount", "currency", "title",
            "qr_image_url", "qr_data", "expires_at", "scan_count",
            "metadata", "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "code", "qr_image_url", "qr_data", "scan_count", "created_at", "updated_at"]

    def get_business_name(self, obj):
        return obj.business.name


class QRCodeCreateSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=10, default="static")
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True)
    currency = serializers.CharField(max_length=3, default="TZS")
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
