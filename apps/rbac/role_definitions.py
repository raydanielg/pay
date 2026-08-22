"""
Role definitions — 18 initial roles with their permission mappings.

This is the single source of truth for what permissions each role has.
The seed_roles management command reads this to populate the database.
"""
from apps.rbac.permissions import *


# ── Internal Roles (SalamaPay Staff) ─────────────────────

SUPER_ADMIN = {
    "code": "SUPER_ADMIN",
    "name": "Super Admin",
    "description": "Full system access. Can manage all resources, users, roles, and settings. Cannot directly edit posted ledger entries — must use reversal workflow.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        # All permissions except ledger.adjust (must use reversal workflow)
        WALLET_VIEW, WALLET_CREATE, WALLET_FREEZE, WALLET_UNFREEZE, WALLET_ADJUST,
        PAYMENT_VIEW, PAYMENT_CREATE, PAYMENT_REFUND, PAYMENT_REVERSE, PAYMENT_EXPORT,
        WITHDRAWAL_VIEW, WITHDRAWAL_CREATE, WITHDRAWAL_APPROVE, WITHDRAWAL_REJECT, WITHDRAWAL_CANCEL,
        REFUND_VIEW, REFUND_CREATE, REFUND_APPROVE, REFUND_REJECT,
        KYC_VIEW, KYC_REVIEW, KYC_APPROVE, KYC_REJECT, KYC_REQUEST_DOCS,
        FEES_VIEW, FEES_CREATE, FEES_UPDATE, FEES_DELETE,
        SETTLEMENT_VIEW, SETTLEMENT_CREATE, SETTLEMENT_APPROVE, SETTLEMENT_PROCESS,
        RECONCILIATION_VIEW, RECONCILIATION_RUN, RECONCILIATION_RESOLVE, RECONCILIATION_EXPORT,
        LEDGER_VIEW, LEDGER_REVERSE,
        API_KEY_VIEW, API_KEY_CREATE, API_KEY_REVOKE,
        WEBHOOK_VIEW, WEBHOOK_CREATE, WEBHOOK_UPDATE, WEBHOOK_DELETE,
        BUSINESS_VIEW, BUSINESS_CREATE, BUSINESS_UPDATE, BUSINESS_SUSPEND,
        TEAM_VIEW, TEAM_INVITE, TEAM_REMOVE, TEAM_UPDATE_ROLE,
        USER_VIEW, USER_CREATE, USER_UPDATE, USER_SUSPEND, USER_ASSIGN_ROLE,
        ROLE_VIEW, ROLE_CREATE, ROLE_UPDATE, ROLE_DELETE,
        RISK_VIEW, RISK_SET_LIMITS, RISK_BLACKLIST, RISK_FREEZE_WALLET, RISK_REVIEW_TRANSACTION,
        REPORT_VIEW, REPORT_EXPORT, REPORT_FINANCIAL,
        AUDIT_VIEW, AUDIT_EXPORT,
        SYSTEM_SETTINGS_VIEW, SYSTEM_SETTINGS_UPDATE, SYSTEM_HEALTH_VIEW,
        SECURITY_VIEW, SECURITY_REVOKE_SESSION, SECURITY_MANAGE_IPS,
        CUSTOMER_VIEW, CUSTOMER_CREATE, CUSTOMER_UPDATE,
    ],
}

OPERATIONS_ADMIN = {
    "code": "OPERATIONS_ADMIN",
    "name": "Operations Admin",
    "description": "Manages day-to-day operations: transactions, wallets, withdrawals, provider issues. Cannot change system settings or fees.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        WALLET_VIEW, WALLET_FREEZE, WALLET_UNFREEZE,
        PAYMENT_VIEW, PAYMENT_CREATE, PAYMENT_REVERSE, PAYMENT_EXPORT,
        WITHDRAWAL_VIEW, WITHDRAWAL_APPROVE, WITHDRAWAL_REJECT, WITHDRAWAL_CANCEL,
        REFUND_VIEW, REFUND_APPROVE, REFUND_REJECT,
        KYC_VIEW,
        FEES_VIEW,
        SETTLEMENT_VIEW,
        RECONCILIATION_VIEW,
        LEDGER_VIEW,
        BUSINESS_VIEW, BUSINESS_UPDATE,
        TEAM_VIEW,
        USER_VIEW,
        RISK_VIEW, RISK_REVIEW_TRANSACTION,
        REPORT_VIEW, REPORT_EXPORT,
        CUSTOMER_VIEW,
    ],
}

