"""
Fee service — the ONLY place where fees are calculated.

All fee calculations go through FeeService.calculate() which:
1. Looks up applicable FeeRules for the business, transaction type, and provider
2. Calculates each fee (platform fee, provider fee, etc.)
3. Returns a breakdown of all fees and the total

This allows fees to be changed via Admin without modifying code.
"""
from decimal import Decimal
from typing import Optional

from apps.fees.models import FeeRule
from common.constants.statuses import FeeType, TransactionType, Currency


class FeeService:
    """
    Central fee calculation service.
    """

    @staticmethod
    def calculate(
        business=None,
        transaction_type: str = TransactionType.PAYMENT,
        amount: Decimal = Decimal("0.00"),
        currency: str = Currency.TZS,
        provider: str = "",
    ) -> dict:
        """
        Calculates all applicable fees for a transaction.

        Returns:
            {
                "platform_fee": Decimal,
                "provider_fee": Decimal,
                "total_fee": Decimal,
                "net_amount": Decimal,
                "payer": str,
                "breakdown": [
                    {"fee_type": "platform", "amount": Decimal, "rule_uuid": "..."},
                    {"fee_type": "provider", "amount": Decimal, "rule_uuid": "..."},
                ]
            }
        """
        if amount <= 0:
            return {
                "platform_fee": Decimal("0.00"),
                "provider_fee": Decimal("0.00"),
                "total_fee": Decimal("0.00"),
                "net_amount": amount,
                "payer": FeePayer.BUSINESS,
                "breakdown": [],
            }

        # Find applicable rules: business-specific first, then global defaults
        rules = FeeService._get_applicable_rules(
            business=business,
            transaction_type=transaction_type,
            currency=currency,
            provider=provider,
        )

        breakdown = []
        platform_fee = Decimal("0.00")
        provider_fee = Decimal("0.00")
        payer = FeePayer.BUSINESS

        for rule in rules:
            fee_amount = rule.calculate(amount)

            if rule.fee_type == FeeType.PLATFORM:
                platform_fee += fee_amount
            elif rule.fee_type == FeeType.PROVIDER:
                provider_fee += fee_amount

            payer = rule.payer  # Last rule's payer wins (or we could take majority)

            breakdown.append({
                "fee_type": rule.fee_type,
                "amount": str(fee_amount),
                "rule_uuid": str(rule.uuid),
            })

        total_fee = platform_fee + provider_fee

        # If business pays the fee, net = amount - fee
        # If customer pays the fee, net = amount (fee is added on top)
        if payer == FeePayer.BUSINESS:
            net_amount = amount - total_fee
        else:
            net_amount = amount

        return {
            "platform_fee": platform_fee,
            "provider_fee": provider_fee,
            "total_fee": total_fee,
            "net_amount": net_amount,
            "payer": payer,
            "breakdown": breakdown,
        }

    @staticmethod
    def _get_applicable_rules(
        business=None,
        transaction_type: str = TransactionType.PAYMENT,
        currency: str = Currency.TZS,
        provider: str = "",
    ) -> list:
        """
        Finds applicable fee rules, preferring business-specific over global.
        """
        from apps.businesses.models import Business

        # Business-specific rules
        biz_rules = FeeRule.objects.none()
        if business:
            biz_rules = FeeRule.objects.filter(
                business=business,
                transaction_type=transaction_type,
                currency=currency,
                is_active=True,
            )

        # Global default rules (business is null)
        global_rules = FeeRule.objects.filter(
            business__isnull=True,
            transaction_type=transaction_type,
            currency=currency,
            is_active=True,
        )

        # If provider specified, filter by provider or blank provider
        if provider:
            biz_rules = biz_rules.filter(
                provider__in=[provider, ""],
            )
            global_rules = global_rules.filter(
                provider__in=[provider, ""],
            )

        # Combine: business-specific rules take priority
        all_rules = list(biz_rules) + list(global_rules)

        # Deduplicate by fee_type — keep the first (highest priority) for each type
        seen_types = set()
        result = []
        for rule in sorted(all_rules, key=lambda r: -r.priority):
            if rule.fee_type not in seen_types:
                seen_types.add(rule.fee_type)
                result.append(rule)

        return result

    @staticmethod
    def create_default_rules():
        """
        Creates default global fee rules if they don't exist.
        Called during setup/migration.
        """
        defaults = [
            {
                "fee_type": FeeType.PLATFORM,
                "transaction_type": TransactionType.PAYMENT,
                "percentage": Decimal("0.0190"),
                "fixed_amount": Decimal("0.00"),
                "minimum_fee": Decimal("100.00"),
                "maximum_fee": Decimal("0.00"),
                "payer": FeePayer.BUSINESS,
            },
            {
                "fee_type": FeeType.PROVIDER,
                "transaction_type": TransactionType.PAYMENT,
                "percentage": Decimal("0.0050"),
                "fixed_amount": Decimal("0.00"),
                "minimum_fee": Decimal("0.00"),
                "maximum_fee": Decimal("0.00"),
                "payer": FeePayer.BUSINESS,
            },
            {
                "fee_type": FeeType.WITHDRAWAL,
                "transaction_type": TransactionType.WITHDRAWAL,
                "percentage": Decimal("0.0100"),
                "fixed_amount": Decimal("500.00"),
                "minimum_fee": Decimal("500.00"),
                "maximum_fee": Decimal("10000.00"),
                "payer": FeePayer.BUSINESS,
            },
        ]

        for default in defaults:
            FeeRule.objects.get_or_create(
                business__isnull=True,
                fee_type=default["fee_type"],
                transaction_type=default["transaction_type"],
                currency=Currency.TZS,
                defaults=default,
            )
