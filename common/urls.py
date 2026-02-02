# common/urls.py — API v1 routes
from django.urls import path
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
    MemberPositionView,
    MemberStatementView,
    PenaltyCreateView,
    ReversalCreateView,
    test_view,
)

urlpatterns = [
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/position/", MemberPositionView.as_view(), name="me_position"),
    path("me/statement/", MemberStatementView.as_view(), name="me_statement"),
    path("group/aggregates/", GroupAggregatesView.as_view(), name="group_aggregates"),
    path(
        "admin/contribution-windows/",
        ContributionWindowListCreateView.as_view(),
        name="admin_contribution_windows",
    ),
    path(
        "admin/contributions/",
        ContributionCreateView.as_view(),
        name="admin_contributions",
    ),
    path(
        "admin/penalties/",
        PenaltyCreateView.as_view(),
        name="admin_penalties",
    ),
    path(
        "admin/investments/",
        InvestmentCreateView.as_view(),
        name="admin_investments",
    ),
    path(
        "admin/assets/",
        AssetCreateView.as_view(),
        name="admin_assets",
    ),
    path(
        "admin/reversals/",
        ReversalCreateView.as_view(),
        name="admin_reversals",
    ),
    path(
        "admin/exit-requests/",
        ExitRequestListCreateView.as_view(),
        name="admin_exit_requests",
    ),
    path(
        "admin/buy-outs/",
        BuyOutCreateView.as_view(),
        name="admin_buy_outs",
    ),
    path("test/", test_view, name="test"),
]