FINANCE_ADMIN = {
    "code": "FINANCE_ADMIN",
    "name": "Finance Admin",
    "description": "Manages financial operations: balances, fees, settlements, reconciliation, refunds, financial reports.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        WALLET_VIEW, WALLET_ADJUST,
        PAYMENT_VIEW, PAYMENT_REFUND, PAYMENT_REVERSE, PAYMENT_EXPORT,
        WITHDRAWAL_VIEW, WITHDRAWAL_APPROVE, WITHDRAWAL_REJECT,
        REFUND_VIEW, REFUND_CREATE, REFUND_APPROVE, REFUND_REJECT,
        FEES_VIEW, FEES_CREATE, FEES_UPDATE,
        SETTLEMENT_VIEW, SETTLEMENT_CREATE, SETTLEMENT_APPROVE, SETTLEMENT_PROCESS,
        RECONCILIATION_VIEW, RECONCILIATION_RUN, RECONCILIATION_RESOLVE, RECONCILIATION_EXPORT,
        LEDGER_VIEW, LEDGER_REVERSE,
        REPORT_VIEW, REPORT_EXPORT, REPORT_FINANCIAL,
        AUDIT_VIEW,
    ],
}

KYC_OFFICER = {
    "code": "KYC_OFFICER",
    "name": "KYC Officer",
    "description": "Handles KYC verification: review documents, approve/reject applications, request additional documents.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        KYC_VIEW, KYC_REVIEW, KYC_APPROVE, KYC_REJECT, KYC_REQUEST_DOCS,
        BUSINESS_VIEW,
        USER_VIEW,
    ],
}

RISK_OFFICER = {
    "code": "RISK_OFFICER",
    "name": "Risk & Compliance Officer",
    "description": "Monitors suspicious activity, sets limits, blacklists accounts, freezes wallets for risk reasons.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        RISK_VIEW, RISK_SET_LIMITS, RISK_BLACKLIST, RISK_FREEZE_WALLET, RISK_REVIEW_TRANSACTION,
        WALLET_VIEW, WALLET_FREEZE,
        PAYMENT_VIEW,
        WITHDRAWAL_VIEW,
        BUSINESS_VIEW,
        USER_VIEW,
        REPORT_VIEW,
    ],
}

RECONCILIATION_OFFICER = {
    "code": "RECONCILIATION_OFFICER",
    "name": "Reconciliation Officer",
    "description": "Reconciles SalamaPay records with provider (Selcom) and ledger. Can run reconciliation and resolve mismatches.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        RECONCILIATION_VIEW, RECONCILIATION_RUN, RECONCILIATION_RESOLVE, RECONCILIATION_EXPORT,
        LEDGER_VIEW,
        PAYMENT_VIEW,
        SETTLEMENT_VIEW,
        REPORT_VIEW, REPORT_EXPORT,
    ],
}

WITHDRAWAL_OFFICER = {
    "code": "WITHDRAWAL_OFFICER",
    "name": "Withdrawal Officer",
    "description": "Reviews and approves/rejects withdrawal requests. Implements maker-checker: cannot create withdrawals.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        WITHDRAWAL_VIEW, WITHDRAWAL_APPROVE, WITHDRAWAL_REJECT, WITHDRAWAL_CANCEL,
        WALLET_VIEW,
        PAYMENT_VIEW,
        LEDGER_VIEW,
    ],
}

SUPPORT_AGENT = {
    "code": "SUPPORT_AGENT",
    "name": "Support Agent",
    "description": "Customer support: search users, transactions, check statuses. Cannot touch money or modify records.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        USER_VIEW,
        BUSINESS_VIEW,
        PAYMENT_VIEW,
        WITHDRAWAL_VIEW,
        WALLET_VIEW,
        KYC_VIEW,
        CUSTOMER_VIEW,
    ],
}

