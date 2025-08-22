from typing import NewType
from uuid import UUID

from pydantic import Field

from src.types.higher_order import BrandedBaseModel

UserId = NewType("UserId", UUID)


class User(BrandedBaseModel):
    id: UserId
    given_name: str
    timezone: str
    avatar_url: str
    preffered_working_hours: tuple[int, int] = Field(description="The user's preferred working hours (in 24-hour format).")
