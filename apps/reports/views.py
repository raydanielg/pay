"""
Reports app — aggregated reporting and exports for the payment gateway.

Provides endpoints for:
- Daily/monthly transaction summaries
- Payment, withdrawal, fee, settlement, revenue reports
- Wallet statements
- CSV export

All reports support date range filtering and business scoping.
"""
import csv
import io
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.transactions.models import Transaction
from apps.withdrawals.models import Withdrawal
from apps.wallets.models import Wallet
from apps.fees.models import FeeRule
from common.constants.statuses import TransactionStatus, WithdrawalStatus, TransactionType
from common.utilities.responses import success_response
from common.permissions.permissions import HasPermission


class ReportBaseView(APIView):
    """Base view with common date-range parsing and business scoping."""
    permission_classes = [IsAuthenticated]

    def get_date_range(self, request):
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if not date_to:
            date_to = timezone.now().date()
        else:
            from datetime import date as parse_date
            date_to = parse_date.fromisoformat(date_to)

        if not date_from:
            date_from = date_to - timedelta(days=30)
        else:
            from datetime import date as parse_date
            date_from = parse_date.fromisoformat(date_from)

        return date_from, date_to

    def get_business(self, request):
        from apps.businesses.models import Business
        business_uuid = request.query_params.get("business_uuid")
        if business_uuid:
            return Business.objects.filter(uuid=business_uuid).first()
        return Business.objects.filter(owner=request.user).first()


class TransactionSummaryReportView(ReportBaseView):
    """Daily/monthly transaction summary report."""
    required_permission = "report.view"

    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        business = self.get_business(request)
        if not business:
            return success_response(data={}, message="No business found")

        txns = Transaction.objects.filter(
            business=business,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        )

        total_count = txns.count()
        total_amount = txns.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        total_fees = txns.aggregate(total=Sum("fee"))["total"] or Decimal("0")
        total_net = txns.aggregate(total=Sum("net_amount"))["total"] or Decimal("0")

        by_status = {}
        for status_code, _ in TransactionStatus.choices:
            count = txns.filter(status=status_code).count()
            amount = txns.filter(status=status_code).aggregate(total=Sum("amount"))["total"] or Decimal("0")
            by_status[status_code] = {"count": count, "amount": str(amount)}

        by_type = {}
        for type_code, _ in TransactionType.choices:
            count = txns.filter(type=type_code).count()
            amount = txns.filter(type=type_code).aggregate(total=Sum("amount"))["total"] or Decimal("0")
            by_type[type_code] = {"count": count, "amount": str(amount)}

        daily = []
        current = date_from
        while current <= date_to:
            day_txns = txns.filter(created_at__date=current)
            daily.append({
                "date": current.isoformat(),
                "count": day_txns.count(),
                "amount": str(day_txns.aggregate(total=Sum("amount"))["total"] or Decimal("0")),
                "fees": str(day_txns.aggregate(total=Sum("fee"))["total"] or Decimal("0")),
            })
            current += timedelta(days=1)

        data = {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "total_count": total_count,
            "total_amount": str(total_amount),
            "total_fees": str(total_fees),
            "total_net": str(total_net),
            "by_status": by_status,
            "by_type": by_type,
            "daily": daily,
        }
        return success_response(data=data, message="Transaction summary report")


