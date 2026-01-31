"""
Integration tests for asset conversion (US3).
Record asset with shares; position shows asset share and recorded value.
"""

from datetime import date, datetime

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from common.models import (
    Contribution,
    ContributionWindow,
    HoldingShare,
    Investment,
    Member,
)
from common.models.member import MemberRole

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """User linked to Member with ADMIN role."""
    user = User.objects.create_user(
        username="admin_asset",
        password="testpass123",
        email="admin_asset@example.com",
    )
    member = Member.objects.create(
        firstName="Admin",
        lastName="Asset",
        email="admin_asset@example.com",
        phone="+255700000010",
        nationalId="id010",
        joinDate=date(2025, 1, 1),
        user=user,
        roles=[MemberRole.MEMBER, MemberRole.ADMIN],
    )
    return user, member


@pytest.fixture
def member_user(db):
    """User linked to Member with MEMBER role."""
    user = User.objects.create_user(
        username="member_asset",
        password="testpass123",
        email="member_asset@example.com",
    )
    member = Member.objects.create(
        firstName="Member",
        lastName="Asset",
        email="member_asset@example.com",
        phone="+255700000011",
        nationalId="id011",
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
        {"username": "admin_asset", "password": "testpass123"},
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
        {"username": "member_asset", "password": "testpass123"},
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


@pytest.fixture
def investment_with_holding(db, member_user, window_and_contribution):
    """An investment and holding share for the member (so they have eligible savings)."""
    _, member = member_user
    inv = Investment.objects.create(
        recorded_at=date(2026, 2, 1),
        unit_value=1.0,
        total_units=500,
    )
    HoldingShare.objects.create(
        investment=inv,
        member=member,
        units=500,
    )
    return inv


@pytest.mark.django_db
class TestAssetConversion:
    """Record asset with shares; position shows asset share and recorded value."""

    def test_admin_records_asset_and_position_shows_assets_breakdown(
        self,
        admin_client,
        member_client,
        member_user,
        investment_with_holding,
    ):
        """Admin records asset conversion; member position shows assets_breakdown with share and value."""
        _, member = member_user
        client = admin_client
        response = client.post(
            "/api/v1/admin/assets/",
            {
                "name": "Property A",
                "recorded_purchase_value": "100000.00",
                "conversion_at": "2026-03-01",
                "source_investment_id": investment_with_holding.id,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data.get("name") == "Property A"

        # Member gets position with assets_breakdown
        pos_resp = member_client.get("/api/v1/me/position/")
        assert pos_resp.status_code == status.HTTP_200_OK
        pos = pos_resp.json()
        assert "assets_breakdown" in pos
        assert isinstance(pos["assets_breakdown"], list)
        assert len(pos["assets_breakdown"]) >= 1
        asset_item = pos["assets_breakdown"][0]
        assert "asset_id" in asset_item
        assert "share_percentage" in asset_item
        assert "recorded_purchase_value" in asset_item
