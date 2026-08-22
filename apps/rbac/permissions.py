"""
All permission constants for the SalamaPay RBAC system.

Permissions follow the format: <resource>.<action>
e.g. wallet.view, payment.create, withdrawal.approve

These are used by the Role-Permission system and checked via HasPermission.
"""

# ── Wallet ──────────────────────────────────────────────
WALLET_VIEW = "wallet.view"
WALLET_CREATE = "wallet.create"
WALLET_FREEZE = "wallet.freeze"
WALLET_UNFREEZE = "wallet.unfreeze"
WALLET_ADJUST = "wallet.adjust"

# ── Payment / Transaction ───────────────────────────────
PAYMENT_VIEW = "payment.view"
PAYMENT_CREATE = "payment.create"
PAYMENT_REFUND = "payment.refund"
PAYMENT_REVERSE = "payment.reverse"
PAYMENT_EXPORT = "payment.export"

# ── Withdrawal ──────────────────────────────────────────
WITHDRAWAL_VIEW = "withdrawal.view"
WITHDRAWAL_CREATE = "withdrawal.create"
WITHDRAWAL_APPROVE = "withdrawal.approve"
WITHDRAWAL_REJECT = "withdrawal.reject"
WITHDRAWAL_CANCEL = "withdrawal.cancel"

# ── Refund ──────────────────────────────────────────────
REFUND_VIEW = "refund.view"
REFUND_CREATE = "refund.create"
REFUND_APPROVE = "refund.approve"
REFUND_REJECT = "refund.reject"

# ── KYC ─────────────────────────────────────────────────
KYC_VIEW = "kyc.view"
KYC_REVIEW = "kyc.review"
KYC_APPROVE = "kyc.approve"
KYC_REJECT = "kyc.reject"
KYC_REQUEST_DOCS = "kyc.request_docs"

# ── Fees ────────────────────────────────────────────────
FEES_VIEW = "fees.view"
FEES_CREATE = "fees.create"
FEES_UPDATE = "fees.update"
FEES_DELETE = "fees.delete"

# ── Settlement ──────────────────────────────────────────
SETTLEMENT_VIEW = "settlement.view"
SETTLEMENT_CREATE = "settlement.create"
SETTLEMENT_APPROVE = "settlement.approve"
SETTLEMENT_PROCESS = "settlement.process"

# ── Reconciliation ──────────────────────────────────────
RECONCILIATION_VIEW = "reconciliation.view"
RECONCILIATION_RUN = "reconciliation.run"
RECONCILIATION_RESOLVE = "reconciliation.resolve"
RECONCILIATION_EXPORT = "reconciliation.export"

# ── Ledger ──────────────────────────────────────────────
LEDGER_VIEW = "ledger.view"
LEDGER_REVERSE = "ledger.reverse"
LEDGER_ADJUST = "ledger.adjust"

# ── API Key ─────────────────────────────────────────────
API_KEY_VIEW = "api_key.view"
API_KEY_CREATE = "api_key.create"
API_KEY_REVOKE = "api_key.revoke"

# ── Webhook ─────────────────────────────────────────────
WEBHOOK_VIEW = "webhook.view"
WEBHOOK_CREATE = "webhook.create"
WEBHOOK_UPDATE = "webhook.update"
WEBHOOK_DELETE = "webhook.delete"

# ── Business ────────────────────────────────────────────
BUSINESS_VIEW = "business.view"
BUSINESS_CREATE = "business.create"
BUSINESS_UPDATE = "business.update"
BUSINESS_SUSPEND = "business.suspend"

# ── Team / Members ──────────────────────────────────────
TEAM_VIEW = "team.view"
TEAM_INVITE = "team.invite"
TEAM_REMOVE = "team.remove"
TEAM_UPDATE_ROLE = "team.update_role"

# ── User Management ─────────────────────────────────────
USER_VIEW = "user.view"
USER_CREATE = "user.create"
USER_UPDATE = "user.update"
USER_SUSPEND = "user.suspend"
USER_ASSIGN_ROLE = "user.assign_role"

# ── Role Management ─────────────────────────────────────
ROLE_VIEW = "role.view"
ROLE_CREATE = "role.create"
ROLE_UPDATE = "role.update"
ROLE_DELETE = "role.delete"

# ── Risk & Compliance ───────────────────────────────────
RISK_VIEW = "risk.view"
RISK_SET_LIMITS = "risk.set_limits"
RISK_BLACKLIST = "risk.blacklist"
RISK_FREEZE_WALLET = "risk.freeze_wallet"
RISK_REVIEW_TRANSACTION = "risk.review_transaction"

# ── Reports ─────────────────────────────────────────────
REPORT_VIEW = "report.view"
REPORT_EXPORT = "report.export"
REPORT_FINANCIAL = "report.financial"

# ── Audit ───────────────────────────────────────────────
AUDIT_VIEW = "audit.view"
AUDIT_EXPORT = "audit.export"

# ── System ──────────────────────────────────────────────
SYSTEM_SETTINGS_VIEW = "system.settings_view"
SYSTEM_SETTINGS_UPDATE = "system.settings_update"
SYSTEM_HEALTH_VIEW = "system.health_view"

# ── Security ────────────────────────────────────────────
SECURITY_VIEW = "security.view"
SECURITY_REVOKE_SESSION = "security.revoke_session"
SECURITY_MANAGE_IPS = "security.manage_ips"

# ── Customer ────────────────────────────────────────────
CUSTOMER_VIEW = "customer.view"
CUSTOMER_CREATE = "customer.create"
CUSTOMER_UPDATE = "customer.update"

