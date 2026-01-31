"""
ExitRequestService — create exit request (FIFO queue), optional fulfill.
Excludes reversed exit requests when assigning queue position.
"""

from decimal import Decimal
from typing import Optional

from django.db.models import Max, Sum
from django.utils import timezone

from common.models import Contribution, ExitRequest, Member, Penalty, Reversal
from common.models.exit_request import ExitRequestStatus
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


def _reversed_exit_request_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.EXIT_REQUEST
        ).values_list("original_record_id", flat=True)
    )


def _member_entitlement(member: Member) -> Decimal:
    """
    Nominal entitlement for exit: contributions (non-reversed) minus penalties (non-reversed).
    Policy: return of contributions; penalties reduce entitlement.
    """
    rev_contrib = _reversed_contribution_ids()
    rev_penalty = _reversed_penalty_ids()
    contrib_total = (
        Contribution.objects.filter(member=member)
        .exclude(id__in=rev_contrib)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )
    penalty_total = (
        Penalty.objects.filter(member=member)
        .exclude(id__in=rev_penalty)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )
    return max(Decimal("0"), contrib_total - penalty_total)


def create_exit_request(member_id: int) -> ExitRequest:
    """
    Create an exit request for the member; assign queue_position (FIFO).
    amount_entitled set from contributions - penalties (policy: return of savings).
    """
    member = Member.objects.get(pk=member_id)
    rev = _reversed_exit_request_ids()
    next_pos = (
        ExitRequest.objects.filter(status=ExitRequestStatus.QUEUED)
        .exclude(id__in=rev)
        .aggregate(m=Max("queue_position"))["m"]
    )
    queue_position = (next_pos or 0) + 1
    amount_entitled = _member_entitlement(member)
    return ExitRequest.objects.create(
        member=member,
        queue_position=queue_position,
        status=ExitRequestStatus.QUEUED,
        amount_entitled=amount_entitled,
    )


def fulfill_exit_request(
    exit_request_id: int,
    amount_entitled: Optional[Decimal] = None,
) -> ExitRequest:
    """
    Mark exit request as fulfilled; set fulfilled_at and optionally amount_entitled.
    """
    req = ExitRequest.objects.get(pk=exit_request_id)
    if req.status != ExitRequestStatus.QUEUED:
        raise ValueError(f"Exit request {exit_request_id} is not queued")
    req.status = ExitRequestStatus.FULFILLED
    req.fulfilled_at = timezone.now()
    if amount_entitled is not None:
        req.amount_entitled = amount_entitled
    req.save(update_fields=["status", "fulfilled_at", "amount_entitled"])
    return req
