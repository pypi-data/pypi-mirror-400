"""
JSON Flattening utility for ublkit.

Flattens nested JSON with support for arrays, custom separators, and tail text preservation.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ublkit.core.models import KeyValuePair


class JSONFlattener:
    """
    Flattens nested JSON dictionaries with array indexing and tail text preservation.

    Converts nested structures like:
    {"Invoice": {"cac:InvoiceLine": [{"cbc:ID": "1"}, {"cbc:ID": "2"}]}}

    Into flat structure:
    {"Invoice/cac:InvoiceLine[0]/cbc:ID": "1", "Invoice/cac:InvoiceLine[1]/cbc:ID": "2"}

    Supports both dict output (for JSON processing) and KeyValuePair output (for CSV).
    """

    def __init__(self, separator: str = "/") -> None:
        """
        Initialize JSONFlattener.

        Args:
            separator: Separator for nested keys (default: "/")
        """
        self._separator = separator

    def flatten(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten nested dictionary into single-level dictionary.

        Args:
            data: Nested dictionary to flatten

        Returns:
            Flattened dictionary with paths as keys
        """
        result: Dict[str, Any] = {}
        self._flatten_recursive(data, "", result)
        return result

    def flatten_to_pairs(
        self,
        data: Dict[str, Any],
        source_file: str = "",
    ) -> List[KeyValuePair]:
        """
        Flatten nested dictionary into list of KeyValuePair objects.

        Used for CSV output. Optimized for memory efficiency.

        Args:
            data: Nested dictionary to flatten
            source_file: Name of source file (for tracking)

        Returns:
            List of KeyValuePair objects
        """
        pairs: List[KeyValuePair] = []
        self._process_value(data, "", pairs, source_file)
        return pairs

    def _flatten_recursive(
        self,
        value: Any,
        current_path: str,
        result: Dict[str, Any],
    ) -> None:
        """Recursively flatten nested structures into dict."""
        if value is None:
            result[current_path] = None

        elif isinstance(value, dict):
            if not value:
                result[current_path] = {}
            elif "value" in value:
                for key, val in value.items():
                    if key == "value":
                        result[current_path] = val
                    else:
                        new_path = self._build_path(current_path, key)
                        self._flatten_recursive(val, new_path, result)
            else:
                for key, val in value.items():
                    new_path = self._build_path(current_path, key)
                    self._flatten_recursive(val, new_path, result)

        elif isinstance(value, list):
            if not value:
                result[current_path] = []
            else:
                for idx, item in enumerate(value):
                    indexed_path = f"{current_path}[{idx}]"
                    self._flatten_recursive(item, indexed_path, result)
        else:
            result[current_path] = value

    def _process_value(
        self,
        value: Any,
        current_path: str,
        pairs: List[KeyValuePair],
        source_file: str,
    ) -> None:
        """Process a value and recursively handle nested structures into pairs."""
        if value is None:
            self._add_pair(current_path, "", pairs, source_file)

        elif isinstance(value, dict):
            if not value:
                self._add_pair(current_path, "", pairs, source_file)
            else:
                for key, val in value.items():
                    new_path = self._build_path(current_path, key)
                    self._process_value(val, new_path, pairs, source_file)

        elif isinstance(value, list):
            if not value:
                self._add_pair(current_path, "", pairs, source_file)
            else:
                for idx, item in enumerate(value):
                    indexed_path = f"{current_path}[{idx}]"
                    self._process_value(item, indexed_path, pairs, source_file)

        else:
            self._add_pair(current_path, str(value), pairs, source_file)

    def _build_path(self, current_path: str, key: str) -> str:
        """Build path for nested key."""
        if current_path:
            return f"{current_path}{self._separator}{key}"
        return key

    def _add_pair(
        self,
        key: str,
        value: str,
        pairs: List[KeyValuePair],
        source_file: str,
    ) -> None:
        """Add key-value pair to list."""
        if key:
            pairs.append(KeyValuePair(key=key, value=value, source_file=source_file))
