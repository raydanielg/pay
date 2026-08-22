from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.risk.models import RiskRule, RiskEvent, BlacklistEntry
from apps.risk.serializers import RiskRuleSerializer, RiskEventSerializer, BlacklistEntrySerializer
from common.permissions.permissions import HasPermission
from common.utilities.responses import success_response, error_response


class RiskRuleListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "risk.view"
    serializer_class = RiskRuleSerializer
    queryset = RiskRule.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Risk rules retrieved")

    def create(self, request, *args, **kwargs):
        from common.permissions.permissions import user_has_permission
        if not user_has_permission(request.user, "risk.set_limits"):
            return error_response(message="Permission denied", error_code="PERMISSION_DENIED", status=403)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Risk rule created", status=status.HTTP_201_CREATED)


class RiskRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "risk.view"
    lookup_field = "uuid"
    serializer_class = RiskRuleSerializer
    queryset = RiskRule.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Risk rule retrieved")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Risk rule updated")


class RiskEventListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "risk.view"
    serializer_class = RiskEventSerializer
    queryset = RiskEvent.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Risk events retrieved")


class BlacklistListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "risk.view"
    serializer_class = BlacklistEntrySerializer
    queryset = BlacklistEntry.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Blacklist entries retrieved")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return success_response(data=serializer.data, message="Blacklist entry created", status=status.HTTP_201_CREATED)


class BlacklistDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "risk.view"
    lookup_field = "uuid"
    serializer_class = BlacklistEntrySerializer
    queryset = BlacklistEntry.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Blacklist entry retrieved")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        return success_response(message="Blacklist entry deactivated")
