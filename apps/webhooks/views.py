from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.webhooks.models import WebhookEndpoint, WebhookEvent, WebhookDelivery
from apps.webhooks.serializers import (
    WebhookEndpointSerializer, WebhookEndpointCreateSerializer,
    WebhookEventSerializer, WebhookDeliverySerializer,
)
from common.utilities.responses import success_response, error_response
import secrets


class WebhookEndpointListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WebhookEndpoint.objects.filter(business__owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = WebhookEndpointSerializer(queryset, many=True)
        return success_response(data=serializer.data, message="Webhook endpoints retrieved")

    def create(self, request, *args, **kwargs):
        serializer = WebhookEndpointCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        business = request.user.businesses.first()
        if not business:
            return error_response(message="No business found", error_code="NO_BUSINESS", status=404)

        endpoint = WebhookEndpoint.objects.create(
            business=business,
            secret=secrets.token_urlsafe(32),
            **serializer.validated_data,
        )

        data = WebhookEndpointSerializer(endpoint).data
        return success_response(data=data, message="Webhook endpoint created", status=status.HTTP_201_CREATED)


class WebhookEndpointDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"
    serializer_class = WebhookEndpointSerializer

    def get_queryset(self):
        return WebhookEndpoint.objects.filter(business__owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Webhook endpoint retrieved")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = WebhookEndpointCreateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=WebhookEndpointSerializer(instance).data, message="Webhook endpoint updated")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        return success_response(message="Webhook endpoint disabled")


class WebhookEventListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WebhookEventSerializer

    def get_queryset(self):
        return WebhookEvent.objects.filter(business__owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Webhook events retrieved")


class WebhookDeliveryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WebhookDeliverySerializer

    def get_queryset(self):
        return WebhookDelivery.objects.filter(endpoint__business__owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Webhook deliveries retrieved")
