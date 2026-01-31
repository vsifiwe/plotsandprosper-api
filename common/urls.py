# common/urls.py — API v1 routes
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ContributionCreateView,
    ContributionWindowListCreateView,
    GroupAggregatesView,
    InvestmentCreateView,
    MemberPositionView,
    PenaltyCreateView,
    ReversalCreateView,
    test_view,
)

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/position/", MemberPositionView.as_view(), name="me_position"),
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
        "admin/reversals/",
        ReversalCreateView.as_view(),
        name="admin_reversals",
    ),
    path("test/", test_view, name="test"),
]
