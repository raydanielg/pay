"""
Transaction service — handles transaction creation, status transitions,
and coordinates with the ledger and fee services.

This is the ONLY place where transaction status should change,
ensuring ledger entries are created consistently.
"""
from decimal import Decimal
from datetime import timezone as dt_timezone

from django.db import transaction as db_transaction
from django.utils import timezone

from apps.transactions.models import Transaction
from apps.ledger.services import LedgerService, LedgerEntryInput
from apps.ledger.models import LedgerAccount
from apps.fees.services import FeeService
from common.constants.statuses import TransactionStatus, TransactionType, Currency
from common.exceptions.handlers import (
    InsufficientBalanceError,
    WalletFrozenError,
    DuplicateTransactionError,
)
from common.utilities.helpers import generate_reference


class TransactionService:
    """
    Central service for transaction lifecycle management.
    """

    @staticmethod
    @db_transaction.atomic
    def create_transaction(
        business,
        wallet,
        amount: Decimal,
        currency: str = Currency.TZS,
        type: str = TransactionType.PAYMENT,
        external_reference: str = "",
        customer=None,
        description: str = "",
        metadata: dict = None,
        idempotency_key: str = "",
        provider: str = "",
    ) -> Transaction:
        """
        Creates a new transaction in PENDING status.
        Does NOT move money — that happens on confirmation.
        """
        if not wallet.is_active:
            raise WalletFrozenError(f"Wallet {wallet.uuid} is not active")

        if idempotency_key:
            existing = Transaction.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                raise DuplicateTransactionError(
                    f"Transaction {existing.reference} already exists for this idempotency key."
                )

        reference = generate_reference(prefix="SP", type_code="TXN")

        # Calculate fees
        fee_breakdown = FeeService.calculate(
            business=business,
            transaction_type=type,
            amount=amount,
            currency=currency,
        )

        txn = Transaction.objects.create(
            reference=reference,
            external_reference=external_reference,
            business=business,
            wallet=wallet,
            customer=customer,
            amount=amount,
            fee=fee_breakdown["total_fee"],
            net_amount=amount - fee_breakdown["total_fee"],
            currency=currency,
            type=type,
            status=TransactionStatus.PENDING,
            provider=provider,
            description=description,
            metadata=metadata or {},
            idempotency_key=idempotency_key,
        )

        return txn

    @staticmethod
    @db_transaction.atomic
    def confirm_transaction(
        transaction: Transaction,
        provider_reference: str = "",
        provider_metadata: dict = None,
        user=None,
    ) -> Transaction:
        """
        Confirms a pending transaction after provider verification.
        Creates ledger entries to move money.
        """
        if transaction.status != TransactionStatus.PENDING:
            raise ValueError(f"Cannot confirm transaction in status {transaction.status}")

        if provider_reference:
            transaction.provider_reference = provider_reference
        if provider_metadata:
            transaction.provider_metadata = provider_metadata

        transaction.status = TransactionStatus.PROCESSING
        transaction.save(update_fields=["status", "provider_reference", "provider_metadata", "updated_at"])

        # Get or create ledger accounts
        wallet_account = LedgerService.get_or_create_wallet_account(transaction.wallet)
        clearing_account = LedgerService.get_or_create_system_account(
            code=f"CLEARING-{transaction.provider.upper()}-{transaction.currency}",
            name=f"{transaction.provider.title()} Clearing Account",
            account_type="liability",
            currency=transaction.currency,
        )
        fee_account = LedgerService.get_or_create_system_account(
            code=f"FEE-PLATFORM-{transaction.currency}",
            name="Platform Fee Revenue",
            account_type="revenue",
            currency=transaction.currency,
        )

        # Post ledger entries:
        # Debit clearing account (money came in from provider)
        # Credit wallet account (business receives net amount)
        # Credit fee account (platform fee revenue)
        entries = [
            LedgerEntryInput(
                account=clearing_account,
                entry_type="debit",
                amount=transaction.amount,
                description=f"Payment received via {transaction.provider}",
            ),
            LedgerEntryInput(
                account=wallet_account,
                entry_type="credit",
                amount=transaction.net_amount,
                description=f"Credit to wallet for {transaction.reference}",
            ),
        ]

        if transaction.fee > 0:
            entries.append(LedgerEntryInput(
                account=fee_account,
                entry_type="credit",
                amount=transaction.fee,
                description=f"Platform fee for {transaction.reference}",
            ))

        ledger_tx = LedgerService.post_transaction(
            entries=entries,
            description=f"Payment confirmation for {transaction.reference}",
            currency=transaction.currency,
            transaction=transaction,
            user=user,
        )

        transaction.status = TransactionStatus.SUCCESS
        transaction.completed_at = timezone.now()
        transaction.save(update_fields=["status", "completed_at", "updated_at"])

        return transaction

    @staticmethod
    @db_transaction.atomic
    def fail_transaction(
        transaction: Transaction,
        failure_reason: str = "",
        provider_metadata: dict = None,
    ) -> Transaction:
        """
        Marks a transaction as failed. No ledger entries needed
        since money was never moved.
        """
        if transaction.status in [TransactionStatus.SUCCESS, TransactionStatus.FAILED]:
            raise ValueError(f"Cannot fail transaction in status {transaction.status}")

        transaction.status = TransactionStatus.FAILED
        transaction.failure_reason = failure_reason
        if provider_metadata:
            transaction.provider_metadata = provider_metadata
        transaction.save(update_fields=["status", "failure_reason", "provider_metadata", "updated_at"])

        return transaction

    @staticmethod
    @db_transaction.atomic
    def cancel_transaction(transaction: Transaction) -> Transaction:
        """
        Cancels a pending transaction.
        """
        if transaction.status != TransactionStatus.PENDING:
            raise ValueError(f"Cannot cancel transaction in status {transaction.status}")

        transaction.status = TransactionStatus.CANCELLED
        transaction.save(update_fields=["status", "updated_at"])
        return transaction
