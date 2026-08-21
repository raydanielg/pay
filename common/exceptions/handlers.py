"""
Custom API exceptions with consistent error response format.
"""
from rest_framework.views import exception_handler
from rest_framework import status as http_status
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Standard API error format:
    {
        "success": false,
        "message": "...",
        "error": {"code": "..."},
        "request_id": "req_xxxxx"
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_code = getattr(exc, "code", None) or exc.__class__.__name__
        message = response.data.get("detail", str(exc)) if isinstance(response.data, dict) else str(exc)

        custom_data = {
            "success": False,
            "message": str(message),
            "error": {"code": error_code},
        }
        response.data = custom_data

    return response


class PaymentError(Exception):
    """Base exception for payment-related errors."""
    status_code = http_status.HTTP_400_BAD_REQUEST
    code = "PAYMENT_ERROR"

    def __init__(self, message="Payment error", code=None):
        self.message = message
        if code:
            self.code = code
        super().__init__(self.message)


class InsufficientBalanceError(PaymentError):
    code = "INSUFFICIENT_BALANCE"
    status_code = http_status.HTTP_400_BAD_REQUEST

    def __init__(self, message="Insufficient wallet balance"):
        super().__init__(message)


class LedgerImbalanceError(PaymentError):
    code = "LEDGER_IMBALANCE"
    status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message="Ledger entries do not balance — debits must equal credits"):
        super().__init__(message)


class WalletFrozenError(PaymentError):
    code = "WALLET_FROZEN"
    status_code = http_status.HTTP_400_BAD_REQUEST

    def __init__(self, message="Wallet is frozen and cannot perform operations"):
        super().__init__(message)


class KYCRequiredError(PaymentError):
    code = "KYC_REQUIRED"
    status_code = http_status.HTTP_403_FORBIDDEN

    def __init__(self, message="KYC verification required to perform this operation"):
        super().__init__(message)


class DuplicateTransactionError(PaymentError):
    code = "DUPLICATE_TRANSACTION"
    status_code = http_status.HTTP_409_CONFLICT

    def __init__(self, message="Duplicate transaction reference"):
        super().__init__(message)
