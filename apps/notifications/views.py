from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from common.utilities.responses import success_response


class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient_user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Notifications retrieved")


class NotificationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient_user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_read:
            from django.utils import timezone
            instance.is_read = True
            instance.read_at = timezone.now()
            instance.save(update_fields=["is_read", "read_at", "updated_at"])
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Notification retrieved")


class UnreadCountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient_user=request.user, is_read=False).count()
        return success_response(data={"unread_count": count}, message="Unread count")
