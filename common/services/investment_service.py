"""
InvestmentRecordingService — record_investment: compute member shares
    from eligible savings, create HoldingShare rows.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from django.db.models import Sum

from common.models import (
    Contribution,
    HoldingShare,
    Investment,
    Penalty,
    Reversal,
)
from common.models.reversal import ReversalRecordType


def _reversed_contribution_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.CONTRIBUTION
        ).values_list("original_record_id", flat=True)
    )


def _reversed_penalty_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.PENALTY
        ).values_list("original_record_id", flat=True)
    )


def _eligible_savings_per_member_as_of(as_of_date):
    """
    Per member: sum of non-reversed contributions with recorded_at <= as_of_date
    minus sum of non-reversed penalties with recorded_at <= as_of_date.
    Returns dict member_id -> Decimal.
    """
    rev_contrib = _reversed_contribution_ids()
    rev_penalty = _reversed_penalty_ids()

    # Contributions: exclude reversed, filter by recorded_at <= as_of_date
    contrib_qs = Contribution.objects.filter(recorded_at__date__lte=as_of_date).exclude(
        id__in=rev_contrib
    )
    contrib_by_member = dict(
        contrib_qs.values("member_id")
        .annotate(total=Sum("amount"))
        .values_list("member_id", "total")
    )

    penalty_qs = Penalty.objects.filter(recorded_at__date__lte=as_of_date).exclude(
        id__in=rev_penalty
    )
    penalty_by_member = dict(
        penalty_qs.values("member_id")
        .annotate(total=Sum("amount"))
        .values_list("member_id", "total")
    )

    members = set(contrib_by_member) | set(penalty_by_member)
    result = {}
    for m_id in members:
        c = contrib_by_member.get(m_id) or Decimal("0")
        p = penalty_by_member.get(m_id) or Decimal("0")
        result[m_id] = c - p
    return result


def record_investment(
    recorded_at,
    unit_value: Decimal,
    total_units: Optional[Decimal] = None,
    created_by=None,
) -> Investment:
    """
    Record investment at date and unit value. Compute each member's eligible savings
    as of that date (contributions - penalties, excluding reversed); create HoldingShare
    rows with units = eligible_savings / unit_value.
    """
    if isinstance(recorded_at, str):
        recorded_at = datetime.fromisoformat(recorded_at.replace("Z", "+00:00")).date()
    elif hasattr(recorded_at, "date"):
        recorded_at = recorded_at.date()
    unit_value = Decimal(unit_value)
    if unit_value <= 0:
        raise ValueError("Unit value must be positive")

    eligible = _eligible_savings_per_member_as_of(recorded_at)
    total_pool = sum(eligible.values())
    if total_pool <= 0:
        # No eligible savings: create investment with no holding shares
        inv = Investment.objects.create(
            recorded_at=recorded_at,
            unit_value=unit_value,
            total_units=total_units or Decimal("0"),
            created_by=created_by,
        )
        return inv

    inv = Investment.objects.create(
        recorded_at=recorded_at,
        unit_value=unit_value,
        total_units=total_units or (total_pool / unit_value),
        created_by=created_by,
    )

    for member_id, amount in eligible.items():
        if amount <= 0:
            continue
        units = amount / unit_value
        HoldingShare.objects.create(
            investment=inv,
            member_id=member_id,
            units=units,
        )
    return inv
