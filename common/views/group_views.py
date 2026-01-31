"""
GET /group/aggregates/ — group-level aggregates (thin view, calls PositionService).
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsMemberReadOwnAndAggregates
from common.services.position_service import get_group_aggregates


class GroupAggregatesView(APIView):
    """
    GET: Return group aggregates (total_members, total_pool). No per-member data.
    Requires authenticated user with linked Member and MEMBER role.
    """

    permission_classes = [IsAuthenticated, IsMemberReadOwnAndAggregates]

    def get(self, request):
        """
        Get group aggregates
        """
        data = get_group_aggregates()
        return Response(data)
