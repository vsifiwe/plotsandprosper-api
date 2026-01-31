"""
ContributionRecordingService — record_contribution, record_penalty; validate window and boundaries.
"""

from decimal import Decimal
from typing import Optional

from django.utils import timezone

from common.models import Contribution, ContributionWindow, Member, Penalty, Reversal
from common.models.reversal import ReversalRecordType


def _reversed_contribution_ids():
    """Set of contribution IDs that have been reversed."""
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.CONTRIBUTION
        ).values_list("original_record_id", flat=True)
    )


def _reversed_penalty_ids():
    """Set of penalty IDs that have been reversed."""
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.PENALTY
        ).values_list("original_record_id", flat=True)
    )


def record_contribution(
    member_id,
    window_id: int,
    amount: Decimal,
    recorded_at=None,
    created_by=None,
) -> Contribution:
    """
    Record a contribution. Validates window exists and optional min/max amount.
    """
    window = ContributionWindow.objects.get(pk=window_id)
    member = Member.objects.get(pk=member_id)
    if recorded_at is None:
        recorded_at = timezone.now()
    amount = Decimal(amount)
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if window.min_amount is not None and amount < window.min_amount:
        raise ValueError(f"Amount below window min_amount {window.min_amount}")
    if window.max_amount is not None and amount > window.max_amount:
        raise ValueError(f"Amount above window max_amount {window.max_amount}")
    return Contribution.objects.create(
        member=member,
        window=window,
        amount=amount,
        recorded_at=recorded_at,
    )


def record_penalty(
    member_id,
    amount: Decimal,
    reason: str = "",
    window_id: Optional[int] = None,
    recorded_at=None,
    created_by=None,
) -> Penalty:
    """Record a penalty (late fee)."""
    member = Member.objects.get(pk=member_id)
    if recorded_at is None:
        recorded_at = timezone.now()
    amount = Decimal(amount)
    if amount <= 0:
        raise ValueError("Amount must be positive")
    window = None
    if window_id is not None:
        window = ContributionWindow.objects.get(pk=window_id)
    return Penalty.objects.create(
        member=member,
        amount=amount,
        reason=reason or "",
        window=window,
        recorded_at=recorded_at,
    )
