"""Unit tests for merge_dicts function."""

from typing import Any

from src.utilities.merge_dicts import merge_dicts


def test_merge_empty_dicts():
    """Test merging two empty dictionaries."""
    dict1: dict[Any, Any] = {}
    dict2: dict[Any, Any] = {}
    result = merge_dicts(dict1, dict2)

    assert result == {}
    assert result is not dict1  # Should return new dict
    assert result is not dict2  # Should return new dict


def test_merge_dict_with_empty():
    """Test merging a dictionary with an empty dictionary."""
    dict1 = {"a": 1, "b": 2}
    dict2: dict[str, int] = {}
    result = merge_dicts(dict1, dict2)

    assert result == {"a": 1, "b": 2}
    assert result is not dict1
    assert result is not dict2


def test_merge_empty_with_dict():
    """Test merging an empty dictionary with a dictionary."""
    dict1: dict[str, int] = {}
    dict2 = {"c": 3, "d": 4}
    result = merge_dicts(dict1, dict2)

    assert result == {"c": 3, "d": 4}
    assert result is not dict1
    assert result is not dict2


def test_merge_no_overlapping_keys():
    """Test merging dictionaries with no overlapping keys."""
    dict1 = {"a": 1, "b": 2}
    dict2 = {"c": 3, "d": 4}
    result = merge_dicts(dict1, dict2)

    assert result == {"a": 1, "b": 2, "c": 3, "d": 4}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_overlapping_keys():
    """Test merging dictionaries with overlapping keys (dict2 should take precedence)."""
    dict1 = {"a": 1, "b": 2, "c": 3}
    dict2 = {"b": 20, "c": 30, "d": 4}
    result = merge_dicts(dict1, dict2)

    assert result == {"a": 1, "b": 20, "c": 30, "d": 4}
    assert result is not dict1
    assert result is not dict2


def test_merge_identical_dicts():
    """Test merging identical dictionaries."""
    dict1 = {"a": 1, "b": 2}
    dict2 = {"a": 1, "b": 2}
    result = merge_dicts(dict1, dict2)

    assert result == {"a": 1, "b": 2}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_none_values():
    """Test merging dictionaries with None values."""
    dict1: dict[str, Any] = {"a": 1, "b": None}
    dict2: dict[str, Any] = {"b": "not_none", "c": None}
    result = merge_dicts(dict1, dict2)

    assert result == {"a": 1, "b": "not_none", "c": None}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_different_value_types():
    """Test merging dictionaries with different value types."""
    dict1: dict[str, Any] = {"a": 1, "b": "string", "c": [1, 2, 3]}
    dict2: dict[str, Any] = {"b": 42, "c": {"nested": "dict"}, "d": True}
    result = merge_dicts(dict1, dict2)

    assert result == {"a": 1, "b": 42, "c": {"nested": "dict"}, "d": True}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_nested_dicts():
    """Test merging dictionaries with nested dictionary values."""
    dict1 = {"a": {"x": 1, "y": 2}, "b": 3}
    dict2 = {"a": {"z": 3}, "c": 4}
    result = merge_dicts(dict1, dict2)

    # Note: dict2 values take precedence, so the entire "a" value is replaced
    assert result == {"a": {"z": 3}, "b": 3, "c": 4}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_list_values():
    """Test merging dictionaries with list values."""
    dict1 = {"a": [1, 2], "b": 3}
    dict2 = {"a": [3, 4, 5], "c": 6}
    result = merge_dicts(dict1, dict2)

    assert result == {"a": [3, 4, 5], "b": 3, "c": 6}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_boolean_values():
    """Test merging dictionaries with boolean values."""
    dict1 = {"a": True, "b": False}
    dict2 = {"b": True, "c": False}
    result = merge_dicts(dict1, dict2)

    assert result == {"a": True, "b": True, "c": False}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_float_values():
    """Test merging dictionaries with float values."""
    dict1 = {"a": 1.5, "b": 2.7}
    dict2 = {"b": 3.14, "c": 0.0}
    result = merge_dicts(dict1, dict2)

    assert result == {"a": 1.5, "b": 3.14, "c": 0.0}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_string_keys():
    """Test merging dictionaries with string keys."""
    dict1 = {"key1": "value1", "key2": "value2"}
    dict2 = {"key2": "new_value2", "key3": "value3"}
    result = merge_dicts(dict1, dict2)

    assert result == {"key1": "value1", "key2": "new_value2", "key3": "value3"}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_numeric_keys():
    """Test merging dictionaries with numeric keys."""
    dict1 = {1: "one", 2: "two"}
    dict2 = {2: "TWO", 3: "three"}
    result = merge_dicts(dict1, dict2)

    assert result == {1: "one", 2: "TWO", 3: "three"}
    assert result is not dict1
    assert result is not dict2


def test_merge_with_mixed_key_types():
    """Test merging dictionaries with mixed key types."""
    dict1: dict[Any, Any] = {"string": 1, 42: "number", (1, 2): "tuple"}
    dict2: dict[Any, Any] = {42: "FORTY_TWO", "new": "value"}
    result = merge_dicts(dict1, dict2)

    assert result == {"string": 1, 42: "FORTY_TWO", (1, 2): "tuple", "new": "value"}
    assert result is not dict1
    assert result is not dict2


def test_merge_original_dicts_unchanged():
    """Test that original dictionaries are not modified."""
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 20, "c": 3}
    original_dict1 = dict1.copy()
    original_dict2 = dict2.copy()

    result = merge_dicts(dict1, dict2)

    # Original dicts should be unchanged
    assert dict1 == original_dict1
    assert dict2 == original_dict2
    assert result == {"a": 1, "b": 20, "c": 3}


def test_merge_single_item_dicts():
    """Test merging single-item dictionaries."""
    dict1 = {"only": "item1"}
    dict2 = {"only": "item2"}
    result = merge_dicts(dict1, dict2)

    assert result == {"only": "item2"}
    assert result is not dict1
    assert result is not dict2


def test_merge_large_dicts():
    """Test merging larger dictionaries."""
    dict1 = {f"key{i}": i for i in range(100)}
    dict2 = {f"key{i}": i * 2 for i in range(50, 150)}
    result = merge_dicts(dict1, dict2)

    # Check that all keys are present
    assert len(result) == 150
    # Check that dict2 values take precedence for overlapping keys
    for i in range(50):
        assert result[f"key{i}"] == i
    for i in range(50, 100):
        assert result[f"key{i}"] == i * 2  # dict2 takes precedence
    for i in range(100, 150):
        assert result[f"key{i}"] == i * 2
    assert result is not dict1
    assert result is not dict2


def test_merge_with_special_values():
    """Test merging dictionaries with special values like empty strings and zero."""
    dict1: dict[str, Any] = {"empty": "", "zero": 0, "false": False}
    dict2: dict[str, Any] = {"empty": "not_empty", "zero": 1, "false": True, "none": None}
    result = merge_dicts(dict1, dict2)

    assert result == {"empty": "not_empty", "zero": 1, "false": True, "none": None}
    assert result is not dict1
    assert result is not dict2
