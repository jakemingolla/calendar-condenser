import operator
from abc import ABC
from typing import Annotated, Any

from pydantic import BaseModel, Field


class BrandedBaseModel(BaseModel, ABC):
    type: Annotated[str, operator.add] = Field(default="")  # NOTE: Overridden in `model_post_init`

    def model_post_init(self, __context: Any, /) -> None:  # noqa: ANN401
        """Set the type field to the actual class name after initialization."""
        object.__setattr__(self, "type", self.__class__.__name__)
