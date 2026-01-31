"""
PositionService — aggregate member position and group aggregates from ledger.
Excludes reversed records; includes holdings (HoldingShare × unit_value).
"""

from decimal import Decimal

from django.db.models import Sum

from common.models import (
    AssetShare,
    Contribution,
    ExitRequest,
    HoldingShare,
    Member,
    Penalty,
    Reversal,
)
from common.models.reversal import ReversalRecordType


# Source-of-truth disclaimer per constitution/spec
SOURCE_OF_TRUTH_DISCLAIMER = (
    "External bank and investment records are the ultimate source of truth in disputes."
)


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


def _reversed_holding_share_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.HOLDING_SHARE
        ).values_list("original_record_id", flat=True)
    )


def _reversed_asset_share_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.ASSET_SHARE
        ).values_list("original_record_id", flat=True)
    )


def _reversed_exit_request_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.EXIT_REQUEST
        ).values_list("original_record_id", flat=True)
    )


def get_member_position(member: Member) -> dict:
    """
    Return member's financial position: contributions total, penalties total,
    holdings_breakdown (HoldingShare × unit_value, excluding reversed),
    assets_breakdown (AssetShare with recorded_purchase_value, excluding reversed),
    exit_request (None), source_of_truth_disclaimer.
    Excludes reversed contributions, penalties, holding shares, asset shares.
    """
    rev_contrib = _reversed_contribution_ids()
    rev_penalty = _reversed_penalty_ids()
    rev_holding = _reversed_holding_share_ids()
    rev_asset_share = _reversed_asset_share_ids()

    contributions_total = Contribution.objects.filter(member=member).exclude(
        id__in=rev_contrib
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    penalties_total = Penalty.objects.filter(member=member).exclude(
        id__in=rev_penalty
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    holdings_breakdown = []
    for hs in (
        HoldingShare.objects.filter(member=member)
        .exclude(id__in=rev_holding)
        .select_related("investment")
    ):
        holdings_breakdown.append(
            {
                "investment_id": hs.investment_id,
                "units": float(hs.units),
                "unit_value": float(hs.investment.unit_value),
                "recorded_at": hs.investment.recorded_at.isoformat(),
            }
        )

    assets_breakdown = []
    for as_ in (
        AssetShare.objects.filter(member=member)
        .exclude(id__in=rev_asset_share)
        .select_related("asset")
    ):
        assets_breakdown.append(
            {
                "asset_id": as_.asset_id,
                "share_percentage": float(as_.share_percentage),
                "recorded_purchase_value": float(as_.asset.recorded_purchase_value),
            }
        )

    rev_exit = _reversed_exit_request_ids()
    exit_request = None
    latest_exit = (
        ExitRequest.objects.filter(member=member)
        .exclude(id__in=rev_exit)
        .order_by("-requested_at")
        .first()
    )
    if latest_exit is not None:
        exit_request = {
            "status": latest_exit.status,
            "queue_position": latest_exit.queue_position,
            "amount_entitled": float(latest_exit.amount_entitled),
        }

    return {
        "contributions_total": float(contributions_total),
        "penalties_total": float(penalties_total),
        "holdings_breakdown": holdings_breakdown,
        "assets_breakdown": assets_breakdown,
        "exit_request": exit_request,
        "source_of_truth_disclaimer": SOURCE_OF_TRUTH_DISCLAIMER,
    }


def get_group_aggregates() -> dict:
    """
    Return group-level aggregates: total_members, total_pool (sum of non-reversed contributions).
    """
    rev_contrib = _reversed_contribution_ids()
    total_members = Member.objects.count()
    total_pool = Contribution.objects.exclude(id__in=rev_contrib).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")
    return {
        "total_members": total_members,
        "total_pool": float(total_pool),
    }
