from fastapi import APIRouter

from src.domains.mock_user.mock_user_provider import MockUserProvider
from src.types.user import User, UserId

router = APIRouter()


@router.get("/users/{user_id:uuid}")
async def get_user(user_id: UserId) -> User:
    return MockUserProvider().get_user(user_id)
