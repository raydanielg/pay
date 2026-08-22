from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.refunds.models import Refund
from apps.refunds.serializers import RefundSerializer, RefundCreateSerializer
from common.permissions.permissions import HasPermission
from common.utilities.responses import success_response, error_response


class RefundListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "refund.view"
    queryset = Refund.objects.all()

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
            serializer = RefundSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RefundSerializer(queryset, many=True)
        return success_response(data=serializer.data, message="Refunds retrieved")

    def create(self, request, *args, **kwargs):
        from common.permissions.permissions import user_has_permission
        if not user_has_permission(request.user, "refund.create"):
            return error_response(message="Permission denied", error_code="PERMISSION_DENIED", status=403)

        serializer = RefundCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.transactions.models import Transaction
        from django.utils import timezone
        import uuid as uuid_lib

        try:
            transaction = Transaction.objects.get(uuid=serializer.validated_data["transaction_uuid"])
        except Transaction.DoesNotExist:
            return error_response(message="Transaction not found", error_code="NOT_FOUND", status=404)

        if transaction.status != "success":
            return error_response(message="Can only refund successful transactions", error_code="INVALID_STATE", status=400)

        amount = serializer.validated_data["amount"]
        if amount > transaction.amount:
            return error_response(message="Refund amount exceeds transaction amount", error_code="INVALID_AMOUNT", status=400)

        refund = Refund.objects.create(
            reference=f"SP-RFD-{timezone.now().strftime('%Y%m%d')}-{uuid_lib.uuid4().hex[:8].upper()}",
            business=transaction.business,
            transaction=transaction,
            wallet=transaction.wallet,
            amount=amount,
            currency=transaction.currency,
            type=serializer.validated_data.get("type", "full"),
            reason=serializer.validated_data["reason"],
            created_by=request.user,
        )

        data = RefundSerializer(refund).data
        return success_response(data=data, message="Refund created", status=status.HTTP_201_CREATED)


class RefundDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "refund.view"
    lookup_field = "uuid"
    queryset = Refund.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RefundSerializer(instance)
        return success_response(data=serializer.data, message="Refund retrieved")


class RefundApproveView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "refund.approve"

    def post(self, request, uuid):
        from django.utils import timezone
        try:
            refund = Refund.objects.get(uuid=uuid)
        except Refund.DoesNotExist:
            return error_response(message="Refund not found", error_code="NOT_FOUND", status=404)

        if refund.status != "pending":
            return error_response(message=f"Cannot approve refund in {refund.status} state", error_code="INVALID_STATE", status=400)

        if refund.created_by == request.user:
            return error_response(message="Maker-checker: you cannot approve your own refund request", error_code="MAKER_CHECKER_DENIED", status=403)

        refund.status = "approved"
        refund.approved_by = request.user
        refund.approved_at = timezone.now()
        refund.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])

        data = RefundSerializer(refund).data
        return success_response(data=data, message="Refund approved")


class RefundRejectView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "refund.approve"

    def post(self, request, uuid):
        from django.utils import timezone
        try:
            refund = Refund.objects.get(uuid=uuid)
        except Refund.DoesNotExist:
            return error_response(message="Refund not found", error_code="NOT_FOUND", status=404)

        if refund.status != "pending":
            return error_response(message=f"Cannot reject refund in {refund.status} state", error_code="INVALID_STATE", status=400)

        refund.status = "rejected"
        refund.rejected_by = request.user
        refund.rejection_reason = request.data.get("rejection_reason", "")
        refund.save(update_fields=["status", "rejected_by", "rejection_reason", "updated_at"])

        data = RefundSerializer(refund).data
        return success_response(data=data, message="Refund rejected")
