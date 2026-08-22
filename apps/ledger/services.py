"""
Ledger service — the ONLY place where ledger entries are created.

This service enforces the double-entry rule: total debits == total credits.
All wallet balance updates must go through this service.

Usage:
    LedgerService.post_transaction(
        reference="SP-LED-...",
        entries=[
            LedgerEntryInput(account=wallet_account, entry_type="debit", amount=Decimal("50000")),
            LedgerEntryInput(account=clearing_account, entry_type="credit", amount=Decimal("50000")),
        ],
        description="Payment received from customer",
    )
"""
from decimal import Decimal
from dataclasses import dataclass
from typing import List

from django.db import transaction as db_transaction
from django.utils import timezone

from apps.ledger.models import LedgerAccount, LedgerTransaction, LedgerEntry
from apps.wallets.models import Wallet
from common.constants.statuses import LedgerEntryType, Currency
from common.exceptions.handlers import LedgerImbalanceError, WalletFrozenError
from common.utilities.helpers import generate_reference


@dataclass
class LedgerEntryInput:
    """Input for a ledger entry — used by the LedgerService."""
    account: LedgerAccount
    entry_type: str
    amount: Decimal
    description: str = ""


class LedgerService:
    """
    Central service for all ledger operations.
    Ensures double-entry integrity and updates wallet balances.
    """

    @staticmethod
    @db_transaction.atomic
    def post_transaction(
        entries: List[LedgerEntryInput],
        reference: str = None,
        description: str = "",
        currency: str = Currency.TZS,
        transaction=None,
        user=None,
    ) -> LedgerTransaction:
        """
        Posts a balanced ledger transaction with the given entries.

        Raises LedgerImbalanceError if debits != credits.
        """
        if not entries or len(entries) < 2:
            raise LedgerImbalanceError("A ledger transaction requires at least 2 entries.")

        total_debits = sum(e.amount for e in entries if e.entry_type == LedgerEntryType.DEBIT)
        total_credits = sum(e.amount for e in entries if e.entry_type == LedgerEntryType.CREDIT)

        if total_debits != total_credits:
            raise LedgerImbalanceError(
                f"Ledger imbalance: debits={total_debits} credits={total_credits}"
            )

        if total_debits == 0:
            raise LedgerImbalanceError("Transaction amount cannot be zero.")

        if not reference:
            reference = generate_reference(prefix="SP", type_code="LED")

        ledger_tx = LedgerTransaction.objects.create(
            reference=reference,
            description=description,
            currency=currency,
            transaction=transaction,
            posted_by=user,
        )

        for entry_input in entries:
            LedgerEntry.objects.create(
                ledger_transaction=ledger_tx,
                account=entry_input.account,
                entry_type=entry_input.entry_type,
                amount=entry_input.amount,
                currency=currency,
                description=entry_input.description,
            )

        # Update wallet balances for any wallet-linked accounts
        LedgerService._update_wallet_balances(entries, currency)

        return ledger_tx

    @staticmethod
    def _update_wallet_balances(entries: List[LedgerEntryInput], currency: str):
        """
        Updates wallet available_balance based on ledger entries.
        For asset accounts (wallets): debit increases, credit decreases.
        """
        wallet_updates = {}

        for entry in entries:
            if entry.account.wallet:
                wallet = entry.account.wallet
                if wallet.currency != currency:
                    continue
                if wallet.status != "active":
                    raise WalletFrozenError(f"Wallet {wallet.uuid} is not active")

                if wallet.uuid not in wallet_updates:
                    wallet_updates[wallet.uuid] = {
                        "wallet": wallet,
                        "delta": Decimal("0.00"),
                    }

                if entry.entry_type == LedgerEntryType.DEBIT:
                    wallet_updates[wallet.uuid]["delta"] += entry.amount
                else:
                    wallet_updates[wallet.uuid]["delta"] -= entry.amount

        for update in wallet_updates.values():
            wallet = update["wallet"]
            new_balance = wallet.available_balance + update["delta"]
            if new_balance < 0:
                raise LedgerImbalanceError(
                    f"Wallet {wallet.uuid} would have negative balance: {new_balance}"
                )
            wallet.available_balance = new_balance
            wallet.save(update_fields=["available_balance", "updated_at"])

    @staticmethod
    @db_transaction.atomic
    def reverse_transaction(ledger_transaction: LedgerTransaction, user=None) -> LedgerTransaction:
        """
        Creates a reversal transaction that mirrors the original entries.
        Debits become credits and vice versa.
        """
        if ledger_transaction.status == "reversed":
            raise ValueError("Transaction is already reversed.")

        original_entries = ledger_transaction.entries.all()

        reversal_entries = []
        for entry in original_entries:
            reversed_type = (
                LedgerEntryType.CREDIT if entry.entry_type == LedgerEntryType.DEBIT
                else LedgerEntryType.DEBIT
            )
            reversal_entries.append(LedgerEntryInput(
                account=entry.account,
                entry_type=reversed_type,
                amount=entry.amount,
                description=f"Reversal of {ledger_transaction.reference}",
            ))

        reversal_ref = generate_reference(prefix="SP", type_code="REV")
        reversal = LedgerService.post_transaction(
            entries=reversal_entries,
            reference=reversal_ref,
            description=f"Reversal of {ledger_transaction.reference}",
            currency=ledger_transaction.currency,
            user=user,
        )
        reversal.reversal_of = ledger_transaction
        reversal.save(update_fields=["reversal_of"])

        ledger_transaction.status = "reversed"
        ledger_transaction.reversed_at = timezone.now()
        ledger_transaction.save(update_fields=["status", "reversed_at", "updated_at"])

        return reversal

    @staticmethod
    def get_or_create_wallet_account(wallet: Wallet) -> LedgerAccount:
        """
        Gets or creates the ledger account linked to a wallet.
        """
        account, created = LedgerAccount.objects.get_or_create(
            wallet=wallet,
            defaults={
                "code": f"WALLET-{wallet.business.uuid.hex[:8].upper()}-{wallet.currency}",
                "name": f"{wallet.business.name} — {wallet.currency} Wallet",
                "account_type": "asset",
                "currency": wallet.currency,
            },
        )
        return account

    @staticmethod
    def get_or_create_system_account(code: str, name: str, account_type: str, currency: str = Currency.TZS) -> LedgerAccount:
        """
        Gets or creates a system ledger account (clearing, fees, etc.).
        """
        account, created = LedgerAccount.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "account_type": account_type,
                "currency": currency,
                "is_system": True,
            },
        )
        return account
