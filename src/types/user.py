from typing import NewType
from uuid import UUID

from pydantic import BaseModel

UserId = NewType("UserId", UUID)


class User(BaseModel):
    id: UserId
    given_name: str
    timezone: str
