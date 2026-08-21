"""
Views for KYC app — submit applications, upload documents, review (staff).
"""
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.kyc.models import KYCApplication, KYCDocument
from apps.kyc.serializers import (
    KYCApplicationSerializer,
    KYCDocumentSerializer,
    KYCReviewSerializer,
)
from common.permissions.permissions import IsStaffUser
from common.utilities.responses import success_response, error_response


class KYCApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = KYCApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return KYCApplication.objects.filter(business__owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="KYC applications retrieved")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        data = KYCApplicationSerializer(application).data
        return success_response(
            data=data,
            message="KYC application submitted",
            status=status.HTTP_201_CREATED,
        )


class KYCApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = KYCApplicationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return KYCApplication.objects.filter(business__owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="KYC application retrieved")


class KYCDocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_application(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            KYCApplication,
            uuid=self.kwargs["application_uuid"],
            business__owner=self.request.user,
        )

    def get_queryset(self):
        return KYCDocument.objects.filter(kyc_application=self.get_application())

    def perform_create(self, serializer):
        application = self.get_application()
        serializer.save(kyc_application=application)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message="Document uploaded",
            status=status.HTTP_201_CREATED,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Documents retrieved")


class KYCReviewView(generics.UpdateAPIView):
    """
    Staff-only endpoint to review (approve/reject) KYC applications.
    """
    serializer_class = KYCReviewSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]
    lookup_field = "uuid"
    queryset = KYCApplication.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        application = serializer.save(
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )

        if application.status == "verified":
            application.business.kyc_status = "verified"
            application.business.save()

        data = KYCApplicationSerializer(application).data
        return success_response(data=data, message=f"KYC application {application.status}")
