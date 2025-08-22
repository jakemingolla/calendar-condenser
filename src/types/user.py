from typing import NewType
from uuid import UUID

from src.types.higher_order import BrandedBaseModel

UserId = NewType("UserId", UUID)


class User(BrandedBaseModel):
    id: UserId
    given_name: str
    timezone: str
    avatar_url: str
