"""
AssetConversionService — record_asset: create Asset and 
    AssetShare rows proportional to holdings at conversion.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from common.models import (
    Asset,
    AssetShare,
    HoldingShare,
    Investment,
    Reversal,
)
from common.models.reversal import ReversalRecordType


def _reversed_holding_share_ids():
    return set(
        Reversal.objects.filter(
            original_record_type=ReversalRecordType.HOLDING_SHARE
        ).values_list("original_record_id", flat=True)
    )


def _holding_value_per_member_as_of(as_of_date):
    """
    Per member: sum of (HoldingShare.units * Investment.unit_value) for non-reversed
    holding shares where investment.recorded_at <= as_of_date.
    Returns dict member_id -> Decimal.
    """
    rev_hs = _reversed_holding_share_ids()
    # HoldingShare with investment.recorded_at <= as_of_date, exclude reversed
    qs = (
        HoldingShare.objects.filter(investment__recorded_at__lte=as_of_date)
        .exclude(id__in=rev_hs)
        .select_related("investment")
    )
    result = {}
    for hs in qs:
        value = hs.units * hs.investment.unit_value
        result[hs.member_id] = result.get(hs.member_id, Decimal("0")) + value
    return result


def record_asset(
    name: str,
    recorded_purchase_value: Decimal,
    conversion_at,
    source_investment_id: Optional[int] = None,
    created_by=None,
) -> Asset:
    """
    Record asset conversion. Create Asset and AssetShare rows; ownership proportional
    to holdings at conversion (non-reversed HoldingShare value per member).
    Sum of share_percentage per asset = 100.
    """
    if isinstance(conversion_at, str):
        conversion_at = datetime.fromisoformat(
            conversion_at.replace("Z", "+00:00")
        ).date()
    elif hasattr(conversion_at, "date"):
        conversion_at = conversion_at.date()
    recorded_purchase_value = Decimal(recorded_purchase_value)
    if recorded_purchase_value < 0:
        raise ValueError("recorded_purchase_value must be >= 0")

    holding_values = _holding_value_per_member_as_of(conversion_at)
    total_value = sum(holding_values.values())
    if total_value <= 0:
        # No holdings at conversion: create asset with no shares (or skip)
        asset = Asset.objects.create(
            name=name,
            recorded_purchase_value=recorded_purchase_value,
            conversion_at=conversion_at,
            source_investment_id=source_investment_id,
            created_by=created_by,
        )
        return asset

    source_investment = None
    if source_investment_id is not None:
        source_investment = Investment.objects.filter(pk=source_investment_id).first()

    asset = Asset.objects.create(
        name=name,
        recorded_purchase_value=recorded_purchase_value,
        conversion_at=conversion_at,
        source_investment=source_investment,
        created_by=created_by,
    )

    for member_id, value in holding_values.items():
        if value <= 0:
            continue
        share_pct = (value / total_value) * Decimal("100")
        AssetShare.objects.create(
            asset=asset,
            member_id=member_id,
            share_percentage=share_pct,
        )
    return asset
