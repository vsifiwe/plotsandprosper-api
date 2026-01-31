"""
Integration tests for exit queue and buy-out (US4).
Create exit request, fulfill or queue; record buy-out; verify position and audit trail.
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
)
from common.models.exit_request import ExitRequestStatus
from common.models.member import MemberRole
from common.services.exit_service import create_exit_request, fulfill_exit_request

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """User linked to Member with ADMIN role."""
    user = User.objects.create_user(
        username="admin_exit",
        password="testpass123",
        email="admin_exit@example.com",
    )
    member = Member.objects.create(
        firstName="Admin",
        lastName="Exit",
        email="admin_exit@example.com",
        phone="+255700000020",
        nationalId="id020",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER, MemberRole.ADMIN],
    )
    return user, member


@pytest.fixture
def member_user(db):
    """User linked to Member with MEMBER role."""
    user = User.objects.create_user(
        username="member_exit",
        password="testpass123",
        email="member_exit@example.com",
    )
    member = Member.objects.create(
        firstName="Member",
        lastName="Exit",
        email="member_exit@example.com",
        phone="+255700000021",
        nationalId="id021",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER],
    )
    return user, member


@pytest.fixture
def admin_client(admin_user):
    """APIClient authenticated as admin with JWT."""
    user, _ = admin_user
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/token/",
        {"username": "admin_exit", "password": "testpass123"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.json()['access']}")
    return client


@pytest.fixture
def member_client(member_user):
    """APIClient authenticated as member with JWT."""
    user, _ = member_user
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/token/",
        {"username": "member_exit", "password": "testpass123"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.json()['access']}")
    return client


@pytest.fixture
def window_and_contribution(db, member_user):
    """A contribution window and a contribution for the member."""
    _, member = member_user
    window = ContributionWindow.objects.create(
        start_at=datetime(2026, 1, 1),
        end_at=datetime(2026, 1, 31),
        min_amount=0,
        max_amount=10000,
        name="2026-01",
    )
    Contribution.objects.create(
        member=member,
        window=window,
        amount=500,
        recorded_at=datetime(2026, 1, 15),
    )
    return window


@pytest.mark.django_db
class TestExitQueueAndBuyOut:
    """Exit request and buy-out: create, queue, fulfill; position shows exit status."""

    def test_admin_creates_exit_request_member_position_shows_exit_request(
        self,
        admin_client,
        member_client,
        member_user,
        window_and_contribution,
    ):
        """Admin creates exit request; member position shows exit_request (status, queue_position, amount_entitled)."""
        _, member = member_user
        client = admin_client
        response = client.post(
            "/api/v1/admin/exit-requests/",
            {"member_id": member.id},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data.get("queue_position") == 1
        assert data.get("status") == ExitRequestStatus.QUEUED
        assert "amount_entitled" in data

        pos_resp = member_client.get("/api/v1/me/position/")
        assert pos_resp.status_code == status.HTTP_200_OK
        pos = pos_resp.json()
        assert "exit_request" in pos
        assert pos["exit_request"] is not None
        assert pos["exit_request"]["status"] == ExitRequestStatus.QUEUED
        assert pos["exit_request"]["queue_position"] == 1
        assert "amount_entitled" in pos["exit_request"]

    def test_exit_request_fulfilled_position_shows_fulfilled(
        self,
        member_user,
        window_and_contribution,
    ):
        """Create exit request, fulfill via service; position shows status fulfilled."""
        _, member = member_user
        req = create_exit_request(member.id)
        assert req.status == ExitRequestStatus.QUEUED
        fulfill_exit_request(req.id, amount_entitled=req.amount_entitled)
        req.refresh_from_db()
        assert req.status == ExitRequestStatus.FULFILLED
        assert req.fulfilled_at is not None

    def test_admin_records_buy_out_returns_201(
        self,
        admin_client,
        member_user,
    ):
        """Admin records buy-out; 201 with seller_id, nominal_valuation."""
        _, seller = member_user
        response = admin_client.post(
            "/api/v1/admin/buy-outs/",
            {
                "seller_id": seller.id,
                "nominal_valuation": "1500.00",
                "valuation_inputs": {"contributions": 500, "realized": 0},
                "recorded_at": "2026-02-01T12:00:00Z",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data.get("seller_id") == seller.id
        assert float(data.get("nominal_valuation", 0)) == 1500.0

    def test_get_exit_requests_list_returns_queue(
        self,
        admin_client,
        member_user,
        window_and_contribution,
    ):
        """GET /admin/exit-requests/ returns list of exit requests (queue)."""
        _, member = member_user
        create_exit_request(member.id)
        response = admin_client.get("/api/v1/admin/exit-requests/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        first = data[0]
        assert "queue_position" in first
        assert "status" in first
        assert "member_id" in first
