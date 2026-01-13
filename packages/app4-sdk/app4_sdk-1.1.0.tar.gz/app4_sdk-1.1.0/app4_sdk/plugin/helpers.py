"""
Helper functions for App4 plugins.

This module provides utility functions for:
- Config extraction with type safety
- Nested value access/manipulation
- Namespace path handling
- Dictionary operations
"""

from typing import Any, Optional
import copy
import re


def get_config_string(
    config: dict[str, Any], key: str, default: str = ""
) -> str:
    """
    Get a string value from config.

    Args:
        config: Configuration dictionary
        key: Key to look up
        default: Default value if key not found or wrong type

    Returns:
        String value
    """
    value = config.get(key)
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return str(value)


def get_config_bool(
    config: dict[str, Any], key: str, default: bool = False
) -> bool:
    """
    Get a boolean value from config.

    Args:
        config: Configuration dictionary
        key: Key to look up
        default: Default value if key not found or wrong type

    Returns:
        Boolean value
    """
    value = config.get(key)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)


def get_config_int(
    config: dict[str, Any], key: str, default: int = 0
) -> int:
    """
    Get an integer value from config.

    Args:
        config: Configuration dictionary
        key: Key to look up
        default: Default value if key not found or wrong type

    Returns:
        Integer value
    """
    value = config.get(key)
    if value is None:
        return default
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def get_config_float(
    config: dict[str, Any], key: str, default: float = 0.0
) -> float:
    """
    Get a float value from config.

    Args:
        config: Configuration dictionary
        key: Key to look up
        default: Default value if key not found or wrong type

    Returns:
        Float value
    """
    value = config.get(key)
    if value is None:
        return default
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def get_config_value(config: dict[str, Any], key: str) -> Any:
    """
    Get a raw value from config.

    Args:
        config: Configuration dictionary
        key: Key to look up

    Returns:
        Raw value or None if not found
    """
    return config.get(key)


def get_config_list(
    config: dict[str, Any], key: str
) -> list[Any]:
    """
    Get a list value from config.

    Args:
        config: Configuration dictionary
        key: Key to look up

    Returns:
        List value or empty list
    """
    value = config.get(key)
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def get_config_dict(
    config: dict[str, Any], key: str
) -> dict[str, Any]:
    """
    Get a dictionary value from config.

    Args:
        config: Configuration dictionary
        key: Key to look up

    Returns:
        Dictionary value or empty dict
    """
    value = config.get(key)
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {}


def require_config(config: dict[str, Any], *keys: str) -> None:
    """
    Ensure required config keys exist.

    Args:
        config: Configuration dictionary
        keys: Required keys

    Raises:
        ValueError: If any required key is missing
    """
    missing = [k for k in keys if k not in config or config[k] is None]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")


def get_nested_value(data: dict[str, Any], path: str) -> Any:
    """
    Get a nested value using dot notation.

    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., "user.profile.name")

    Returns:
        Value at path or None if not found

    Examples:
        get_nested_value({"user": {"name": "John"}}, "user.name")  # "John"
        get_nested_value({"items": [1, 2, 3]}, "items.0")  # 1
    """
    if not path:
        return data

    parts = path.split(".")
    current = data

    for part in parts:
        if current is None:
            return None

        # Handle array index
        if isinstance(current, list):
            try:
                idx = int(part)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            except ValueError:
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None

    return current


def set_nested_value(data: dict[str, Any], path: str, value: Any) -> None:
    """
    Set a nested value using dot notation.

    Args:
        data: Dictionary to modify
        path: Dot-separated path (e.g., "user.profile.name")
        value: Value to set

    Examples:
        data = {}
        set_nested_value(data, "user.name", "John")
        # data = {"user": {"name": "John"}}
    """
    if not path:
        return

    parts = path.split(".")
    current = data

    for i, part in enumerate(parts[:-1]):
        if part not in current:
            # Check if next part is an integer (array index)
            try:
                int(parts[i + 1])
                current[part] = []
            except ValueError:
                current[part] = {}
        current = current[part]

    # Handle final part
    final_part = parts[-1]
    if isinstance(current, list):
        try:
            idx = int(final_part)
            while len(current) <= idx:
                current.append(None)
            current[idx] = value
        except ValueError:
            pass
    elif isinstance(current, dict):
        current[final_part] = value


def is_namespaced_path(path: str) -> bool:
    """
    Check if a path is a namespaced path.

    Namespaced paths start with $.args., $.ctx., or $.return.

    Args:
        path: Path to check

    Returns:
        True if path is namespaced
    """
    return path.startswith("$.args.") or path.startswith("$.ctx.") or path.startswith("$.return.")


def parse_namespace_path(path: str) -> tuple[str, str]:
    """
    Parse a namespaced path into namespace and remaining path.

    Args:
        path: Namespaced path (e.g., "$.args.user.name")

    Returns:
        Tuple of (namespace, remaining_path)
        e.g., ("args", "user.name")

    Raises:
        ValueError: If path is not a valid namespaced path
    """
    if not is_namespaced_path(path):
        raise ValueError(f"Not a namespaced path: {path}")

    # Remove $. prefix
    path = path[2:]

    # Split into namespace and rest
    parts = path.split(".", 1)
    namespace = parts[0]
    remaining = parts[1] if len(parts) > 1 else ""

    return namespace, remaining


def parse_action_name(name: str) -> tuple[str, str]:
    """
    Parse an action name into prefix and action parts.

    Args:
        name: Action name (e.g., "mongo:find")

    Returns:
        Tuple of (prefix, action)
        e.g., ("mongo", "find")

    Raises:
        ValueError: If action name is invalid
    """
    if ":" not in name:
        raise ValueError(f"Invalid action name format: {name} (expected prefix:action)")

    parts = name.split(":", 1)
    return parts[0], parts[1]


def is_valid_action_name(name: str) -> bool:
    """
    Check if an action name is valid.

    Valid format: prefix:action where both parts are non-empty
    and contain only alphanumeric characters, hyphens, and underscores.

    Args:
        name: Action name to validate

    Returns:
        True if valid
    """
    if ":" not in name:
        return False

    parts = name.split(":", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False

    pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
    return bool(pattern.match(parts[0]) and pattern.match(parts[1]))


def copy_dict(d: dict[str, Any]) -> dict[str, Any]:
    """
    Deep copy a dictionary.

    Args:
        d: Dictionary to copy

    Returns:
        Deep copy of dictionary
    """
    return copy.deepcopy(d)


def merge_dicts(
    base: dict[str, Any], override: dict[str, Any]
) -> dict[str, Any]:
    """
    Deep merge two dictionaries.

    Values in override take precedence. Nested dictionaries are merged
    recursively. Lists are replaced, not merged.

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary (new instance)
    """
    result = copy.deepcopy(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result
