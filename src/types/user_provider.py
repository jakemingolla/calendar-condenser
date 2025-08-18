from abc import ABC, abstractmethod
from typing import Self

from pydantic import BaseModel

from src.types.user import User, UserId


class UserProvider(ABC, BaseModel):
    @abstractmethod
    def get_user(self: Self, user_id: UserId) -> User:
        """Get a user by their ID.

        Args:
            user_id: The ID of the user to get.

        Returns:
            The user with the given ID.

        Raises:
            UserNotFoundError: If the user is not found.

        """
        raise NotImplementedError


class UserNotFoundError(Exception):
    def __init__(self: Self, user_id: UserId) -> None:
        """Initialize the error with the user ID that was not found."""
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")
