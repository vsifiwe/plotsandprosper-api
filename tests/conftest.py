"""
Pytest configuration for Plots & Prosper backend.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def django_db_setup():
    """Use real DB for tests that need it (integration/contract)."""
    pass
