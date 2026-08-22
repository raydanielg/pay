from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.qr_payments.models import QRCode
from apps.qr_payments.serializers import QRCodeSerializer, QRCodeCreateSerializer
from common.utilities.responses import success_response, error_response


class QRCodeListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QRCode.objects.filter(business__owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = QRCodeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = QRCodeSerializer(queryset, many=True)
        return success_response(data=serializer.data, message="QR codes retrieved")

    def create(self, request, *args, **kwargs):
        serializer = QRCodeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        business = request.user.businesses.first()
        if not business:
            return error_response(message="No business found", error_code="NO_BUSINESS", status=404)

        qr = QRCode.objects.create(
            business=business,
            **serializer.validated_data,
        )

        data = QRCodeSerializer(qr).data
        return success_response(data=data, message="QR code created", status=status.HTTP_201_CREATED)


class QRCodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return QRCode.objects.filter(business__owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = QRCodeSerializer(instance)
        return success_response(data=serializer.data, message="QR code retrieved")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = "disabled"
        instance.save(update_fields=["status", "updated_at"])
        return success_response(message="QR code disabled")
