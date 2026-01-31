"""
Integration tests for statement export and transparency (US5).
GET /me/statement/, disclaimer in /me/position/, auditor 403 on POST admin.
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
def member_user(db):
    """User linked to Member with MEMBER role."""
    user = User.objects.create_user(
        username="member_stmt",
        password="testpass123",
        email="member_stmt@example.com",
    )
    member = Member.objects.create(
        firstName="Member",
        lastName="Stmt",
        email="member_stmt@example.com",
        phone="+255700000030",
        nationalId="id030",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER],
    )
    return user, member


@pytest.fixture
def admin_user(db):
    """User linked to Member with ADMIN role."""
    user = User.objects.create_user(
        username="admin_stmt",
        password="testpass123",
        email="admin_stmt@example.com",
    )
    member = Member.objects.create(
        firstName="Admin",
        lastName="Stmt",
        email="admin_stmt@example.com",
        phone="+255700000031",
        nationalId="id031",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER, MemberRole.ADMIN],
    )
    return user, member


@pytest.fixture
def auditor_user(db):
    """User linked to Member with AUDITOR role only (no ADMIN)."""
    user = User.objects.create_user(
        username="auditor_stmt",
        password="testpass123",
        email="auditor_stmt@example.com",
    )
    member = Member.objects.create(
        firstName="Auditor",
        lastName="Stmt",
        email="auditor_stmt@example.com",
        phone="+255700000032",
        nationalId="id032",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.AUDITOR],
    )
    return user, member


@pytest.fixture
def member_client(member_user):
    """APIClient authenticated as member with JWT."""
    user, _ = member_user
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/token/",
        {"username": "member_stmt", "password": "testpass123"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.json()['access']}")
    return client


@pytest.fixture
def auditor_client(auditor_user):
    """APIClient authenticated as auditor with JWT."""
    user, _ = auditor_user
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/token/",
        {"username": "auditor_stmt", "password": "testpass123"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.json()['access']}")
    return client


@pytest.fixture
def admin_client(admin_user):
    """APIClient authenticated as admin with JWT."""
    user, _ = admin_user
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/token/",
        {"username": "admin_stmt", "password": "testpass123"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.json()['access']}")
    return client


@pytest.mark.django_db
class TestStatementTransparency:
    """Statement export, disclaimer in position, auditor read-only."""

    def test_get_me_statement_returns_200_and_structure(self, member_client):
        """GET /me/statement/ returns 200 and contributions, penalties, investments, exits."""
        response = member_client.get("/api/v1/me/statement/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "contributions" in data
        assert "penalties" in data
        assert "investments" in data
        assert "exit_requests" in data
        assert "buy_outs" in data
        assert isinstance(data["contributions"], list)
        assert isinstance(data["penalties"], list)
        assert isinstance(data["investments"], list)
        assert isinstance(data["exit_requests"], list)
        assert isinstance(data["buy_outs"], list)

    def test_get_me_statement_with_date_range(self, member_client):
        """GET /me/statement/?from_date=2025-01-01&to_date=2025-12-31 returns 200."""
        response = member_client.get(
            "/api/v1/me/statement/",
            {"from_date": "2025-01-01", "to_date": "2025-12-31"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("from_date") == "2025-01-01"
        assert data.get("to_date") == "2025-12-31"

    def test_me_position_includes_source_of_truth_disclaimer(self, member_client):
        """GET /me/position/ includes source_of_truth_disclaimer string."""
        response = member_client.get("/api/v1/me/position/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "source_of_truth_disclaimer" in data
        assert isinstance(data["source_of_truth_disclaimer"], str)
        assert len(data["source_of_truth_disclaimer"]) > 0

    def test_auditor_post_admin_returns_403(
        self,
        auditor_client,
        member_user,
    ):
        """Auditor cannot POST to admin endpoints; returns 403."""
        _, member = member_user
        response = auditor_client.post(
            "/api/v1/admin/contributions/",
            {
                "member_id": member.id,
                "window_id": 1,
                "amount": "100.00",
                "recorded_at": "2026-01-14T10:00:00Z",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auditor_post_exit_requests_returns_403(
        self,
        auditor_client,
        member_user,
    ):
        """Auditor cannot POST /admin/exit-requests/; returns 403."""
        _, member = member_user
        response = auditor_client.post(
            "/api/v1/admin/exit-requests/",
            {"member_id": member.id},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
