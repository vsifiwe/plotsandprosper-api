# common/urls.py — API v1 routes
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import GroupAggregatesView, MemberPositionView, test_view

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/position/", MemberPositionView.as_view(), name="me_position"),
    path("group/aggregates/", GroupAggregatesView.as_view(), name="group_aggregates"),
    path("test/", test_view, name="test"),
]
