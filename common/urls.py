# common/urls.py — API v1 routes (optional trailing slash for all paths)
from django.urls import re_path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    AssetCreateView,
    BuyOutCreateView,
    ContributionCreateView,
    ContributionWindowListCreateView,
    ExitRequestListCreateView,
    GroupAggregatesView,
    InvestmentCreateView,
    MemberListCreateView,
    MemberPositionView,
    MemberStatementView,
    PenaltyCreateView,
    ReversalCreateView,
    test_view,
)

# Use ? for optional trailing slash so POST without slash works (APPEND_SLASH=False).
urlpatterns = [
    re_path(r"^auth/token/?$", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path(r"^auth/token/refresh/?$", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"^me/position/?$", MemberPositionView.as_view(), name="me_position"),
    re_path(r"^me/statement/?$", MemberStatementView.as_view(), name="me_statement"),
    re_path(r"^group/aggregates/?$", GroupAggregatesView.as_view(), name="group_aggregates"),
    re_path(
        r"^admin/members/?$",
        MemberListCreateView.as_view(),
        name="admin_members",
    ),
    re_path(
        r"^admin/contribution-windows/?$",
        ContributionWindowListCreateView.as_view(),
        name="admin_contribution_windows",
    ),
    re_path(
        r"^admin/contributions/?$",
        ContributionCreateView.as_view(),
        name="admin_contributions",
    ),
    re_path(
        r"^admin/penalties/?$",
        PenaltyCreateView.as_view(),
        name="admin_penalties",
    ),
    re_path(
        r"^admin/investments/?$",
        InvestmentCreateView.as_view(),
        name="admin_investments",
    ),
    re_path(
        r"^admin/assets/?$",
        AssetCreateView.as_view(),
        name="admin_assets",
    ),
    re_path(
        r"^admin/reversals/?$",
        ReversalCreateView.as_view(),
        name="admin_reversals",
    ),
    re_path(
        r"^admin/exit-requests/?$",
        ExitRequestListCreateView.as_view(),
        name="admin_exit_requests",
    ),
    re_path(
        r"^admin/buy-outs/?$",
        BuyOutCreateView.as_view(),
        name="admin_buy_outs",
    ),
    re_path(r"^test/?$", test_view, name="test"),
]
