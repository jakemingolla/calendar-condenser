"""Unit tests for StateSerializer."""

import json
from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import BaseModel

from src.api.serializers import StateSerializer


class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""

    name: str
    value: int
    optional_field: str | None = None

    model_config = {"arbitrary_types_allowed": True}


def test_serialize_datetime():
    """Test serialization of datetime objects."""
    dt = datetime(2023, 1, 1, 12, 0, 0)
    result = StateSerializer.serialize(dt)

    assert isinstance(result, str)
    assert result == "2023-01-01T12:00:00"


def test_serialize_uuid():
    """Test serialization of UUID objects."""
    test_uuid = uuid4()
    result = StateSerializer.serialize(test_uuid)

    assert isinstance(result, str)
    assert result == str(test_uuid)


def test_serialize_dict_with_uuid_keys():
    """Test serialization of dict with UUID keys."""
    test_uuid = uuid4()
    test_dict = {test_uuid: "value", "string_key": "another_value"}
    result = StateSerializer.serialize(test_dict)

    assert isinstance(result, dict)
    assert str(test_uuid) in result
    assert result[str(test_uuid)] == "value"
    assert result["string_key"] == "another_value"


def test_serialize_dict_with_uuid_values():
    """Test serialization of dict with UUID values."""
    test_uuid = uuid4()
    test_dict = {"key": test_uuid, "another_key": "string_value"}
    result = StateSerializer.serialize(test_dict)

    assert isinstance(result, dict)
    assert result["key"] == str(test_uuid)
    assert result["another_key"] == "string_value"


def test_serialize_nested_dict():
    """Test serialization of nested dict structures."""
    test_uuid = uuid4()
    dt = datetime(2023, 1, 1, 12, 0, 0)
    test_dict = {
        "level1": {
            "level2": {
                "uuid": test_uuid,
                "datetime": dt,
                "string": "value",
            },
        },
    }
    result = StateSerializer.serialize(test_dict)

    assert isinstance(result, dict)
    assert result["level1"]["level2"]["uuid"] == str(test_uuid)
    assert result["level1"]["level2"]["datetime"] == "2023-01-01T12:00:00"
    assert result["level1"]["level2"]["string"] == "value"


def test_serialize_list():
    """Test serialization of list objects."""
    test_uuid = uuid4()
    dt = datetime(2023, 1, 1, 12, 0, 0)
    test_list = [test_uuid, dt, "string", 123]
    result = StateSerializer.serialize(test_list)

    assert isinstance(result, list)
    assert result[0] == str(test_uuid)
    assert result[1] == "2023-01-01T12:00:00"
    assert result[2] == "string"
    assert result[3] == 123


def test_serialize_nested_list():
    """Test serialization of nested list structures."""
    test_uuid = uuid4()
    dt = datetime(2023, 1, 1, 12, 0, 0)
    test_list = [
        [test_uuid, dt],
        ["nested", "values"],
        [1, 2, 3],
    ]
    result = StateSerializer.serialize(test_list)

    assert isinstance(result, list)
    assert result[0][0] == str(test_uuid)
    assert result[0][1] == "2023-01-01T12:00:00"
    assert result[1] == ["nested", "values"]
    assert result[2] == [1, 2, 3]


def test_serialize_pydantic_model():
    """Test serialization of Pydantic models."""
    model = SampleModel(name="test", value=42, optional_field="optional")
    result = StateSerializer.serialize(model)

    assert isinstance(result, dict)
    assert result["name"] == "test"
    assert result["value"] == 42
    assert result["optional_field"] == "optional"


def test_serialize_pydantic_model_with_none_values():
    """Test serialization of Pydantic model with None values."""
    model = SampleModel(name="test", value=42, optional_field=None)
    result = StateSerializer.serialize(model)

    assert isinstance(result, dict)
    assert result["name"] == "test"
    assert result["value"] == 42
    assert "optional_field" not in result  # None values are excluded


def test_serialize_pydantic_model_with_defaults():
    """Test serialization of Pydantic model with default values."""
    model = SampleModel(name="test", value=42)  # optional_field will use default None
    result = StateSerializer.serialize(model)

    assert isinstance(result, dict)
    assert result["name"] == "test"
    assert result["value"] == 42
    assert "optional_field" not in result


def test_serialize_primitive_types():
    """Test serialization of primitive types (should remain unchanged)."""
    test_cases = [
        "string",
        123,
        3.14,
        True,
        False,
        None,
    ]

    for test_case in test_cases:
        result = StateSerializer.serialize(test_case)
        assert result == test_case


