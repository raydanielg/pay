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
