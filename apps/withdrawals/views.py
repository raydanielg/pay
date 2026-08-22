from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.withdrawals.models import Withdrawal
from apps.withdrawals.serializers import (
    WithdrawalSerializer, WithdrawalCreateSerializer,
    WithdrawalApproveSerializer, WithdrawalRejectSerializer,
)
from common.permissions.permissions import HasPermission
from common.utilities.responses import success_response, error_response


class WithdrawalListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "withdrawal.view"
    queryset = Withdrawal.objects.all()

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
            serializer = WithdrawalSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = WithdrawalSerializer(queryset, many=True)
        return success_response(data=serializer.data, message="Withdrawals retrieved")

    def create(self, request, *args, **kwargs):
        from common.permissions.permissions import user_has_permission
        if not user_has_permission(request.user, "withdrawal.create"):
            return error_response(message="Permission denied", error_code="PERMISSION_DENIED", status=403)

        serializer = WithdrawalCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.wallets.models import Wallet
        from decimal import Decimal
        from django.utils import timezone
        import uuid as uuid_lib

        try:
            wallet = Wallet.objects.get(uuid=serializer.validated_data["wallet_uuid"])
        except Wallet.DoesNotExist:
            return error_response(message="Wallet not found", error_code="WALLET_NOT_FOUND", status=404)

        amount = serializer.validated_data["amount"]
        if wallet.available_balance < amount:
            return error_response(message="Insufficient balance", error_code="INSUFFICIENT_BALANCE", status=400)

        from apps.rbac.services import MakerCheckerService
        tier = MakerCheckerService.get_approval_tier(amount, wallet.currency)

        withdrawal = Withdrawal.objects.create(
            reference=f"SP-WDR-{timezone.now().strftime('%Y%m%d')}-{uuid_lib.uuid4().hex[:8].upper()}",
            business=wallet.business,
            wallet=wallet,
            amount=amount,
            net_amount=amount,
            currency=wallet.currency,
            type=serializer.validated_data.get("type", "manual"),
            destination_type=serializer.validated_data.get("destination_type", "mobile_money"),
            destination_account=serializer.validated_data["destination_account"],
            destination_name=serializer.validated_data.get("destination_name", ""),
            description=serializer.validated_data.get("description", ""),
            created_by=request.user,
            approval_tier=tier,
        )

        if tier == "auto":
            withdrawal.status = "approved"
            withdrawal.approved_at = timezone.now()
            withdrawal.save(update_fields=["status", "approved_at", "updated_at"])

        data = WithdrawalSerializer(withdrawal).data
        return success_response(data=data, message="Withdrawal created", status=status.HTTP_201_CREATED)


class WithdrawalDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "withdrawal.view"
    lookup_field = "uuid"
    queryset = Withdrawal.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = WithdrawalSerializer(instance)
        return success_response(data=serializer.data, message="Withdrawal retrieved")


class WithdrawalApproveView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "withdrawal.approve"

    def post(self, request, uuid):
        from django.utils import timezone
        try:
            withdrawal = Withdrawal.objects.get(uuid=uuid)
        except Withdrawal.DoesNotExist:
            return error_response(message="Withdrawal not found", error_code="NOT_FOUND", status=404)

        if withdrawal.status != "pending":
            return error_response(message=f"Cannot approve withdrawal in {withdrawal.status} state", error_code="INVALID_STATE", status=400)

        from apps.rbac.services import MakerCheckerService
        check = MakerCheckerService.can_approve(
            user=request.user,
            amount=withdrawal.amount,
            currency=withdrawal.currency,
            creator=withdrawal.created_by,
        )
        if not check["can_approve"]:
            return error_response(message=check["reason"], error_code="MAKER_CHECKER_DENIED", status=403)

        serializer = WithdrawalApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        withdrawal.status = "approved"
        withdrawal.approved_by = request.user
        withdrawal.approved_at = timezone.now()
        withdrawal.approval_note = serializer.validated_data.get("approval_note", "")
        withdrawal.save(update_fields=["status", "approved_by", "approved_at", "approval_note", "updated_at"])

        data = WithdrawalSerializer(withdrawal).data
        return success_response(data=data, message="Withdrawal approved")


class WithdrawalRejectView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "withdrawal.approve"

    def post(self, request, uuid):
        from django.utils import timezone
        try:
            withdrawal = Withdrawal.objects.get(uuid=uuid)
        except Withdrawal.DoesNotExist:
            return error_response(message="Withdrawal not found", error_code="NOT_FOUND", status=404)

        if withdrawal.status != "pending":
            return error_response(message=f"Cannot reject withdrawal in {withdrawal.status} state", error_code="INVALID_STATE", status=400)

        serializer = WithdrawalRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        withdrawal.status = "rejected"
        withdrawal.rejected_by = request.user
        withdrawal.rejection_reason = serializer.validated_data["rejection_reason"]
        withdrawal.save(update_fields=["status", "rejected_by", "rejection_reason", "updated_at"])

        data = WithdrawalSerializer(withdrawal).data
        return success_response(data=data, message="Withdrawal rejected")
