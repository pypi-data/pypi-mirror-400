"""
ublkit - Simple, powerful UBL XML to JSON/CSV converter.

Main API exports for single file and batch processing.
"""

from __future__ import annotations

from typing import Any, Dict

from py_logex import logger

from ublkit.config import UBLKitConfig
from ublkit.core.models import ProcessingSummary
from ublkit.core.pipeline import BatchConverter, SingleFileConverter
from ublkit.version import __version__

__all__ = [
    "convert_file",
    "convert_batch",
    "__version__",
]

VALID_FORMATS = {"json", "csv"}


def convert_file(
    xml_path: str,
    output_format: str,
    config_path: str,
) -> Dict[str, Any]:
    """
    Convert a single XML file to JSON or CSV format (in-memory).

    This function processes the file entirely in memory and returns
    the result. No files are written to disk.

    Args:
        xml_path: Path to UBL XML file
        output_format: Output format - "json" or "csv"
        config_path: Path to ublkit.yaml configuration file (required)

    Returns:
        Dictionary containing:
        - success: bool
        - error_message: str (empty if successful)
        - processing_time_seconds: float
        - source_file: str
        - file_size_bytes: int
        - ubl_document_type: str
        - output_format: str
        - content: dict | list (the converted data)

    Example:
        >>> result = convert_file(
        ...     xml_path="invoice.xml",
        ...     output_format="json",
        ...     config_path="ublkit.yaml"
        ... )
        >>> if result["success"]:
        ...     data = result["content"]
        ...     print(f"Document type: {result['ubl_document_type']}")
    """
    output_format_lower = output_format.lower()
    if output_format_lower not in VALID_FORMATS:
        raise ValueError(
            f"Invalid output_format: {output_format}. Must be 'json' or 'csv'"
        )

    config = UBLKitConfig.from_yaml(config_path)

    logger.info(f"Converting file: {xml_path} to {output_format_lower}")

    converter = SingleFileConverter(config, output_format_lower)
    result = converter.convert(xml_path)

    return result.to_dict()


def convert_batch(
    input_dir: str,
    output_dir: str,
    output_format: str,
    config_path: str,
) -> ProcessingSummary:
    """
    Convert multiple XML files from input directory (writes to disk).

    This function processes all .xml files in the input directory,
    writes output files to the output directory, and generates a
    summary file in the configured summary directory.

    Args:
        input_dir: Directory containing UBL XML files
        output_dir: Directory for output files
        output_format: Output format - "json" or "csv"
        config_path: Path to ublkit.yaml configuration file (required)

    Returns:
        ProcessingSummary object containing:
        - total_files: int
        - successful: int
        - failed: int
        - results: List[ProcessingResult]
        - start_time: datetime
        - end_time: datetime
        - output_format: str

    Example:
        >>> summary = convert_batch(
        ...     input_dir="./xml_files",
        ...     output_dir="./output",
        ...     output_format="csv",
        ...     config_path="ublkit.yaml"
        ... )
        >>> print(f"Processed: {summary.total_files}")
        >>> print(f"Successful: {summary.successful}")
        >>> print(f"Failed: {summary.failed}")
    """
    output_format_lower = output_format.lower()
    if output_format_lower not in VALID_FORMATS:
        raise ValueError(
            f"Invalid output_format: {output_format}. Must be 'json' or 'csv'"
        )

    config = UBLKitConfig.from_yaml(config_path)

    logger.info(
        f"Starting batch conversion: {input_dir} -> {output_dir} ({output_format_lower})"
    )

    converter = BatchConverter(config, output_format_lower, input_dir, output_dir)
    summary = converter.convert()

    logger.info(
        f"Batch conversion complete: {summary.successful}/{summary.total_files} successful"
    )

    return summary
