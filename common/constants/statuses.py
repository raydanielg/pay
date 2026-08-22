"""
Centralized status and type constants for the entire payment platform.
Using TextChoices ensures consistent values across the database.
"""
from django.db import models


class UserStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    BLOCKED = "blocked", "Blocked"
    PENDING = "pending", "Pending"


class UserType(models.TextChoices):
    INDIVIDUAL = "individual", "Individual"
    BUSINESS_OWNER = "business_owner", "Business Owner"
    DEVELOPER = "developer", "Developer"
    STAFF = "staff", "Staff"


class BusinessStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    BLOCKED = "blocked", "Blocked"
    PENDING = "pending", "Pending"


class KYCStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    PENDING = "pending", "Pending"
    UNDER_REVIEW = "under_review", "Under Review"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"


class KYCType(models.TextChoices):
    INDIVIDUAL = "individual", "Individual"
    BUSINESS = "business", "Business"


class WalletStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    FROZEN = "frozen", "Frozen"
    CLOSED = "closed", "Closed"
    PENDING = "pending", "Pending"


class TransactionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    REVERSED = "reversed", "Reversed"
    EXPIRED = "expired", "Expired"
    REFUNDED = "refunded", "Refunded"
    PARTIAL_REFUND = "partial_refund", "Partial Refund"


class TransactionType(models.TextChoices):
    PAYMENT = "payment", "Payment"
    TRANSFER = "transfer", "Transfer"
    WITHDRAWAL = "withdrawal", "Withdrawal"
    DEPOSIT = "deposit", "Deposit"
    REFUND = "refund", "Refund"
    FEE = "fee", "Fee"
    REVERSAL = "reversal", "Reversal"
    SETTLEMENT = "settlement", "Settlement"


class Currency(models.TextChoices):
    TZS = "TZS", "Tanzanian Shilling"
    USD = "USD", "US Dollar"
    KES = "KES", "Kenyan Shilling"
    UGX = "UGX", "Ugandan Shilling"


class LedgerEntryType(models.TextChoices):
    DEBIT = "debit", "Debit"
    CREDIT = "credit", "Credit"


class LedgerAccountType(models.TextChoices):
    ASSET = "asset", "Asset"
    LIABILITY = "liability", "Liability"
    EQUITY = "equity", "Equity"
    REVENUE = "revenue", "Revenue"
    EXPENSE = "expense", "Expense"


class FeePayer(models.TextChoices):
    BUSINESS = "business", "Business"
    CUSTOMER = "customer", "Customer"


class FeeType(models.TextChoices):
    PLATFORM = "platform", "Platform Fee"
    PROVIDER = "provider", "Provider Fee"
    WITHDRAWAL = "withdrawal", "Withdrawal Fee"
    TRANSFER = "transfer", "Transfer Fee"
    REFUND = "refund", "Refund Fee"
    SETTLEMENT = "settlement", "Settlement Fee"


class Environment(models.TextChoices):
    SANDBOX = "sandbox", "Sandbox"
    PRODUCTION = "production", "Production"


class PaymentMethod(models.TextChoices):
    MOBILE_MONEY = "mobile_money", "Mobile Money"
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CARD = "card", "Card"
    QR_CODE = "qr_code", "QR Code"
    WALLET_TRANSFER = "wallet_transfer", "Wallet Transfer"
    PHONE_NUMBER = "phone_number", "Phone Number"
    HOSTED_CHECKOUT = "hosted_checkout", "Hosted Checkout"
    PAYMENT_LINK = "payment_link", "Payment Link"


class WithdrawalStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    PROCESSING = "processing", "Processing"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    RETRYING = "retrying", "Retrying"


class WithdrawalType(models.TextChoices):
    MANUAL = "manual", "Manual"
    AUTO = "auto", "Auto"


class RefundStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    PROCESSING = "processing", "Processing"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class RefundType(models.TextChoices):
    FULL = "full", "Full Refund"
    PARTIAL = "partial", "Partial Refund"


class CheckoutStatus(models.TextChoices):
    OPEN = "open", "Open"
    COMPLETED = "completed", "Completed"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled"


class PaymentLinkStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    DISABLED = "disabled", "Disabled"
    EXPIRED = "expired", "Expired"
    USED = "used", "Used"


class QRCodeType(models.TextChoices):
    STATIC = "static", "Static QR"
    DYNAMIC = "dynamic", "Dynamic QR"


class QRCodeStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    DISABLED = "disabled", "Disabled"


class WebhookStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"
    RETRYING = "retrying", "Retrying"


class ReconciliationStatus(models.TextChoices):
    MATCHED = "matched", "Matched"
    UNMATCHED = "unmatched", "Unmatched"
    RESOLVED = "resolved", "Resolved"
    FLAGGED = "flagged", "Flagged"


class ReconciliationBatchStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class NotificationType(models.TextChoices):
    SMS = "sms", "SMS"
    EMAIL = "email", "Email"
    IN_APP = "in_app", "In-App"
    WEBHOOK = "webhook", "Webhook"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"


class RiskLevel(models.TextChoices):
    LOW = "low", "Low Risk"
    MEDIUM = "medium", "Medium Risk"
    HIGH = "high", "High Risk"
    CRITICAL = "critical", "Critical Risk"


class RiskEventType(models.TextChoices):
    VELOCITY_BREACH = "velocity_breach", "Velocity Breach"
    AMOUNT_THRESHOLD = "amount_threshold", "Amount Threshold"
    SUSPICIOUS_ACTIVITY = "suspicious_activity", "Suspicious Activity"
    BLACKLIST_MATCH = "blacklist_match", "Blacklist Match"
    MANUAL_REVIEW = "manual_review", "Manual Review"


class BlacklistType(models.TextChoices):
    PHONE = "phone", "Phone Number"
    EMAIL = "email", "Email"
    ACCOUNT = "account", "Account"
    IP = "ip", "IP Address"
