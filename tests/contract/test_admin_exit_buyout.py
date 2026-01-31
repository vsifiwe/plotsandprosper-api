"""
Contract tests for POST /api/v1/admin/exit-requests/ and POST /api/v1/admin/buy-outs/.
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
        username="adminexit",
        password="testpass123",
        email="adminexit@example.com",
    )
    Member.objects.create(
        firstName="Admin",
        lastName="Exit",
        email="adminexit@example.com",
        phone="+255700000090",
        nationalId="id090",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER, MemberRole.ADMIN],
    )
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/token/",
        {"username": "adminexit", "password": "testpass123"},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.json()['access']}")
    return client


@pytest.fixture
def member_for_exit(db):
    """A member to create exit request for."""
    user = User.objects.create_user(
        username="memberexit",
        password="testpass123",
        email="memberexit@example.com",
    )
    member = Member.objects.create(
        firstName="Member",
        lastName="Exit",
        email="memberexit@example.com",
        phone="+255700000091",
        nationalId="id091",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER],
    )
    return member


@pytest.mark.django_db
class TestAdminExitRequests:
    """POST /api/v1/admin/exit-requests/ — contract."""

    def test_post_exit_request_returns_201(self, admin_client, member_for_exit):
        """Contract: 201, body has id, queue_position, status; queue position assigned."""
        response = admin_client.post(
            "/api/v1/admin/exit-requests/",
            {"member_id": member_for_exit.id},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert "queue_position" in data
        assert "status" in data
        assert data.get("status") == "queued"

    def test_get_exit_requests_returns_200(self, admin_client):
        """GET /admin/exit-requests/ returns 200 and list."""
        response = admin_client.get("/api/v1/admin/exit-requests/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)


@pytest.mark.django_db
class TestAdminBuyOuts:
    """POST /api/v1/admin/buy-outs/ — contract."""

    def test_post_buy_out_returns_201(self, admin_client, member_for_exit):
        """Contract: 201, body has id, seller_id, nominal_valuation."""
        response = admin_client.post(
            "/api/v1/admin/buy-outs/",
            {
                "seller_id": member_for_exit.id,
                "nominal_valuation": "1000.00",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data.get("seller_id") == member_for_exit.id
        assert float(data.get("nominal_valuation", 0)) == 1000.0
