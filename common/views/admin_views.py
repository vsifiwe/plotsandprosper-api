"""
Admin-only views: contribution windows, contributions, penalties, investments,
assets, reversals, exit-requests, buy-outs.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.models import ContributionWindow, Member, Reversal
from common.permissions import IsAdmin
from common.services.asset_service import record_asset
from common.services.contribution_service import (
    record_contribution,
    record_penalty,
)
from common.services.exit_service import create_exit_request
from common.services.investment_service import record_investment
from common.services.buyout_service import record_buyout
from common.models.reversal import ReversalRecordType


class ContributionWindowListCreateView(APIView):
    """GET and POST /admin/contribution-windows/ — admin only."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request: Request):
        """List contribution windows."""
        windows = ContributionWindow.objects.all().order_by("-start_at")[:100]
        data = [
            {
                "id": w.id,
                "name": w.name,
                "start_at": w.start_at.isoformat(),
                "end_at": w.end_at.isoformat(),
                "min_amount": str(w.min_amount),
                "max_amount": str(w.max_amount) if w.max_amount is not None else None,
            }
            for w in windows
        ]
        return Response(data)

    def post(self, request: Request):
        """Create contribution window."""
        start_at = request.data.get("start_at")
        end_at = request.data.get("end_at")
        min_amount = request.data.get("min_amount", 0)
        max_amount = request.data.get("max_amount")
        name = request.data.get("name", "")
        if not start_at or not end_at:
            return Response(
                {"detail": "start_at and end_at required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from django.utils.dateparse import parse_datetime

        start_at = parse_datetime(start_at)
        end_at = parse_datetime(end_at)
        if not start_at or not end_at:
            return Response(
                {"detail": "Invalid start_at or end_at"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        w = ContributionWindow.objects.create(
            start_at=start_at,
            end_at=end_at,
            min_amount=min_amount,
            max_amount=max_amount,
            name=name,
        )
        return Response(
            {
                "id": w.id,
                "name": w.name,
                "start_at": w.start_at.isoformat(),
                "end_at": w.end_at.isoformat(),
                "min_amount": str(w.min_amount),
                "max_amount": str(w.max_amount) if w.max_amount is not None else None,
            },
            status=status.HTTP_201_CREATED,
        )


class ContributionCreateView(APIView):
    """POST /admin/contributions/ — admin only, immutable."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request):
        """Record contribution."""
        member_id = request.data.get("member_id")
        window_id = request.data.get("window_id")
        amount = request.data.get("amount")
        recorded_at = request.data.get("recorded_at")
        if not all([member_id, window_id, amount is not None]):
            return Response(
                {"detail": "member_id, window_id, amount required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from django.utils.dateparse import parse_datetime

            rec_at = parse_datetime(recorded_at) if recorded_at else None
            contrib = record_contribution(
                member_id=member_id,
                window_id=int(window_id),
                amount=amount,
                recorded_at=rec_at,
                created_by=request.user,
            )
            return Response(
                {
                    "id": contrib.id,
                    "member_id": str(contrib.member_id),
                    "window_id": contrib.window_id,
                    "amount": str(contrib.amount),
                    "recorded_at": contrib.recorded_at.isoformat(),
                },
                status=status.HTTP_201_CREATED,
            )
        except (ValueError, ContributionWindow.DoesNotExist, Member.DoesNotExist) as e:
            return Response(
                {
                    "detail": (
                        str(e)
                        if isinstance(e, ValueError)
                        else "Window or member not found"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class PenaltyCreateView(APIView):
    """POST /admin/penalties/ — admin only, immutable."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request):
        """Record penalty."""
        member_id = request.data.get("member_id")
        amount = request.data.get("amount")
        reason = request.data.get("reason", "")
        window_id = request.data.get("window_id")
        recorded_at = request.data.get("recorded_at")
        if not member_id or amount is None:
            return Response(
                {"detail": "member_id, amount required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from django.utils.dateparse import parse_datetime

            rec_at = parse_datetime(recorded_at) if recorded_at else None
            penalty = record_penalty(
                member_id=member_id,
                amount=amount,
                reason=reason,
                window_id=int(window_id) if window_id is not None else None,
                recorded_at=rec_at,
                created_by=request.user,
            )
            return Response(
                {
                    "id": penalty.id,
                    "member_id": str(penalty.member_id),
                    "amount": str(penalty.amount),
                    "reason": penalty.reason,
                    "recorded_at": penalty.recorded_at.isoformat(),
                },
                status=status.HTTP_201_CREATED,
            )
        except (ValueError, Member.DoesNotExist, ContributionWindow.DoesNotExist) as e:
            return Response(
                {
                    "detail": (
                        str(e)
                        if isinstance(e, ValueError)
                        else "Member or window not found"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class InvestmentCreateView(APIView):
    """POST /admin/investments/ — admin only, immutable."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request):
        """Record investment; holding shares created per policy."""
        recorded_at = request.data.get("recorded_at")
        unit_value = request.data.get("unit_value")
        total_units = request.data.get("total_units")
        if not recorded_at or unit_value is None:
            return Response(
                {"detail": "recorded_at, unit_value required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            inv = record_investment(
                recorded_at=recorded_at,
                unit_value=unit_value,
                total_units=total_units,
                created_by=request.user,
            )
            return Response(
                {
                    "id": inv.id,
                    "recorded_at": inv.recorded_at.isoformat(),
                    "unit_value": str(inv.unit_value),
                    "total_units": str(inv.total_units) if inv.total_units else None,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AssetCreateView(APIView):
    """POST /admin/assets/ — admin only, immutable."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request):
        """Record asset conversion; asset shares fixed at conversion."""
        name = request.data.get("name")
        recorded_purchase_value = request.data.get("recorded_purchase_value")
        conversion_at = request.data.get("conversion_at")
        source_investment_id = request.data.get("source_investment_id")
        if not name or recorded_purchase_value is None or not conversion_at:
            return Response(
                {"detail": "name, recorded_purchase_value, conversion_at required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            asset = record_asset(
                name=name,
                recorded_purchase_value=recorded_purchase_value,
                conversion_at=conversion_at,
                source_investment_id=int(source_investment_id)
                if source_investment_id is not None
                else None,
                created_by=request.user,
            )
            return Response(
                {
                    "id": asset.id,
                    "name": asset.name,
                    "recorded_purchase_value": str(asset.recorded_purchase_value),
                    "conversion_at": asset.conversion_at.isoformat(),
                    "source_investment_id": asset.source_investment_id,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReversalCreateView(APIView):
    """POST /admin/reversals/ — admin only; create reversal record only."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request):
        """Create reversal record; original unchanged."""
        original_record_type = request.data.get("original_record_type")
        original_record_id = request.data.get("original_record_id")
        reason = request.data.get("reason", "")
        if not original_record_type or original_record_id is None:
            return Response(
                {"detail": "original_record_type, original_record_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            rev_type = ReversalRecordType(original_record_type)
        except ValueError:
            return Response(
                {"detail": "Invalid original_record_type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rev = Reversal.objects.create(
            original_record_type=rev_type.value,
            original_record_id=int(original_record_id),
            reason=reason,
            created_by=request.user,
        )
        return Response(
            {
                "id": rev.id,
                "original_record_type": rev.original_record_type,
                "original_record_id": rev.original_record_id,
                "reason": rev.reason,
                "created_at": rev.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class ExitRequestListCreateView(APIView):
    """GET and POST /admin/exit-requests/ — admin only."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request: Request):
        """List exit queue (all exit requests, ordered by queue_position)."""
        from common.models import ExitRequest

        requests = ExitRequest.objects.all().order_by("queue_position", "-requested_at")[
            :100
        ]
        data = [
            {
                "id": r.id,
                "member_id": r.member_id,
                "requested_at": r.requested_at.isoformat(),
                "queue_position": r.queue_position,
                "status": r.status,
                "fulfilled_at": r.fulfilled_at.isoformat() if r.fulfilled_at else None,
                "amount_entitled": str(r.amount_entitled),
                "created_at": r.created_at.isoformat(),
            }
            for r in requests
        ]
        return Response(data)

    def post(self, request: Request):
        """Create exit request; queue position assigned FIFO."""
        member_id = request.data.get("member_id")
        if member_id is None:
            return Response(
                {"detail": "member_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            req = create_exit_request(member_id=int(member_id))
            return Response(
                {
                    "id": req.id,
                    "member_id": req.member_id,
                    "requested_at": req.requested_at.isoformat(),
                    "queue_position": req.queue_position,
                    "status": req.status,
                    "fulfilled_at": req.fulfilled_at.isoformat() if req.fulfilled_at else None,
                    "amount_entitled": str(req.amount_entitled),
                    "created_at": req.created_at.isoformat(),
                },
                status=status.HTTP_201_CREATED,
            )
        except Member.DoesNotExist:
            return Response(
                {"detail": "Member not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class BuyOutCreateView(APIView):
    """POST /admin/buy-outs/ — admin only, immutable."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request):
        """Record buy-out (seller, optional buyer, nominal valuation)."""
        seller_id = request.data.get("seller_id")
        buyer_id = request.data.get("buyer_id")
        nominal_valuation = request.data.get("nominal_valuation")
        valuation_inputs = request.data.get("valuation_inputs")
        recorded_at = request.data.get("recorded_at")
        if seller_id is None or nominal_valuation is None:
            return Response(
                {"detail": "seller_id, nominal_valuation required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from django.utils.dateparse import parse_datetime

            rec_at = parse_datetime(recorded_at) if recorded_at else None
            buyout = record_buyout(
                seller_id=int(seller_id),
                nominal_valuation=nominal_valuation,
                buyer_id=int(buyer_id) if buyer_id is not None else None,
                valuation_inputs=valuation_inputs,
                recorded_at=rec_at,
                created_by=request.user,
            )
            return Response(
                {
                    "id": buyout.id,
                    "seller_id": buyout.seller_id,
                    "buyer_id": buyout.buyer_id,
                    "nominal_valuation": str(buyout.nominal_valuation),
                    "valuation_inputs": buyout.valuation_inputs,
                    "recorded_at": buyout.recorded_at.isoformat(),
                    "created_at": buyout.created_at.isoformat(),
                },
                status=status.HTTP_201_CREATED,
            )
        except Member.DoesNotExist:
            return Response(
                {"detail": "Member (seller or buyer) not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
