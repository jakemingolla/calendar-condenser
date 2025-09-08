from typing import Literal

from pydantic import BaseModel


class LoadingIndicator(BaseModel):
    type: Literal["loading"] = "loading"
    message: str
