#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config class for managing RegScale CLI configuration.

This module provides a dedicated Config class that handles init.yaml configuration
with the following key features:
- Non-destructive updates: Preserves user-modified values
- Atomic file operations: Prevents corruption during parallel writes
- Type coercion: Converts values to expected types while preserving user intent
- Clear separation of concerns: Single responsibility for configuration management
"""

import contextlib
import logging
import os
import re
import tempfile
from threading import Lock
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import yaml

logger = logging.getLogger("regscale")

# Placeholder patterns that indicate default/unset values
PLACEHOLDER_PATTERNS = [
    re.compile(r"^<[^>]+>$"),  # <myClientIdGoesHere>, <createdProgrammatically>
    re.compile(r"^enter .+ here$", re.IGNORECASE),  # enter RegScale user id here
]


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    pass


class Config:
    """
    Configuration manager for RegScale CLI.

    Provides non-destructive configuration management with atomic file operations.
    User-modified values are preserved when merging with defaults.

    :param config_path: Path to the configuration file (default: init.yaml)
    :param auto_load: Whether to load config from file on initialization (default: True)
    """

    def __init__(self, config_path: str = "init.yaml", auto_load: bool = True):
        """
        Initialize Config instance.

        :param str config_path: Path to configuration file
        :param bool auto_load: Whether to load config from file immediately
        """
        self._config_path = config_path
        self._data: Dict[str, Any] = {}
        self._lock = Lock()

        if auto_load:
            self._load()

    @property
    def config_path(self) -> str:
        """Return the configuration file path."""
        return self._config_path

    def _load(self) -> None:
        """Load configuration from file."""
        with self._lock:
            try:
                with open(self._config_path, encoding="utf-8") as f:
                    loaded_data = yaml.safe_load(f)
                    self._data = loaded_data if loaded_data else {}
            except FileNotFoundError:
                logger.debug("Config file not found: %s", self._config_path)
                self._data = {}
            except yaml.YAMLError as e:
                logger.error("Error parsing config file: %s", e)
                self._data = {}

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load()

    def save(self) -> None:
        """
        Save configuration to file using atomic operations.

        Uses a temporary file and atomic rename to prevent corruption
        during parallel writes.

        :raises ConfigError: If save operation fails
        """
        with self._lock:
            config_dir = os.path.dirname(self._config_path) or "."
            temp_path = None
            try:
                # Create temp file in same directory for atomic rename
                temp_fd, temp_path = tempfile.mkstemp(dir=config_dir, prefix=".tmp_config_", suffix=".yaml", text=True)
                try:
                    with os.fdopen(temp_fd, "w", encoding="utf-8") as temp_file:
                        yaml.dump(self._data, temp_file, default_flow_style=False)
                except Exception:
                    # Close fd if fdopen fails
                    with contextlib.suppress(OSError):
                        os.close(temp_fd)
                    raise

                # Atomic rename
                os.replace(temp_path, self._config_path)
                temp_path = None  # Mark as successfully moved
            except Exception as e:
                logger.error("Failed to save config: %s", e)
                raise ConfigError(f"Failed to save configuration: {e}") from e
            finally:
                # Clean up temp file if it still exists
                if temp_path and os.path.exists(temp_path):
                    with contextlib.suppress(OSError):
                        os.unlink(temp_path)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        :param str key: Configuration key
        :param Any default: Default value if key not found
        :return: Configuration value or default
        :rtype: Any
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        :param str key: Configuration key
        :param Any value: Configuration value
        """
        with self._lock:
            self._data[key] = value

    def delete(self, key: str) -> None:
        """
        Delete a configuration key.

        :param str key: Configuration key to delete
        """
        with self._lock:
            self._data.pop(key, None)

    def merge_defaults(self, defaults: Dict[str, Any]) -> None:
        """
        Merge default values into configuration.

        IMPORTANT: This method preserves user-modified values.
        Only keys that don't exist in the current config are added from defaults.
        Nested dictionaries are merged recursively.

        :param dict defaults: Default configuration values
        """
        with self._lock:
            self._data = self._merge_dicts(self._data, defaults)

    def _merge_dicts(self, user_dict: Dict[str, Any], default_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge defaults into user config, preserving user values.

        :param dict user_dict: User's configuration (takes precedence)
        :param dict default_dict: Default values (only fills gaps)
        :return: Merged configuration
        :rtype: dict
        """
        result = user_dict.copy()

        for key, default_value in default_dict.items():
            if key not in result:
                # Key doesn't exist in user config, use default
                result[key] = default_value
            elif isinstance(default_value, dict) and isinstance(result.get(key), dict):
                # Both are dicts - only merge if user dict has no non-placeholder values
                # If user has set any real values, treat their dict as a complete replacement
                user_value = result[key]
                if self._has_non_placeholder_values(user_value):
                    # User has real values, don't pollute with default placeholders
                    pass
                else:
                    # User dict only has placeholders or is empty, safe to merge defaults
                    result[key] = self._merge_dicts(user_value, default_value)
            # else: User has a value, preserve it

        return result

    def _has_non_placeholder_values(self, d: Dict[str, Any]) -> bool:
        """
        Check if a dictionary contains any non-placeholder values.

        :param dict d: Dictionary to check
        :return: True if any value is not a placeholder
        :rtype: bool
        """
        for value in d.values():
            if isinstance(value, dict):
                if self._has_non_placeholder_values(value):
                    return True
            elif not self.is_placeholder(value):
                return True
        return False

    def coerce_types(self, template: Dict[str, Any]) -> None:
        """
        Coerce configuration values to match template types.

        This method attempts to convert values to the types expected by the template
        while preserving the user's actual values. If conversion fails, the original
        value is kept.

        :param dict template: Template with expected types
        """
        with self._lock:
            self._data = self._coerce_dict(self._data, template)

    def _coerce_dict(self, data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively coerce types in dictionary.

        :param dict data: Data to coerce
        :param dict template: Template with expected types
        :return: Data with coerced types
        :rtype: dict
        """
        result = data.copy()

        for key, template_value in template.items():
            if key not in result:
                continue

            current_value = result[key]

            if isinstance(template_value, dict) and isinstance(current_value, dict):
                result[key] = self._coerce_dict(current_value, template_value)
            elif not isinstance(current_value, type(template_value)):
                coerced = self._coerce_value(current_value, template_value)
                if coerced is not None:
                    result[key] = coerced

        return result

    def _coerce_value(self, value: Any, template_value: Any) -> Optional[Any]:
        """
        Attempt to coerce a value to match the template type.

        :param Any value: Value to coerce
        :param Any template_value: Template value with expected type
        :return: Coerced value or None if coercion fails
        :rtype: Optional[Any]
        """
        try:
            if isinstance(template_value, bool):
                return self._coerce_to_bool(value)
            elif isinstance(template_value, int):
                return int(value)
            elif isinstance(template_value, float):
                return float(value)
            elif isinstance(template_value, str):
                return str(value)
        except (ValueError, TypeError):
            logger.debug("Failed to coerce %s to %s", value, type(template_value).__name__)
        return None

    def _coerce_to_bool(self, value: Any) -> bool:
        """
        Coerce a value to boolean.

        :param Any value: Value to coerce
        :return: Boolean value
        :rtype: bool
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    def is_valid(self) -> bool:
        """
        Check if configuration is valid.

        :return: True if configuration is valid
        :rtype: bool
        """
        return isinstance(self._data, dict)

    def has_required(self, required_keys: List[str]) -> bool:
        """
        Check if all required keys are present.

        :param list required_keys: List of required key names
        :return: True if all required keys are present
        :rtype: bool
        """
        return all(key in self._data for key in required_keys)

    def is_placeholder(self, value: Any) -> bool:
        """
        Check if a value is a placeholder (default/unset value).

        :param Any value: Value to check
        :return: True if value is a placeholder
        :rtype: bool
        """
        if not isinstance(value, str):
            return False
        return any(pattern.match(value) for pattern in PLACEHOLDER_PATTERNS)

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a copy of the configuration as a dictionary.

        :return: Copy of configuration data
        :rtype: dict
        """
        return self._data.copy()

    def items(self) -> Iterator[Tuple[str, Any]]:
        """
        Return configuration items.

        :return: Iterator of key-value pairs
        :rtype: Iterator[Tuple[str, Any]]
        """
        return iter(self._data.items())

    def keys(self) -> Iterator[str]:
        """
        Return configuration keys.

        :return: Iterator of keys
        :rtype: Iterator[str]
        """
        return iter(self._data.keys())

    def values(self) -> Iterator[Any]:
        """
        Return configuration values.

        :return: Iterator of values
        :rtype: Iterator[Any]
        """
        return iter(self._data.values())

    # Dict-like interface

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        """Delete item by key."""
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return number of configuration items."""
        return len(self._data)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Config(path={self._config_path!r}, keys={list(self._data.keys())})"