TECHNICAL_ADMIN = {
    "code": "TECHNICAL_ADMIN",
    "name": "Technical Admin",
    "description": "Manages API keys, webhooks, API logs, sandbox, integrations. No access to financial operations.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        API_KEY_VIEW, API_KEY_CREATE, API_KEY_REVOKE,
        WEBHOOK_VIEW, WEBHOOK_CREATE, WEBHOOK_UPDATE, WEBHOOK_DELETE,
        BUSINESS_VIEW,
        SYSTEM_HEALTH_VIEW,
    ],
}

AUDITOR = {
    "code": "AUDITOR",
    "name": "Auditor",
    "description": "Read-only access to all financial records, transactions, ledger, KYC history, audit logs. No create/update/delete.",
    "category": "internal",
    "is_system": True,
    "permissions": [
        WALLET_VIEW,
        PAYMENT_VIEW, PAYMENT_EXPORT,
        WITHDRAWAL_VIEW,
        REFUND_VIEW,
        KYC_VIEW,
        FEES_VIEW,
        SETTLEMENT_VIEW,
        RECONCILIATION_VIEW, RECONCILIATION_EXPORT,
        LEDGER_VIEW,
        BUSINESS_VIEW,
        USER_VIEW,
        REPORT_VIEW, REPORT_EXPORT, REPORT_FINANCIAL,
        AUDIT_VIEW, AUDIT_EXPORT,
    ],
}


# ── Business Roles (Client Staff) ───────────────────────

BUSINESS_OWNER = {
    "code": "BUSINESS_OWNER",
    "name": "Business Owner",
    "description": "Full business access: manage team, wallets, transactions, API, withdrawals, settlements, webhooks, reports.",
    "category": "business",
    "is_system": True,
    "permissions": [
        WALLET_VIEW,
        PAYMENT_VIEW, PAYMENT_CREATE, PAYMENT_REFUND, PAYMENT_EXPORT,
        WITHDRAWAL_VIEW, WITHDRAWAL_CREATE, WITHDRAWAL_APPROVE, WITHDRAWAL_REJECT, WITHDRAWAL_CANCEL,
        REFUND_VIEW, REFUND_CREATE, REFUND_APPROVE, REFUND_REJECT,
        FEES_VIEW,
        SETTLEMENT_VIEW,
        LEDGER_VIEW,
        API_KEY_VIEW, API_KEY_CREATE, API_KEY_REVOKE,
        WEBHOOK_VIEW, WEBHOOK_CREATE, WEBHOOK_UPDATE, WEBHOOK_DELETE,
        BUSINESS_VIEW, BUSINESS_UPDATE,
        TEAM_VIEW, TEAM_INVITE, TEAM_REMOVE, TEAM_UPDATE_ROLE,
        CUSTOMER_VIEW, CUSTOMER_CREATE, CUSTOMER_UPDATE,
        REPORT_VIEW, REPORT_EXPORT,
    ],
}

BUSINESS_ADMIN = {
    "code": "BUSINESS_ADMIN",
    "name": "Business Admin",
    "description": "Manages business operations: users, transactions, payments, payment links, checkout, developers, webhooks, reports. No ownership.",
    "category": "business",
    "is_system": True,
    "permissions": [
        WALLET_VIEW,
        PAYMENT_VIEW, PAYMENT_CREATE, PAYMENT_EXPORT,
        WITHDRAWAL_VIEW, WITHDRAWAL_CREATE,
        FEES_VIEW,
        SETTLEMENT_VIEW,
        API_KEY_VIEW, API_KEY_CREATE, API_KEY_REVOKE,
        WEBHOOK_VIEW, WEBHOOK_CREATE, WEBHOOK_UPDATE,
        BUSINESS_VIEW,
        TEAM_VIEW, TEAM_INVITE, TEAM_REMOVE,
        CUSTOMER_VIEW, CUSTOMER_CREATE, CUSTOMER_UPDATE,
        REPORT_VIEW, REPORT_EXPORT,
    ],
}

