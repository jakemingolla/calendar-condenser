"""Unit tests for MockUserProvider class."""

from uuid import uuid4

import pytest

from src.domains.user.mock_user_provider import (
    MockUserProvider,
    adams_user,
    adams_user_id,
    me,
    my_user_id,
    pauls_user,
    pauls_user_id,
    sallys_user,
    sallys_user_id,
)
from src.types.user import UserId
from src.types.user_provider import UserNotFoundError


@pytest.fixture
def user_provider() -> MockUserProvider:
    """Create a MockUserProvider instance for testing."""
    return MockUserProvider()


@pytest.fixture
def nonexistent_user_id() -> UserId:
    """Create a nonexistent user ID for testing error conditions."""
    return UserId(uuid4())


def test_get_user_me(user_provider: MockUserProvider):
    """Test getting the 'me' user."""
    user = user_provider.get_user(my_user_id)

    assert user.id == my_user_id
    assert user.given_name == "Randall Kleiser"
    assert user.timezone == "America/New_York"
    assert user.preffered_working_hours == (9, 17)
    assert "https://" in user.avatar_url


def test_get_user_nonexistent_raises_error(user_provider: MockUserProvider, nonexistent_user_id: UserId):
    """Test that getting a nonexistent user raises UserNotFoundError."""
    with pytest.raises(UserNotFoundError) as exc_info:
        user_provider.get_user(nonexistent_user_id)
    assert str(exc_info.value) == f"User {nonexistent_user_id} not found"


def test_get_user_all_predefined_users(user_provider: MockUserProvider):
    """Test getting all predefined users in one test."""
    predefined_users = [
        (my_user_id, me),
        (adams_user_id, adams_user),
        (sallys_user_id, sallys_user),
        (pauls_user_id, pauls_user),
    ]

    for user_id, expected_user in predefined_users:
        user = user_provider.get_user(user_id)
        assert user == expected_user
        assert user.id == user_id


def test_get_user_ids_unique():
    """Test that all predefined user IDs are unique."""
    user_ids = [my_user_id, adams_user_id, sallys_user_id, pauls_user_id]
    assert len(set(user_ids)) == len(user_ids)
