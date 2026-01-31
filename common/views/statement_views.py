"""
GET /me/statement/ — member's historical statement (contributions, penalties,
investments, exits) for date range; member own only.
"""

from datetime import datetime

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsMemberReadOwnAndAggregates, get_member
from common.services.statement_service import get_member_statement


class MemberStatementView(APIView):
    """
    GET: Return member's historical statement for date range (from_date, to_date).
    Requires authenticated user with linked Member and MEMBER role.
    """

    permission_classes = [IsAuthenticated, IsMemberReadOwnAndAggregates]

    def get(self, request: Request):
        """Get member statement; query params from_date, to_date (YYYY-MM-DD)."""
        member = get_member(request.user)
        if not member:
            return Response(
                {"detail": "Member profile not found."},
                status=status.HTTP_403_FORBIDDEN,
            )
        from_date_str = request.query_params.get("from_date")
        to_date_str = request.query_params.get("to_date")
        from_date = None
        to_date = None
        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "from_date must be YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if to_date_str:
            try:
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "to_date must be YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if from_date and to_date and from_date > to_date:
            return Response(
                {"detail": "from_date must be before or equal to to_date."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = get_member_statement(member, from_date=from_date, to_date=to_date)
        return Response(data)
