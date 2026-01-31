"""
StatementService — historical statement for member (contributions, penalties,
investments, exits) for a date range; deterministic, excludes reversed records.
"""

from datetime import date
from typing import Optional

from django.db.models import Q

from common.models import (
    BuyOut,
    Contribution,
    ExitRequest,
    HoldingShare,
    Member,
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


def _reversed_holding_share_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.HOLDING_SHARE
        ).values_list("original_record_id", flat=True)
    )


def _reversed_exit_request_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.EXIT_REQUEST
        ).values_list("original_record_id", flat=True)
    )


def _reversed_buy_out_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.BUY_OUT
        ).values_list("original_record_id", flat=True)
    )


def get_member_statement(
    member: Member,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> dict:
    """
    Return deterministic historical statement for member: contributions, penalties,
    investments (holdings), exit_requests, buy_outs in date range.
    Excludes reversed records. Dates filter on recorded_at / requested_at / recorded_at.
    """
    rev_contrib = _reversed_contribution_ids()
    rev_penalty = _reversed_penalty_ids()
    rev_holding = _reversed_holding_share_ids()
    rev_exit = _reversed_exit_request_ids()
    rev_buyout = _reversed_buy_out_ids()

    contributions = (
        Contribution.objects.filter(member=member)
        .exclude(id__in=rev_contrib)
        .select_related("window")
        .order_by("recorded_at")
    )
    if from_date is not None:
        contributions = contributions.filter(recorded_at__date__gte=from_date)
    if to_date is not None:
        contributions = contributions.filter(recorded_at__date__lte=to_date)
    contributions_list = [
        {
            "id": c.id,
            "window_id": c.window_id,
            "amount": float(c.amount),
            "recorded_at": c.recorded_at.isoformat(),
        }
        for c in contributions
    ]

    penalties = (
        Penalty.objects.filter(member=member)
        .exclude(id__in=rev_penalty)
        .order_by("recorded_at")
    )
    if from_date is not None:
        penalties = penalties.filter(recorded_at__date__gte=from_date)
    if to_date is not None:
        penalties = penalties.filter(recorded_at__date__lte=to_date)
    penalties_list = [
        {
            "id": p.id,
            "amount": float(p.amount),
            "reason": p.reason,
            "recorded_at": p.recorded_at.isoformat(),
        }
        for p in penalties
    ]

    holding_shares = (
        HoldingShare.objects.filter(member=member)
        .exclude(id__in=rev_holding)
        .select_related("investment")
        .order_by("investment__recorded_at")
    )
    if from_date is not None or to_date is not None:
        inv_filter = Q()
        if from_date is not None:
            inv_filter &= Q(investment__recorded_at__gte=from_date)
        if to_date is not None:
            inv_filter &= Q(investment__recorded_at__lte=to_date)
        holding_shares = holding_shares.filter(inv_filter)
    investments_list = [
        {
            "investment_id": hs.investment_id,
            "recorded_at": hs.investment.recorded_at.isoformat(),
            "unit_value": float(hs.investment.unit_value),
            "units": float(hs.units),
        }
        for hs in holding_shares
    ]

    exit_requests = (
        ExitRequest.objects.filter(member=member)
        .exclude(id__in=rev_exit)
        .order_by("requested_at")
    )
    if from_date is not None:
        exit_requests = exit_requests.filter(requested_at__date__gte=from_date)
    if to_date is not None:
        exit_requests = exit_requests.filter(requested_at__date__lte=to_date)
    exit_requests_list = [
        {
            "id": r.id,
            "requested_at": r.requested_at.isoformat(),
            "queue_position": r.queue_position,
            "status": r.status,
            "amount_entitled": float(r.amount_entitled),
        }
        for r in exit_requests
    ]

    buy_outs = (
        BuyOut.objects.filter(Q(seller=member) | Q(buyer=member))
        .exclude(id__in=rev_buyout)
        .order_by("recorded_at")
    )
    if from_date is not None:
        buy_outs = buy_outs.filter(recorded_at__date__gte=from_date)
    if to_date is not None:
        buy_outs = buy_outs.filter(recorded_at__date__lte=to_date)
    buy_outs_list = [
        {
            "id": b.id,
            "seller_id": b.seller_id,
            "buyer_id": b.buyer_id,
            "nominal_valuation": float(b.nominal_valuation),
            "recorded_at": b.recorded_at.isoformat(),
        }
        for b in buy_outs
    ]

    return {
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None,
        "contributions": contributions_list,
        "penalties": penalties_list,
        "investments": investments_list,
        "exit_requests": exit_requests_list,
        "buy_outs": buy_outs_list,
    }
