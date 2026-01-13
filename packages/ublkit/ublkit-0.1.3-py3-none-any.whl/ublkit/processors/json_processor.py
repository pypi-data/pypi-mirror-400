"""
JSON Processing Module for ublkit.

Handles JSON output generation and writing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from py_logex import logger

from ublkit.utils.decorators import log_execution
from ublkit.utils.json_flattener import JSONFlattener


class JSONProcessor:
    """Handles JSON output operations."""

    def __init__(
        self,
        indent: int = 2,
        ensure_ascii: bool = False,
        flatten: bool = False,
        separator: str = "/",
    ) -> None:
        """
        Initialize JSONProcessor.

        Args:
            indent: JSON indentation level
            ensure_ascii: Whether to escape non-ASCII characters
            flatten: Whether to flatten nested JSON
            separator: Separator for flattened keys
        """
        self._indent = indent
        self._ensure_ascii = ensure_ascii
        self._flatten = flatten
        self._flattener = JSONFlattener(separator) if flatten else None

    def process_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process JSON data with optional flattening.

        Args:
            data: Dictionary to process

        Returns:
            Processed dictionary (flattened or nested)
        """
        if self._flatten and self._flattener:
            return self._flattener.flatten(data)
        return data

    @log_execution
    def write_file(
        self,
        data: Dict[str, Any],
        output_path: Path,
    ) -> None:
        """
        Write dictionary to JSON file.

        Args:
            data: Dictionary to write
            output_path: Path for output JSON file
        """
        processed_data = self.process_json(data)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                processed_data,
                f,
                indent=self._indent,
                ensure_ascii=self._ensure_ascii,
            )

        logger.debug(f"Wrote JSON to: {output_path}")
