"""
BuyOutService — record buy-out (ownership transfer at nominal valuation); immutable.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from common.models import BuyOut, Member


def record_buyout(
    seller_id: int,
    nominal_valuation: Decimal,
    buyer_id: Optional[int] = None,
    valuation_inputs: Optional[dict[str, Any]] = None,
    recorded_at: Optional[datetime] = None,
    created_by: Optional[Any] = None,
) -> BuyOut:
    """
    Record an immutable buy-out: seller, optional buyer, nominal valuation.
    Ownership transfer per policy; no update/delete.
    """
    seller = Member.objects.get(pk=seller_id)
    buyer = None
    if buyer_id is not None:
        buyer = Member.objects.get(pk=buyer_id)
    rec_at = recorded_at or datetime.now()
    inputs = valuation_inputs if valuation_inputs is not None else {}
    return BuyOut.objects.create(
        seller=seller,
        buyer=buyer,
        nominal_valuation=nominal_valuation,
        valuation_inputs=inputs,
        recorded_at=rec_at,
        created_by=created_by,
    )
