from fastapi import APIRouter, HTTPException

from src.domains.mock_user.mock_user_provider import MockUserProvider, UserNotFoundError
from src.types.user import User, UserId

router = APIRouter()


@router.get("/users/{user_id:uuid}")
async def get_user(user_id: UserId) -> User:
    try:
        return MockUserProvider().get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
