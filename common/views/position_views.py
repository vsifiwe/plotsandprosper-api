"""
GET /me/position/ — member's own financial position (thin view, calls PositionService).
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsMemberReadOwnAndAggregates, get_member
from common.services.position_service import get_member_position


class MemberPositionView(APIView):
    """
    GET: Return member's financial position
    (contributions, penalties, holdings, assets, exit, disclaimer).
    Requires authenticated user with linked Member and MEMBER role.
    """

    permission_classes = [IsAuthenticated, IsMemberReadOwnAndAggregates]

    def get(self, request):
        """
        Get member position
        """
        member = get_member(request.user)
        if not member:
            return Response(
                {"detail": "Member profile not found."},
                status=status.HTTP_403_FORBIDDEN,
            )
        data = get_member_position(member)
        return Response(data)
