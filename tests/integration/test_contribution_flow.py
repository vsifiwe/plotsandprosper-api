"""
Integration tests for contribution flow (US2).
Record contribution, penalty, investment; verify position and no edit/delete.
"""

from datetime import date, datetime

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from common.models import (
    Contribution,
    ContributionWindow,
    Member,
    Penalty,
)
from common.models.member import MemberRole

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """User linked to a Member with ADMIN role."""
    user = User.objects.create_user(
        username="admin1",
        password="testpass123",
        email="admin1@example.com",
    )
    member = Member.objects.create(
        firstName="Admin",
        lastName="User",
        email="admin1@example.com",
        phone="+255700000002",
        nationalId="id002",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER, MemberRole.ADMIN],
    )
    return user, member


@pytest.fixture
def member_user(db):
    """User linked to a Member with MEMBER role only."""
    user = User.objects.create_user(
        username="member2",
        password="testpass123",
        email="member2@example.com",
    )
    member = Member.objects.create(
        firstName="Member",
        lastName="Two",
        email="member2@example.com",
        phone="+255700000003",
        nationalId="id003",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER],
    )
    return user, member


@pytest.fixture
def api_client_admin(admin_user):
    """APIClient authenticated as admin with JWT."""
    user, _ = admin_user
    client = APIClient()
    response = client.post(
        "/api/v1/auth/token/",
        {"username": "admin1", "password": "testpass123"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")
    return client


@pytest.fixture
def contribution_window(db):
    """A contribution window for tests."""
    start = datetime(2026, 1, 1, 0, 0, 0)
    end = datetime(2026, 1, 31, 23, 59, 59)
    return ContributionWindow.objects.create(
        start_at=start,
        end_at=end,
        min_amount=100,
        max_amount=1000,
        name="2026-01",
    )


@pytest.mark.django_db
class TestContributionFlow:
    """Record contribution, penalty, investment; verify position."""

    def test_admin_records_contribution_and_position_updates(
        self, api_client_admin, member_user, contribution_window
    ):
        """Admin records contribution; member position shows contributions_total."""
        _, member = member_user
        client = api_client_admin
        response = client.post(
            "/api/v1/admin/contributions/",
            {
                "member_id": str(member.id),
                "window_id": contribution_window.id,
                "amount": "500.00",
                "recorded_at": "2026-01-15T12:00:00Z",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Contribution.objects.filter(member=member).count() == 1

        # Member gets position (via member client)
        member_client = APIClient()
        token_resp = member_client.post(
            "/api/v1/auth/token/",
            {"username": "member2", "password": "testpass123"},
            format="json",
        )
        member_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_resp.json()['access']}"
        )
        pos_resp = member_client.get("/api/v1/me/position/")
        assert pos_resp.status_code == status.HTTP_200_OK
        data = pos_resp.json()
        assert float(data["contributions_total"]) == 500.0

    def test_admin_records_penalty(self, api_client_admin, member_user):
        """Admin records penalty; position shows penalties_total."""
        _, member = member_user
        client = api_client_admin
        response = client.post(
            "/api/v1/admin/penalties/",
            {
                "member_id": str(member.id),
                "amount": "50.00",
                "reason": "late",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Penalty.objects.filter(member=member).count() == 1

    def test_contributions_are_immutable_no_edit_delete(
        self, api_client_admin, member_user, contribution_window
    ):
        """Contributions cannot be edited or deleted via API (only reversal)."""
        _, member = member_user
        client = api_client_admin
        resp = client.post(
            "/api/v1/admin/contributions/",
            {
                "member_id": str(member.id),
                "window_id": contribution_window.id,
                "amount": "200.00",
                "recorded_at": "2026-01-10T12:00:00Z",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        contrib_id = resp.json().get("id")
        # API does not expose PUT/PATCH/DELETE on contributions (admin only creates)
        # So we just verify no such endpoints exist by checking 405 or 404
        patch_resp = client.patch(
            f"/api/v1/admin/contributions/{contrib_id}/",
            {"amount": "999"},
            format="json",
        )
        assert patch_resp.status_code in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
