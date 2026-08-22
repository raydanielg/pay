"""
Views for fees — list fee rules and calculate fees.
"""
from decimal import Decimal

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.fees.models import FeeRule
from apps.fees.serializers import FeeRuleSerializer, FeeCalculationSerializer
from apps.fees.services import FeeService
from common.utilities.responses import success_response, error_response


class FeeRuleListView(generics.ListCreateAPIView):
    serializer_class = FeeRuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from apps.businesses.models import Business
        from django.db.models import Q
        business = Business.objects.filter(owner=self.request.user).first()
        if business:
            return FeeRule.objects.filter(
                Q(business=business) | Q(business__isnull=True),
                is_active=True,
            )
        return FeeRule.objects.filter(business__isnull=True, is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Fee rules retrieved")


class FeeRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeeRuleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        from apps.businesses.models import Business
        business = Business.objects.filter(owner=self.request.user).first()
        if business:
            return FeeRule.objects.filter(business__in=[business, None])
        return FeeRule.objects.filter(business__isnull=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Fee rule retrieved")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Fee rule updated")


class FeeCalculateView(APIView):
    """
    Calculate fees for a given amount and transaction type.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FeeCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.businesses.models import Business
        business = Business.objects.filter(owner=request.user).first()

        result = FeeService.calculate(
            business=business,
            transaction_type=serializer.validated_data["transaction_type"],
            amount=Decimal(str(serializer.validated_data["amount"])),
            currency=serializer.validated_data["currency"],
            provider=serializer.validated_data.get("provider", ""),
        )

        data = {
            "platform_fee": str(result["platform_fee"]),
            "provider_fee": str(result["provider_fee"]),
            "total_fee": str(result["total_fee"]),
            "net_amount": str(result["net_amount"]),
            "payer": result["payer"],
            "breakdown": result["breakdown"],
        }

        return success_response(data=data, message="Fee calculation completed")
