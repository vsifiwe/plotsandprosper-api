"""
Contract tests for auth endpoints (OpenAPI: /auth/token/, /auth/token/refresh/).
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestAuthToken:
    """POST /api/v1/auth/token/ — obtain JWT pair."""

    def test_obtain_token_returns_access_and_refresh(self):
        """Contract: 200, body has access and refresh strings."""
        User.objects.create_user(
            username="contractuser",
            password="testpass123",
            email="contract@example.com",
        )
        client = APIClient()
        response = client.post(
            "/api/v1/auth/token/",
            {"username": "contractuser", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert isinstance(data["access"], str)
        assert isinstance(data["refresh"], str)
        assert len(data["access"]) > 0
        assert len(data["refresh"]) > 0

    def test_obtain_token_invalid_credentials_returns_401(self):
        """Invalid username/password returns 401."""
        client = APIClient()
        response = client.post(
            "/api/v1/auth/token/",
            {"username": "nobody", "password": "wrong"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_obtain_token_missing_fields_returns_400(self):
        """Missing username or password returns 400."""
        client = APIClient()
        response = client.post(
            "/api/v1/auth/token/",
            {"username": "only"},
            format="json",
        )
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        )


@pytest.mark.django_db
class TestAuthTokenRefresh:
    """POST /api/v1/auth/token/refresh/ — refresh access token."""

    def test_refresh_token_returns_new_access(self):
        """Contract: 200, body has access string."""
        user = User.objects.create_user(
            username="refreshuser",
            password="testpass123",
            email="refresh@example.com",
        )
        client = APIClient()
        # Obtain refresh token first
        obtain = client.post(
            "/api/v1/auth/token/",
            {"username": "refreshuser", "password": "testpass123"},
            format="json",
        )
        assert obtain.status_code == status.HTTP_200_OK
        refresh = obtain.json()["refresh"]

        response = client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert isinstance(data["access"], str)
        assert len(data["access"]) > 0
