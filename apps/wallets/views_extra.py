from django.urls import path
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.wallets.models import Wallet
from apps.wallets.serializers import WalletSerializer
from common.constants.statuses import WalletStatus
from common.utilities.responses import success_response, error_response
from common.permissions.permissions import HasPermission
from decimal import Decimal


class WalletFreezeView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "wallet.freeze"

    def post(self, request, uuid):
        try:
            wallet = Wallet.objects.get(uuid=uuid)
        except Wallet.DoesNotExist:
            return error_response(message="Wallet not found", error_code="NOT_FOUND", status=404)

        if wallet.status == WalletStatus.FROZEN:
            return error_response(message="Wallet already frozen", error_code="INVALID_STATE", status=400)

        wallet.status = WalletStatus.FROZEN
        wallet.save(update_fields=["status", "updated_at"])
        return success_response(data=WalletSerializer(wallet).data, message="Wallet frozen")


class WalletUnfreezeView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "wallet.unfreeze"

    def post(self, request, uuid):
        try:
            wallet = Wallet.objects.get(uuid=uuid)
        except Wallet.DoesNotExist:
            return error_response(message="Wallet not found", error_code="NOT_FOUND", status=404)

        if wallet.status != WalletStatus.FROZEN:
            return error_response(message="Wallet is not frozen", error_code="INVALID_STATE", status=400)

        wallet.status = WalletStatus.ACTIVE
        wallet.save(update_fields=["status", "updated_at"])
        return success_response(data=WalletSerializer(wallet).data, message="Wallet unfrozen")


class WalletTransferView(APIView):
    """Wallet-to-wallet transfer within the same business."""
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
        try:
            source_wallet = Wallet.objects.get(uuid=uuid)
        except Wallet.DoesNotExist:
            return error_response(message="Source wallet not found", error_code="NOT_FOUND", status=404)

        destination_uuid = request.data.get("destination_wallet_uuid")
        amount = request.data.get("amount")

        if not destination_uuid or not amount:
            return error_response(message="destination_wallet_uuid and amount are required", error_code="MISSING_FIELDS", status=400)

        try:
            amount = Decimal(str(amount))
        except Exception:
            return error_response(message="Invalid amount", error_code="INVALID_AMOUNT", status=400)

        try:
            dest_wallet = Wallet.objects.get(uuid=destination_uuid)
        except Wallet.DoesNotExist:
            return error_response(message="Destination wallet not found", error_code="NOT_FOUND", status=404)

        if source_wallet.uuid == dest_wallet.uuid:
            return error_response(message="Cannot transfer to the same wallet", error_code="INVALID_OPERATION", status=400)

        if source_wallet.currency != dest_wallet.currency:
            return error_response(message="Currency mismatch between wallets", error_code="CURRENCY_MISMATCH", status=400)

        if not source_wallet.can_debit or source_wallet.available_balance < amount:
            return error_response(message="Insufficient balance", error_code="INSUFFICIENT_BALANCE", status=400)

        source_wallet.available_balance -= amount
        dest_wallet.available_balance += amount
        source_wallet.save(update_fields=["available_balance", "updated_at"])
        dest_wallet.save(update_fields=["available_balance", "updated_at"])

        return success_response(
            data={
                "source_wallet": WalletSerializer(source_wallet).data,
                "destination_wallet": WalletSerializer(dest_wallet).data,
                "amount": str(amount),
                "currency": source_wallet.currency,
            },
            message="Transfer completed",
        )


class WalletDepositView(APIView):
    """Deposit funds into a wallet (admin/staff operation)."""
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "wallet.adjust"

    def post(self, request, uuid):
        try:
            wallet = Wallet.objects.get(uuid=uuid)
        except Wallet.DoesNotExist:
            return error_response(message="Wallet not found", error_code="NOT_FOUND", status=404)

        amount = request.data.get("amount")
        description = request.data.get("description", "")

        if not amount:
            return error_response(message="amount is required", error_code="MISSING_FIELDS", status=400)

        try:
            amount = Decimal(str(amount))
        except Exception:
            return error_response(message="Invalid amount", error_code="INVALID_AMOUNT", status=400)

        if amount <= 0:
            return error_response(message="Amount must be positive", error_code="INVALID_AMOUNT", status=400)

        wallet.available_balance += amount
        wallet.save(update_fields=["available_balance", "updated_at"])

        return success_response(
            data=WalletSerializer(wallet).data,
            message="Deposit completed",
        )