def test_serialize_empty_structures():
    """Test serialization of empty structures."""
    empty_dict = {}
    empty_list = []

    result_dict = StateSerializer.serialize(empty_dict)
    result_list = StateSerializer.serialize(empty_list)

    assert result_dict == {}
    assert result_list == []


def test_serialize_mixed_complex_structure():
    """Test serialization of a complex mixed structure."""
    test_uuid = uuid4()
    dt = datetime(2023, 1, 1, 12, 0, 0)
    model = SampleModel(name="test", value=42)

    complex_structure = {
        "uuid_key": test_uuid,
        "datetime_key": dt,
        "model": model,
        "list_with_mixed": [test_uuid, dt, model, "string", 123],
        "nested_dict": {
            "inner_uuid": test_uuid,
            "inner_datetime": dt,
            "inner_model": model,
        },
    }

    result = StateSerializer.serialize(complex_structure)

    # Verify UUID keys and values are converted
    assert "uuid_key" in result
    assert result["uuid_key"] == str(test_uuid)

    # Verify datetime is converted
    assert result["datetime_key"] == "2023-01-01T12:00:00"

    # Verify model is converted
    assert isinstance(result["model"], dict)
    assert result["model"]["name"] == "test"

    # Verify list elements are converted
    assert result["list_with_mixed"][0] == str(test_uuid)
    assert result["list_with_mixed"][1] == "2023-01-01T12:00:00"
    assert isinstance(result["list_with_mixed"][2], dict)
    assert result["list_with_mixed"][3] == "string"
    assert result["list_with_mixed"][4] == 123

    # Verify nested dict is converted
    assert result["nested_dict"]["inner_uuid"] == str(test_uuid)
    assert result["nested_dict"]["inner_datetime"] == "2023-01-01T12:00:00"
    assert isinstance(result["nested_dict"]["inner_model"], dict)


def test_to_json_basic():
    """Test to_json method with basic serialization."""
    test_uuid = uuid4()
    dt = datetime(2023, 1, 1, 12, 0, 0)
    test_data = {"uuid": test_uuid, "datetime": dt, "string": "value"}

    result = StateSerializer.to_json(test_data)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed["uuid"] == str(test_uuid)
    assert parsed["datetime"] == "2023-01-01T12:00:00"
    assert parsed["string"] == "value"


def test_to_json_with_indent():
    """Test to_json method with indentation."""
    test_data = {"key": "value"}

    result = StateSerializer.to_json(test_data, indent=2)

    assert isinstance(result, str)
    # Verify it's properly formatted (contains newlines and spaces)
    assert "\n" in result
    assert "  " in result


def test_to_json_without_indent():
    """Test to_json method without indentation."""
    test_data = {"key": "value"}

    result = StateSerializer.to_json(test_data, indent=None)

    assert isinstance(result, str)
    # Verify it's compact (no extra whitespace)
    # Note: json.dumps with indent=None still adds spaces after colons
    assert result == '{"key": "value"}'


def test_to_json_ensure_ascii_false():
    """Test to_json method handles non-ASCII characters correctly."""
    test_data = {"unicode": "测试🎉"}

    result = StateSerializer.to_json(test_data)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed["unicode"] == "测试🎉"


def test_serialize_circular_reference_handling():
    """Test that serializer handles potential circular references gracefully."""
    # Note: The current serializer doesn't handle circular references gracefully
    # This test documents that behavior - circular references will cause recursion errors
    # In a production environment, you might want to add cycle detection

    # Create a dict that references itself
    test_dict = {"key": "value"}
    test_dict["self_ref"] = test_dict  # type: ignore

    # This will cause a RecursionError, which is expected behavior
    with pytest.raises(RecursionError):
        StateSerializer.serialize(test_dict)


def test_serialize_none_values():
    """Test serialization of None values in various contexts."""
    test_uuid = uuid4()
    dt = datetime(2023, 1, 1, 12, 0, 0)

    test_data = {
        "none_value": None,
        "list_with_none": [None, test_uuid, None, dt],
        "dict_with_none": {"key1": None, "key2": test_uuid, "key3": None},
    }

    result = StateSerializer.serialize(test_data)

    assert result["none_value"] is None
    assert result["list_with_none"][0] is None
    assert result["list_with_none"][1] == str(test_uuid)
    assert result["list_with_none"][2] is None
    assert result["list_with_none"][3] == "2023-01-01T12:00:00"
    assert result["dict_with_none"]["key1"] is None
    assert result["dict_with_none"]["key2"] == str(test_uuid)
    assert result["dict_with_none"]["key3"] is None
