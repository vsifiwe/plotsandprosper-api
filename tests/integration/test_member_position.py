"""
Integration tests for member position (US1).
Authenticated member GET /me/position/, GET /group/aggregates/, RBAC.
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
    """User linked to a Member with MEMBER role."""
    user = User.objects.create_user(
        username="member1",
        password="testpass123",
        email="member1@example.com",
    )
    member = Member.objects.create(
        firstName="Jane",
        lastName="Doe",
        email="member1@example.com",
        phone="+255700000001",
        nationalId="id001",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER],
    )
    return user, member


@pytest.fixture
def api_client_with_auth(member_user):
    """APIClient authenticated as member_user with JWT."""
    user, _ = member_user
    client = APIClient()
    response = client.post(
        "/api/v1/auth/token/",
        {"username": "member1", "password": "testpass123"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
class TestMemberPosition:
    """GET /api/v1/me/position/ — member's own financial position."""

    def test_authenticated_member_gets_position(self, api_client_with_auth):
        """Authenticated member receives position with totals and disclaimer."""
        client = api_client_with_auth
        response = client.get("/api/v1/me/position/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "contributions_total" in data
        assert "penalties_total" in data
        assert "holdings_breakdown" in data
        assert "assets_breakdown" in data
        assert "exit_request" in data
        assert "source_of_truth_disclaimer" in data
        assert isinstance(data["contributions_total"], (int, float))
        assert isinstance(data["penalties_total"], (int, float))
        assert isinstance(data["holdings_breakdown"], list)
        assert isinstance(data["assets_breakdown"], list)

    def test_unauthenticated_gets_403(self):
        """Unauthenticated request returns 403."""
        client = APIClient()
        response = client.get("/api/v1/me/position/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_without_member_gets_403(self, db):
        """User with no linked Member gets 403."""
        User.objects.create_user(
            username="nomember",
            password="testpass123",
            email="nomember@example.com",
        )
        client = APIClient()
        response = client.post(
            "/api/v1/auth/token/",
            {"username": "nomember", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/v1/me/position/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGroupAggregates:
    """GET /api/v1/group/aggregates/ — group-level aggregates."""

    def test_authenticated_member_gets_aggregates(self, api_client_with_auth):
        """Authenticated member receives group aggregates."""
        client = api_client_with_auth
        response = client.get("/api/v1/group/aggregates/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_members" in data
        assert "total_pool" in data
        assert isinstance(data["total_members"], int)
        assert isinstance(data["total_pool"], (int, float))

    def test_unauthenticated_gets_403(self):
        """Unauthenticated request returns 403."""
        client = APIClient()
        response = client.get("/api/v1/group/aggregates/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
