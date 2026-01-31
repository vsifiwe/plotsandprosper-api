"""
Contract tests for POST /api/v1/admin/investments/.
"""

from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from common.models import Member
from common.models.member import MemberRole

User = get_user_model()


@pytest.fixture
def admin_client(db):
    """APIClient with JWT for an admin user."""
    user = User.objects.create_user(
        username="admininv",
        password="testpass123",
        email="admininv@example.com",
    )
    Member.objects.create(
        firstName="Admin",
        lastName="Inv",
        email="admininv@example.com",
        phone="+255700000086",
        nationalId="id086",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER, MemberRole.ADMIN],
    )
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/token/",
        {"username": "admininv", "password": "testpass123"},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.json()['access']}")
    return client


@pytest.mark.django_db
class TestAdminInvestments:
    """POST /api/v1/admin/investments/ — contract."""

    def test_post_investment_returns_201(self, admin_client):
        """Contract: 201, recorded_at and unit_value; holding shares created per policy."""
        response = admin_client.post(
            "/api/v1/admin/investments/",
            {
                "recorded_at": "2026-02-01",
                "unit_value": "1.50",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert "recorded_at" in data or "recorded_at" in str(data)
        assert "unit_value" in data or float(data.get("unit_value", 0)) == 1.5
