from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.reconciliation.models import ReconciliationBatch, ReconciliationRecord
from apps.reconciliation.serializers import (
    ReconciliationBatchSerializer, ReconciliationBatchCreateSerializer,
    ReconciliationRecordSerializer,
)
from common.permissions.permissions import HasPermission
from common.utilities.responses import success_response, error_response


class ReconciliationBatchListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "reconciliation.view"
    queryset = ReconciliationBatch.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReconciliationBatchSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReconciliationBatchSerializer(queryset, many=True)
        return success_response(data=serializer.data, message="Reconciliation batches retrieved")

    def create(self, request, *args, **kwargs):
        from common.permissions.permissions import user_has_permission
        if not user_has_permission(request.user, "reconciliation.run"):
            return error_response(message="Permission denied", error_code="PERMISSION_DENIED", status=403)

        serializer = ReconciliationBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from django.utils import timezone
        import uuid as uuid_lib

        batch = ReconciliationBatch.objects.create(
            batch_reference=f"SP-REC-{timezone.now().strftime('%Y%m%d')}-{uuid_lib.uuid4().hex[:6].upper()}",
            initiated_by=request.user,
            **serializer.validated_data,
        )

        data = ReconciliationBatchSerializer(batch).data
        return success_response(data=data, message="Reconciliation batch created", status=status.HTTP_201_CREATED)


class ReconciliationBatchDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "reconciliation.view"
    lookup_field = "uuid"
    queryset = ReconciliationBatch.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ReconciliationBatchSerializer(instance)
        return success_response(data=serializer.data, message="Reconciliation batch retrieved")


class ReconciliationRecordListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "reconciliation.view"
    serializer_class = ReconciliationRecordSerializer

    def get_queryset(self):
        batch_uuid = self.kwargs.get("batch_uuid")
        return ReconciliationRecord.objects.filter(batch__uuid=batch_uuid)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Reconciliation records retrieved")