class PaymentReportView(ReportBaseView):
    """Payment-specific report."""
    required_permission = "report.view"

    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        business = self.get_business(request)
        if not business:
            return success_response(data={}, message="No business found")

        payments = Transaction.objects.filter(
            business=business,
            type=TransactionType.PAYMENT,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        )

        total = payments.count()
        successful = payments.filter(status=TransactionStatus.SUCCESS).count()
        failed = payments.filter(status=TransactionStatus.FAILED).count()
        pending = payments.filter(status__in=[TransactionStatus.PENDING, TransactionStatus.PROCESSING]).count()
        success_rate = (successful / total * 100) if total > 0 else 0

        data = {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "total_payments": total,
            "successful": successful,
            "failed": failed,
            "pending": pending,
            "success_rate": round(success_rate, 2),
            "total_amount": str(payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")),
            "total_fees": str(payments.aggregate(total=Sum("fee"))["total"] or Decimal("0")),
        }
        return success_response(data=data, message="Payment report")


class WithdrawalReportView(ReportBaseView):
    """Withdrawal-specific report."""
    required_permission = "report.view"

    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        business = self.get_business(request)
        if not business:
            return success_response(data={}, message="No business found")

        withdrawals = Withdrawal.objects.filter(
            business=business,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        )

        total = withdrawals.count()
        successful = withdrawals.filter(status=WithdrawalStatus.SUCCESS).count()
        failed = withdrawals.filter(status=WithdrawalStatus.FAILED).count()
        pending = withdrawals.filter(status__in=[WithdrawalStatus.PENDING, WithdrawalStatus.APPROVED, WithdrawalStatus.PROCESSING]).count()

        data = {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "total_withdrawals": total,
            "successful": successful,
            "failed": failed,
            "pending": pending,
            "total_amount": str(withdrawals.aggregate(total=Sum("amount"))["total"] or Decimal("0")),
            "total_fees": str(withdrawals.aggregate(total=Sum("fee"))["total"] or Decimal("0")),
        }
        return success_response(data=data, message="Withdrawal report")


class FeeReportView(ReportBaseView):
    """Fee revenue report."""
    required_permission = "report.view"

    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        business = self.get_business(request)
        if not business:
            return success_response(data={}, message="No business found")

        txns = Transaction.objects.filter(
            business=business,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        )

        total_fees = txns.aggregate(total=Sum("fee"))["total"] or Decimal("0")

        fees_by_type = {}
        for type_code, _ in TransactionType.choices:
            amount = txns.filter(type=type_code).aggregate(total=Sum("fee"))["total"] or Decimal("0")
            if amount > 0:
                fees_by_type[type_code] = str(amount)

        active_rules = FeeRule.objects.filter(business=business, is_active=True).count()
        global_rules = FeeRule.objects.filter(business__isnull=True, is_active=True).count()

        data = {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "total_fees_collected": str(total_fees),
            "fees_by_type": fees_by_type,
            "active_business_rules": active_rules,
            "active_global_rules": global_rules,
        }
        return success_response(data=data, message="Fee report")


class RevenueReportView(ReportBaseView):
    """Platform revenue report (admin/staff only)."""
    required_permission = "report.financial"

    def get(self, request):
        date_from, date_to = self.get_date_range(request)

        txns = Transaction.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        )

        total_revenue = txns.aggregate(total=Sum("fee"))["total"] or Decimal("0")
        total_volume = txns.aggregate(total=Sum("amount"))["total"] or Decimal("0")

        revenue_by_business = []
        from apps.businesses.models import Business
        for biz in Business.objects.all():
            biz_txns = txns.filter(business=biz)
            biz_revenue = biz_txns.aggregate(total=Sum("fee"))["total"] or Decimal("0")
            if biz_revenue > 0:
                revenue_by_business.append({
                    "business": biz.name,
                    "transactions": biz_txns.count(),
                    "revenue": str(biz_revenue),
                    "volume": str(biz_txns.aggregate(total=Sum("amount"))["total"] or Decimal("0")),
                })

        data = {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "total_revenue": str(total_revenue),
            "total_volume": str(total_volume),
            "total_transactions": txns.count(),
            "revenue_by_business": revenue_by_business,
        }
        return success_response(data=data, message="Revenue report")


class WalletStatementView(ReportBaseView):
    """Wallet statement — transaction history for a specific wallet."""
    required_permission = "report.view"

    def get(self, request, uuid):
        from apps.wallets.models import Wallet
        try:
            wallet = Wallet.objects.get(uuid=uuid)
        except Wallet.DoesNotExist:
            return success_response(data={}, message="Wallet not found", status=404)

        date_from, date_to = self.get_date_range(request)

        txns = Transaction.objects.filter(
            wallet=wallet,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        ).order_by("-created_at")

        from apps.transactions.serializers import TransactionSerializer

        data = {
            "wallet_uuid": str(wallet.uuid),
            "wallet_label": wallet.label,
            "currency": wallet.currency,
            "opening_balance": str(wallet.available_balance),
            "available_balance": str(wallet.available_balance),
            "pending_balance": str(wallet.pending_balance),
            "locked_balance": str(wallet.locked_balance),
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "transaction_count": txns.count(),
            "total_amount": str(txns.aggregate(total=Sum("amount"))["total"] or Decimal("0")),
            "transactions": TransactionSerializer(txns[:100], many=True).data,
        }
        return success_response(data=data, message="Wallet statement")


class ExportCSVView(ReportBaseView):
    """Export transactions as CSV."""
    required_permission = "report.export"

    def get(self, request):
        date_from, date_to = self.get_date_range(request)
        business = self.get_business(request)
        if not business:
            return success_response(data={}, message="No business found")

        txns = Transaction.objects.filter(
            business=business,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        ).order_by("-created_at")[:1000]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Reference", "External Ref", "Type", "Status", "Payment Method",
            "Amount", "Fee", "Net Amount", "Currency",
            "Customer", "Provider", "Created At", "Completed At",
        ])

        for txn in txns:
            writer.writerow([
                txn.reference,
                txn.external_reference,
                txn.type,
                txn.status,
                txn.payment_method,
                str(txn.amount),
                str(txn.fee),
                str(txn.net_amount),
                txn.currency,
                txn.customer.name if txn.customer else "",
                txn.provider,
                txn.created_at.isoformat(),
                txn.completed_at.isoformat() if txn.completed_at else "",
            ])

        response = Response(
            {"success": True, "message": "CSV export", "data": {"csv": output.getvalue(), "count": txns.count()}},
            content_type="application/json",
        )
        return response
