from rest_framework import serializers
from apps.payment_links.models import PaymentLink


class PaymentLinkSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = PaymentLink
        fields = [
            "uuid", "link_code", "business", "business_name", "url", "is_available",
            "amount", "currency", "title", "description", "status",
            "is_single_use", "max_uses", "use_count",
            "expires_at", "success_url", "cancel_url", "metadata",
            "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "link_code", "use_count", "created_at", "updated_at"]

    def get_business_name(self, obj):
        return obj.business.name

    def get_url(self, obj):
        return obj.url

    def get_is_available(self, obj):
        return obj.is_available


class PaymentLinkCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True)
    currency = serializers.CharField(max_length=3, default="TZS")
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    is_single_use = serializers.BooleanField(default=False)
    max_uses = serializers.IntegerField(default=0)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    success_url = serializers.URLField(required=False, allow_blank=True)
    cancel_url = serializers.URLField(required=False, allow_blank=True)
