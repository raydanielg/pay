"""
Maker-Checker / Four-Eyes control service.

Ensures that the person who creates a financial action (e.g. withdrawal)
is NOT the same person who approves it. This is a critical control for
payment gateways handling money.

Amount-based approval tiers:
- Below auto_approve_max: auto-approved (no manual review needed)
- Between auto_approve_max and officer_approve_max: withdrawal officer approves
- Above officer_approve_max: senior roles (FINANCE_ADMIN, SUPER_ADMIN) approve

The maker (creator) can never be the checker (approver).
"""
from decimal import Decimal
from typing import Optional

from django.db import models
from django.utils import timezone

from apps.rbac.models import WithdrawalLimit
from common.permissions.permissions import user_has_role, user_has_permission


class MakerCheckerService:
    """
    Central service for maker-checker validation.
    """

    @staticmethod
    def get_approval_tier(amount: Decimal, currency: str = "TZS") -> str:
        """
        Returns the approval tier for a given amount.
        - 'auto': below auto_approve_max
        - 'officer': between auto_approve_max and officer_approve_max
        - 'senior': above officer_approve_max
        """
        limit = WithdrawalLimit.objects.filter(
            currency=currency, is_active=True
        ).first()

        if not limit:
            return "officer"

        return limit.get_approval_tier(amount)

    @staticmethod
    def can_approve(user, amount: Decimal, currency: str = "TZS", creator=None) -> dict:
        """
        Checks if a user can approve a withdrawal of the given amount.

        Returns:
            {
                "can_approve": bool,
                "tier": str,
                "reason": str (if denied),
                "required_roles": list,
            }
        """
        result = {
            "can_approve": False,
            "tier": None,
            "reason": None,
            "required_roles": [],
        }

        # Maker-checker: creator cannot approve their own request
        if creator and user == creator:
            result["reason"] = "Maker-checker: you cannot approve a request you created."
            return result

        tier = MakerCheckerService.get_approval_tier(amount, currency)
        result["tier"] = tier

        limit = WithdrawalLimit.objects.filter(currency=currency, is_active=True).first()

        if tier == "auto":
            result["can_approve"] = True
            return result

        if tier == "officer":
            required_roles = ["WITHDRAWAL_OFFICER", "OPERATIONS_ADMIN", "FINANCE_ADMIN", "SUPER_ADMIN"]
            result["required_roles"] = required_roles
            if not user_has_permission(user, "withdrawal.approve"):
                result["reason"] = "You do not have the withdrawal.approve permission."
                return result
            if not any(user_has_role(user, r) for r in required_roles):
                result["reason"] = f"Requires one of: {', '.join(required_roles)}"
                return result
            result["can_approve"] = True
            return result

        if tier == "senior":
            senior_roles = limit.senior_roles_list if limit else ["FINANCE_ADMIN", "SUPER_ADMIN"]
            result["required_roles"] = senior_roles
            if not user_has_permission(user, "withdrawal.approve"):
                result["reason"] = "You do not have the withdrawal.approve permission."
                return result
            if not any(user_has_role(user, r) for r in senior_roles):
                result["reason"] = f"Senior approval required. Needs one of: {', '.join(senior_roles)}"
                return result
            result["can_approve"] = True
            return result

        result["reason"] = "Unknown approval tier."
        return result

    @staticmethod
    def validate_maker_checker(creator, approver) -> Optional[str]:
        """
        Validates that the creator and approver are different users.
        Returns error message if invalid, None if valid.
        """
        if creator and approver and creator == approver:
            return "Maker-checker violation: the creator cannot approve this request."
        return None
