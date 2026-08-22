from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.payment_links.models import PaymentLink
from apps.payment_links.serializers import PaymentLinkSerializer, PaymentLinkCreateSerializer
from common.utilities.responses import success_response, error_response


class PaymentLinkListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentLink.objects.filter(business__owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaymentLinkSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PaymentLinkSerializer(queryset, many=True)
        return success_response(data=serializer.data, message="Payment links retrieved")

    def create(self, request, *args, **kwargs):
        serializer = PaymentLinkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        business = request.user.businesses.first()
        if not business:
            return error_response(message="No business found", error_code="NO_BUSINESS", status=404)

        link = PaymentLink.objects.create(
            business=business,
            **serializer.validated_data,
        )

        data = PaymentLinkSerializer(link).data
        return success_response(data=data, message="Payment link created", status=status.HTTP_201_CREATED)


class PaymentLinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return PaymentLink.objects.filter(business__owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PaymentLinkSerializer(instance)
        return success_response(data=serializer.data, message="Payment link retrieved")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = PaymentLinkCreateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=PaymentLinkSerializer(instance).data, message="Payment link updated")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = "disabled"
        instance.save(update_fields=["status", "updated_at"])
        return success_response(message="Payment link disabled")
