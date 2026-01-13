"""
CSV Processing Module for ublkit.

Handles JSON-to-CSV flattening, data preservation, and file splitting.
Optimized for speed using polars for large datasets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import polars as pl
from py_logex import logger

from ublkit.core.models import KeyValuePair
from ublkit.utils.decorators import log_execution
from ublkit.utils.json_flattener import JSONFlattener


class DataPreserver:
    """
    Applies preservation methods to prevent Excel from corrupting data.

    Supports three methods:
    - apostrophe: Prepends ' to values
    - quotes: Wraps values in double quotes
    - brackets: Wraps values in [value]
    """

    def __init__(self, method: str = "apostrophe") -> None:
        """
        Initialize DataPreserver.

        Args:
            method: Preservation method (apostrophe, quotes, brackets)
        """
        self._method = method

        if method not in ["apostrophe", "quotes", "brackets"]:
            raise ValueError(
                f"Invalid preservation method: {method}. "
                f"Must be one of: apostrophe, quotes, brackets"
            )

    def preserve_value(self, value: str) -> str:
        """
        Apply preservation method to a value.

        Args:
            value: Value to preserve

        Returns:
            Preserved value
        """
        if not value:
            return value

        if self._method == "apostrophe":
            return f"'{value}"
        elif self._method == "quotes":
            escaped = value.replace('"', '""')
            return f'"{escaped}"'
        elif self._method == "brackets":
            return f"[{value}]"

        return value


class CSVWriter:
    """
    Writes CSV files with automatic splitting for large datasets.

    Uses polars for efficient CSV writing.
    """

    def __init__(
        self,
        max_records_per_file: int = 50000,
        preservation_method: str = "apostrophe",
    ) -> None:
        """
        Initialize CSVWriter.

        Args:
            max_records_per_file: Maximum records per CSV file
            preservation_method: Data preservation method
        """
        self._max_records = max_records_per_file
        self._preserver = DataPreserver(preservation_method)

    @log_execution
    def write_csv(
        self,
        output_path: Path,
        pairs: List[KeyValuePair],
    ) -> List[Path]:
        """
        Write key-value pairs to CSV file(s).

        Automatically splits into multiple files if needed.

        Args:
            output_path: Base output path for CSV file(s)
            pairs: List of KeyValuePair objects to write

        Returns:
            List of created file paths
        """
        if not pairs:
            logger.warning("No data to write to CSV")
            return []

        total_records = len(pairs)
        num_files = (total_records + self._max_records - 1) // self._max_records

        output_files: List[Path] = []

        if num_files == 1:
            self._write_single_file(output_path, pairs)
            output_files.append(output_path)
        else:
            logger.info(
                f"Splitting {total_records} records into {num_files} files "
                f"({self._max_records} records per file)"
            )

            for file_idx in range(num_files):
                start_idx = file_idx * self._max_records
                end_idx = min(start_idx + self._max_records, total_records)
                chunk = pairs[start_idx:end_idx]

                file_path = self._get_split_filename(output_path, file_idx + 1)
                self._write_single_file(file_path, chunk)
                output_files.append(file_path)

        return output_files

    def _write_single_file(
        self,
        output_path: Path,
        pairs: List[KeyValuePair],
    ) -> None:
        """Write a single CSV file using polars."""
        keys = []
        values = []
        filenames = []

        for pair in pairs:
            keys.append(pair.key)
            values.append(self._preserver.preserve_value(pair.value))
            filenames.append(pair.source_file)

        df = pl.DataFrame(
            {
                "Key": keys,
                "Value": values,
                "Filename": filenames,
            }
        )

        df.write_csv(output_path)

        logger.debug(f"Wrote {len(pairs)} records to: {output_path}")

    def _get_split_filename(self, base_path: Path, file_number: int) -> Path:
        """
        Generate filename for split CSV files.

        Args:
            base_path: Original output path
            file_number: File number (1-indexed)

        Returns:
            Path with number inserted before extension
        """
        stem = base_path.stem
        suffix = base_path.suffix
        parent = base_path.parent

        new_name = f"{stem}_part{file_number:03d}{suffix}"
        return parent / new_name


class CSVProcessor:
    """
    High-level CSV processor orchestrator.

    Combines flattening, preservation, and writing in a single interface.
    """

    def __init__(
        self,
        key_separator: str = " | ",
        max_records_per_file: int = 50000,
        preservation_method: str = "apostrophe",
    ) -> None:
        """
        Initialize CSVProcessor.

        Args:
            key_separator: Separator for nested keys
            max_records_per_file: Maximum records per CSV file
            preservation_method: Data preservation method
        """
        self._flattener = JSONFlattener(key_separator)
        self._writer = CSVWriter(max_records_per_file, preservation_method)

    def process_to_csv(
        self,
        data: Dict[str, Any],
        output_path: Path,
        source_file: str = "",
    ) -> List[Path]:
        """
        Process JSON data to CSV file(s).

        Args:
            data: JSON dictionary to flatten
            output_path: Output CSV file path
            source_file: Source filename for tracking

        Returns:
            List of created CSV file paths
        """
        pairs = self._flattener.flatten_to_pairs(data, source_file)

        output_files = self._writer.write_csv(output_path, pairs)

        return output_files

    def flatten_only(
        self,
        data: Dict[str, Any],
        source_file: str = "",
    ) -> List[KeyValuePair]:
        """
        Flatten JSON data without writing to file.

        Args:
            data: JSON dictionary to flatten
            source_file: Source filename for tracking

        Returns:
            List of KeyValuePair objects
        """
        return self._flattener.flatten_to_pairs(data, source_file)
