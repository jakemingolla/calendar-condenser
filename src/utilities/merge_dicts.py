from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


def merge_dicts(dict1: dict[K, V], dict2: dict[K, V]) -> dict[K, V]:
    """Merge two dictionaries, with dict2 values taking precedence."""
    return {**dict1, **dict2}
