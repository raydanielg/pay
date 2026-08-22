from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.checkout.models import CheckoutSession
from apps.checkout.serializers import CheckoutSessionSerializer, CheckoutCreateSerializer
from common.utilities.responses import success_response, error_response


class CheckoutCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = CheckoutCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from django.utils import timezone
        from datetime import timedelta
        import uuid as uuid_lib

        data = serializer.validated_data
        expires_at = timezone.now() + timedelta(minutes=data.get("expires_in_minutes", 30))

        session = CheckoutSession.objects.create(
            reference=f"SP-CHK-{timezone.now().strftime('%Y%m%d')}-{uuid_lib.uuid4().hex[:8].upper()}",
            business=request.user.businesses.first(),
            amount=data["amount"],
            currency=data.get("currency", "TZS"),
            customer_name=data.get("customer_name", ""),
            customer_email=data.get("customer_email", ""),
            customer_phone=data.get("customer_phone", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            success_url=data.get("success_url", ""),
            cancel_url=data.get("cancel_url", ""),
            expires_at=expires_at,
            allowed_methods=data.get("allowed_methods", []),
        )

        result = CheckoutSessionSerializer(session).data
        return success_response(data=result, message="Checkout session created", status=status.HTTP_201_CREATED)


class CheckoutDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    lookup_field = "reference"
    queryset = CheckoutSession.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CheckoutSessionSerializer(instance)
        return success_response(data=serializer.data, message="Checkout session retrieved")
