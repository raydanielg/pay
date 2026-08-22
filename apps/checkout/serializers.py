from rest_framework import serializers
from apps.checkout.models import CheckoutSession


class CheckoutSessionSerializer(serializers.ModelSerializer):
    business_name = serializers.SerializerMethodField()
    checkout_url = serializers.SerializerMethodField()

    class Meta:
        model = CheckoutSession
        fields = [
            "uuid", "reference", "business", "business_name", "transaction",
            "amount", "currency", "status", "checkout_url",
            "customer_name", "customer_email", "customer_phone",
            "title", "description", "success_url", "cancel_url", "expires_at",
            "allowed_methods", "logo_url", "brand_color", "selected_method",
            "metadata", "created_at", "updated_at", "completed_at",
        ]
        read_only_fields = ["uuid", "reference", "transaction", "selected_method", "created_at", "updated_at", "completed_at"]

    def get_business_name(self, obj):
        return obj.business.name

    def get_checkout_url(self, obj):
        return obj.checkout_url


class CheckoutCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    currency = serializers.CharField(max_length=3, default="TZS")
    customer_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    customer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    success_url = serializers.URLField(required=False, allow_blank=True)
    cancel_url = serializers.URLField(required=False, allow_blank=True)
    expires_in_minutes = serializers.IntegerField(default=30)
    allowed_methods = serializers.ListField(child=serializers.CharField(), required=False)
