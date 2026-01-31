"""
Contract tests for POST /api/v1/admin/contributions/ and POST /api/v1/admin/penalties/.
"""

from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from common.models import ContributionWindow, Member
from common.models.member import MemberRole

User = get_user_model()


@pytest.fixture
def admin_client(db):
    """APIClient with JWT for an admin user."""
    user = User.objects.create_user(
        username="admincontract",
        password="testpass123",
        email="admincontract@example.com",
    )
    Member.objects.create(
        firstName="Admin",
        lastName="Contract",
        email="admincontract@example.com",
        phone="+255700000088",
        nationalId="id088",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER, MemberRole.ADMIN],
    )
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/token/",
        {"username": "admincontract", "password": "testpass123"},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.json()['access']}")
    return client


@pytest.fixture
def member_and_window(db):
    """A member and a contribution window."""
    user = User.objects.create_user(
        username="membercontract",
        password="testpass123",
        email="membercontract@example.com",
    )
    member = Member.objects.create(
        firstName="Member",
        lastName="Contract",
        email="membercontract@example.com",
        phone="+255700000087",
        nationalId="id087",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER],
    )
    from datetime import datetime

    window = ContributionWindow.objects.create(
        start_at=datetime(2026, 1, 1),
        end_at=datetime(2026, 1, 31),
        min_amount=0,
        max_amount=10000,
        name="2026-01",
    )
    return member, window


@pytest.mark.django_db
class TestAdminContributions:
    """POST /api/v1/admin/contributions/ — contract."""

    def test_post_contribution_returns_201(self, admin_client, member_and_window):
        """Contract: 201, body has id and payload fields."""
        member, window = member_and_window
        response = admin_client.post(
            "/api/v1/admin/contributions/",
            {
                "member_id": str(member.id),
                "window_id": window.id,
                "amount": "300.50",
                "recorded_at": "2026-01-14T10:00:00Z",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data.get("amount") == "300.5000" or float(data.get("amount", 0)) == 300.5

    def test_post_contribution_invalid_window_returns_400(
        self, admin_client, member_and_window
    ):
        """Invalid window_id returns 400."""
        member, _ = member_and_window
        response = admin_client.post(
            "/api/v1/admin/contributions/",
            {
                "member_id": str(member.id),
                "window_id": 99999,
                "amount": "100.00",
                "recorded_at": "2026-01-14T10:00:00Z",
            },
            format="json",
        )
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        )


@pytest.mark.django_db
class TestAdminPenalties:
    """POST /api/v1/admin/penalties/ — contract."""

    def test_post_penalty_returns_201(self, admin_client, member_and_window):
        """Contract: 201, body has id and amount."""
        member, _ = member_and_window
        response = admin_client.post(
            "/api/v1/admin/penalties/",
            {
                "member_id": str(member.id),
                "amount": "25.00",
                "reason": "late payment",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert float(data.get("amount", 0)) == 25.0 or data.get("amount") == "25.0000"
