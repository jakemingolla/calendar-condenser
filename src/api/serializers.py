# ruff: noqa: ANN401
import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class StateSerializer:
    """Custom serializer for graph state objects that handles complex nested structures."""

    @staticmethod
    def serialize(obj: Any) -> Any:
        """Recursively convert datetime and UUID objects to JSON-serializable types."""
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, UUID):
            return str(obj)

        if isinstance(obj, dict):
            return {str(key) if isinstance(key, UUID) else key: StateSerializer.serialize(value) for key, value in obj.items()}

        if isinstance(obj, list):
            return [StateSerializer.serialize(item) for item in obj]

        if isinstance(obj, BaseModel):
            return StateSerializer.serialize(obj.model_dump(exclude_none=True, exclude_defaults=True))

        return obj

    @staticmethod
    def to_json(state: Any, indent: int | None = None) -> str:
        """Convert state to formatted JSON string."""
        return json.dumps(StateSerializer.serialize(state), indent=indent, ensure_ascii=False)
