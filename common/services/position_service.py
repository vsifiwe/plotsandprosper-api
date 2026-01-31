"""
PositionService — aggregate member position and group aggregates from ledger.
US1: contributions and penalties only; holdings/assets/exit added in later stories.
"""
from decimal import Decimal

from django.db.models import Sum

from common.models import Contribution, Member, Penalty


# Source-of-truth disclaimer per constitution/spec
SOURCE_OF_TRUTH_DISCLAIMER = (
    "External bank and investment records are the ultimate source of truth in disputes."
)


def get_member_position(member: Member) -> dict:
    """
    Return member's financial position: contributions total, penalties total,
    holdings_breakdown (empty for US1), assets_breakdown (empty for US1),
    exit_request (None for US1), source_of_truth_disclaimer.
    """
    contrib_agg = Contribution.objects.filter(member=member).aggregate(
        total=Sum("amount")
    )
    contributions_total = contrib_agg["total"] or Decimal("0")

    penalty_agg = Penalty.objects.filter(member=member).aggregate(
        total=Sum("amount")
    )
    penalties_total = penalty_agg["total"] or Decimal("0")

    return {
        "contributions_total": float(contributions_total),
        "penalties_total": float(penalties_total),
        "holdings_breakdown": [],
        "assets_breakdown": [],
        "exit_request": None,
        "source_of_truth_disclaimer": SOURCE_OF_TRUTH_DISCLAIMER,
    }


def get_group_aggregates() -> dict:
    """
    Return group-level aggregates: total_members, total_pool (sum of all contributions).
    No per-member data.
    """

    total_members = Member.objects.count()
    pool_agg = Contribution.objects.aggregate(total=Sum("amount"))
    total_pool = float(pool_agg["total"] or Decimal("0"))

    return {
        "total_members": total_members,
        "total_pool": total_pool,
    }