# ── All permissions grouped by category ─────────────────
ALL_PERMISSIONS = [
    # Wallet
    (WALLET_VIEW, "View wallet details and balances"),
    (WALLET_CREATE, "Create new wallets"),
    (WALLET_FREEZE, "Freeze a wallet"),
    (WALLET_UNFREEZE, "Unfreeze a wallet"),
    (WALLET_ADJUST, "Adjust wallet balance (controlled workflow)"),

    # Payment
    (PAYMENT_VIEW, "View transactions and payments"),
    (PAYMENT_CREATE, "Create payments / payment links"),
    (PAYMENT_REFUND, "Issue refunds"),
    (PAYMENT_REVERSE, "Reverse a transaction"),
    (PAYMENT_EXPORT, "Export transaction data"),

    # Withdrawal
    (WITHDRAWAL_VIEW, "View withdrawal requests"),
    (WITHDRAWAL_CREATE, "Create withdrawal requests"),
    (WITHDRAWAL_APPROVE, "Approve withdrawal requests"),
    (WITHDRAWAL_REJECT, "Reject withdrawal requests"),
    (WITHDRAWAL_CANCEL, "Cancel withdrawal requests"),

    # Refund
    (REFUND_VIEW, "View refund requests"),
    (REFUND_CREATE, "Create refund requests"),
    (REFUND_APPROVE, "Approve refund requests"),
    (REFUND_REJECT, "Reject refund requests"),

    # KYC
    (KYC_VIEW, "View KYC applications"),
    (KYC_REVIEW, "Review KYC documents"),
    (KYC_APPROVE, "Approve KYC applications"),
    (KYC_REJECT, "Reject KYC applications"),
    (KYC_REQUEST_DOCS, "Request additional KYC documents"),

    # Fees
    (FEES_VIEW, "View fee rules"),
    (FEES_CREATE, "Create fee rules"),
    (FEES_UPDATE, "Update fee rules"),
    (FEES_DELETE, "Delete fee rules"),

    # Settlement
    (SETTLEMENT_VIEW, "View settlements"),
    (SETTLEMENT_CREATE, "Create settlement batches"),
    (SETTLEMENT_APPROVE, "Approve settlements"),
    (SETTLEMENT_PROCESS, "Process settlement payouts"),

    # Reconciliation
    (RECONCILIATION_VIEW, "View reconciliation reports"),
    (RECONCILIATION_RUN, "Run reconciliation jobs"),
    (RECONCILIATION_RESOLVE, "Resolve reconciliation issues"),
    (RECONCILIATION_EXPORT, "Export reconciliation reports"),

    # Ledger
    (LEDGER_VIEW, "View ledger entries and transactions"),
    (LEDGER_REVERSE, "Reverse ledger transactions"),
    (LEDGER_ADJUST, "Create ledger adjustment entries"),

    # API Key
    (API_KEY_VIEW, "View API keys"),
    (API_KEY_CREATE, "Create API keys"),
    (API_KEY_REVOKE, "Revoke API keys"),

    # Webhook
    (WEBHOOK_VIEW, "View webhook configurations"),
    (WEBHOOK_CREATE, "Create webhook endpoints"),
    (WEBHOOK_UPDATE, "Update webhook configurations"),
    (WEBHOOK_DELETE, "Delete webhook endpoints"),

    # Business
    (BUSINESS_VIEW, "View businesses"),
    (BUSINESS_CREATE, "Create/register businesses"),
    (BUSINESS_UPDATE, "Update business details"),
    (BUSINESS_SUSPEND, "Suspend a business"),

    # Team
    (TEAM_VIEW, "View team members"),
    (TEAM_INVITE, "Invite team members"),
    (TEAM_REMOVE, "Remove team members"),
    (TEAM_UPDATE_ROLE, "Change member roles"),

    # User
    (USER_VIEW, "View users"),
    (USER_CREATE, "Create user accounts"),
    (USER_UPDATE, "Update user profiles"),
    (USER_SUSPEND, "Suspend user accounts"),
    (USER_ASSIGN_ROLE, "Assign roles to users"),

    # Role
    (ROLE_VIEW, "View roles and permissions"),
    (ROLE_CREATE, "Create new roles"),
    (ROLE_UPDATE, "Update role permissions"),
    (ROLE_DELETE, "Delete roles"),

    # Risk
    (RISK_VIEW, "View risk events and alerts"),
    (RISK_SET_LIMITS, "Set transaction and withdrawal limits"),
    (RISK_BLACKLIST, "Blacklist accounts or phone numbers"),
    (RISK_FREEZE_WALLET, "Freeze wallets for risk reasons"),
    (RISK_REVIEW_TRANSACTION, "Review flagged transactions"),

    # Reports
    (REPORT_VIEW, "View reports"),
    (REPORT_EXPORT, "Export reports"),
    (REPORT_FINANCIAL, "View financial reports"),

    # Audit
    (AUDIT_VIEW, "View audit logs"),
    (AUDIT_EXPORT, "Export audit logs"),

    # System
    (SYSTEM_SETTINGS_VIEW, "View system settings"),
    (SYSTEM_SETTINGS_UPDATE, "Update system settings"),
    (SYSTEM_HEALTH_VIEW, "View system health and monitoring"),

    # Security
    (SECURITY_VIEW, "View security events"),
    (SECURITY_REVOKE_SESSION, "Revoke user sessions"),
    (SECURITY_MANAGE_IPS, "Manage IP blacklists/whitelists"),

    # Customer
    (CUSTOMER_VIEW, "View customers"),
    (CUSTOMER_CREATE, "Create customer records"),
    (CUSTOMER_UPDATE, "Update customer records"),
]

# Quick lookup set
PERMISSION_CODES = {p[0] for p in ALL_PERMISSIONS}