FINANCE_MANAGER = {
    "code": "FINANCE_MANAGER",
    "name": "Business Finance Manager",
    "description": "Manages business finances: wallets, balances, transactions, withdrawals, fees, settlements, financial reports.",
    "category": "business",
    "is_system": True,
    "permissions": [
        WALLET_VIEW,
        PAYMENT_VIEW, PAYMENT_EXPORT,
        WITHDRAWAL_VIEW, WITHDRAWAL_CREATE,
        FEES_VIEW,
        SETTLEMENT_VIEW,
        LEDGER_VIEW,
        REPORT_VIEW, REPORT_EXPORT, REPORT_FINANCIAL,
        CUSTOMER_VIEW,
    ],
}

DEVELOPER = {
    "code": "DEVELOPER",
    "name": "Business Developer",
    "description": "Technical access: API keys, webhooks, API logs, sandbox, payment APIs. No access to withdrawals, KYC, or team management.",
    "category": "business",
    "is_system": True,
    "permissions": [
        API_KEY_VIEW, API_KEY_CREATE, API_KEY_REVOKE,
        WEBHOOK_VIEW, WEBHOOK_CREATE, WEBHOOK_UPDATE,
        PAYMENT_VIEW,
        WALLET_VIEW,
        CUSTOMER_VIEW,
    ],
}

OPERATIONS_STAFF = {
    "code": "OPERATIONS_STAFF",
    "name": "Business Operations Staff",
    "description": "Day-to-day operations: create payment links, view orders, manage customers, check transaction status.",
    "category": "business",
    "is_system": True,
    "permissions": [
        PAYMENT_VIEW, PAYMENT_CREATE,
        WALLET_VIEW,
        CUSTOMER_VIEW, CUSTOMER_CREATE, CUSTOMER_UPDATE,
        REPORT_VIEW,
    ],
}

VIEWER = {
    "code": "VIEWER",
    "name": "Business Viewer",
    "description": "Read-only access: view transactions, payments, reports, wallet. No modifications.",
    "category": "business",
    "is_system": True,
    "permissions": [
        PAYMENT_VIEW,
        WALLET_VIEW,
        REPORT_VIEW,
        CUSTOMER_VIEW,
    ],
}


# ── System Roles ─────────────────────────────────────────

API_SERVICE_ACCOUNT = {
    "code": "API_SERVICE_ACCOUNT",
    "name": "API Service Account",
    "description": "Non-human account for applications (WooCommerce, Mobile App, ERP, POS). Uses API key authentication with scoped permissions.",
    "category": "system",
    "is_system": True,
    "permissions": [
        PAYMENT_VIEW, PAYMENT_CREATE,
        WALLET_VIEW,
        CUSTOMER_VIEW, CUSTOMER_CREATE, CUSTOMER_UPDATE,
        WITHDRAWAL_VIEW, WITHDRAWAL_CREATE,
    ],
}

CUSTOMER = {
    "code": "CUSTOMER",
    "name": "Customer / Payer",
    "description": "End customer who pays via payment links or checkout. Can view payment status and request refunds.",
    "category": "system",
    "is_system": True,
    "permissions": [
        PAYMENT_VIEW,
    ],
}


# ── All roles ────────────────────────────────────────────

ALL_ROLES = [
    SUPER_ADMIN,
    OPERATIONS_ADMIN,
    FINANCE_ADMIN,
    KYC_OFFICER,
    RISK_OFFICER,
    RECONCILIATION_OFFICER,
    WITHDRAWAL_OFFICER,
    SUPPORT_AGENT,
    TECHNICAL_ADMIN,
    AUDITOR,
    BUSINESS_OWNER,
    BUSINESS_ADMIN,
    FINANCE_MANAGER,
    DEVELOPER,
    OPERATIONS_STAFF,
    VIEWER,
    API_SERVICE_ACCOUNT,
    CUSTOMER,
]
