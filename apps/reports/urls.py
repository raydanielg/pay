from django.urls import path
from .views import (
    TransactionSummaryReportView,
    PaymentReportView,
    WithdrawalReportView,
    FeeReportView,
    RevenueReportView,
    WalletStatementView,
    ExportCSVView,
)

urlpatterns = [
    path("reports/transactions/summary/", TransactionSummaryReportView.as_view(), name="report-transaction-summary"),
    path("reports/payments/", PaymentReportView.as_view(), name="report-payments"),
    path("reports/withdrawals/", WithdrawalReportView.as_view(), name="report-withdrawals"),
    path("reports/fees/", FeeReportView.as_view(), name="report-fees"),
    path("reports/revenue/", RevenueReportView.as_view(), name="report-revenue"),
    path("reports/wallets/<uuid:uuid>/statement/", WalletStatementView.as_view(), name="report-wallet-statement"),
    path("reports/export/csv/", ExportCSVView.as_view(), name="report-export-csv"),
]
