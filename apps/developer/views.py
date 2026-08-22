from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.developer.models import APIRequestLog, RateLimitTracker
from apps.developer.serializers import APIRequestLogSerializer, RateLimitTrackerSerializer
from common.permissions.permissions import HasPermission
from common.utilities.responses import success_response


class APIRequestLogListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "audit.view"
    serializer_class = APIRequestLogSerializer
    queryset = APIRequestLog.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        business_uuid = self.request.query_params.get("business_uuid")
        if business_uuid:
            qs = qs.filter(business__uuid=business_uuid)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="API request logs retrieved")


class APIRequestLogDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "audit.view"
    lookup_field = "uuid"
    serializer_class = APIRequestLogSerializer
    queryset = APIRequestLog.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="API request log retrieved")
