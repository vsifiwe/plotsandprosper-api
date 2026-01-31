"""
Contract tests for GET /api/v1/me/position/ (OpenAPI MemberPosition schema).
"""

from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from common.models import Member
from common.models.member import MemberRole

User = get_user_model()


@pytest.mark.django_db
class TestMePositionContract:
    """GET /api/v1/me/position/ — response schema and 403 when unauthenticated."""

    def test_response_schema_member_position(self):
        """
        Response matches MemberPosition: contributions_total,
        penalties_total, holdings_breakdown, assets_breakdown,
        exit_request, source_of_truth_disclaimer.
        """
        user = User.objects.create_user(
            username="contractpos",
            password="testpass123",
            email="contractpos@example.com",
        )
        Member.objects.create(
            firstName="Contract",
            lastName="User",
            email="contractpos@example.com",
            phone="+255700000099",
            nationalId="id099",
            joinDate=date(2025, 1, 1),
            user=user,
            roles=[MemberRole.MEMBER],
        )
        client = APIClient()
        response = client.post(
            "/api/v1/auth/token/",
            {"username": "contractpos", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = client.get("/api/v1/me/position/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "contributions_total" in data
        assert "penalties_total" in data
        assert "holdings_breakdown" in data
        assert "assets_breakdown" in data
        assert "exit_request" in data
        assert "source_of_truth_disclaimer" in data
        assert isinstance(data["holdings_breakdown"], list)
        assert isinstance(data["assets_breakdown"], list)
        assert isinstance(data["source_of_truth_disclaimer"], str)

    def test_unauthenticated_returns_403(self):
        """Unauthenticated GET /me/position/ returns 403."""
        client = APIClient()
        response = client.get("/api/v1/me/position/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
