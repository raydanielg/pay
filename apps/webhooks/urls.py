from django.urls import path
from .views import (
    WebhookEndpointListView, WebhookEndpointDetailView,
    WebhookEventListView, WebhookDeliveryListView,
)

urlpatterns = [
    path("webhooks/endpoints/", WebhookEndpointListView.as_view(), name="webhook-endpoint-list"),
    path("webhooks/endpoints/<uuid:uuid>/", WebhookEndpointDetailView.as_view(), name="webhook-endpoint-detail"),
    path("webhooks/events/", WebhookEventListView.as_view(), name="webhook-event-list"),
    path("webhooks/deliveries/", WebhookDeliveryListView.as_view(), name="webhook-delivery-list"),
]
