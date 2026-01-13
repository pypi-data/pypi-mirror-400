"""
Pipeline Module for ublkit.

Main orchestration for single file and batch processing.
"""

from __future__ import annotations

import datetime
import gc
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

from py_logex import logger

from ublkit.config import DEFAULT_ENCODING_PRIORITY, UBLKitConfig
from ublkit.core.models import ConversionResult, ProcessingResult, ProcessingSummary
from ublkit.processors.csv_processor import CSVProcessor
from ublkit.processors.json_processor import JSONProcessor
from ublkit.processors.xml_processor import XMLProcessor
from ublkit.utils.decorators import log_execution, memory_cleanup


def _build_encoding_priority(config: UBLKitConfig) -> List[str]:
    """
    Build encoding priority list from config.

    Args:
        config: UBLKit configuration

    Returns:
        List of encodings in priority order (no duplicates)
    """
    priority = [config.processing.encoding] + DEFAULT_ENCODING_PRIORITY
    return list(dict.fromkeys(priority))


class SingleFileConverter:
    """Handles conversion of a single XML file (in-memory)."""

    def __init__(
        self,
        config: UBLKitConfig,
        output_format: str,
    ) -> None:
        """
        Initialize SingleFileConverter.

        Args:
            config: UBLKit configuration
            output_format: Output format ("json" or "csv")
        """
        self._config = config
        self._output_format = output_format.lower()

        encoding_priority = _build_encoding_priority(config)

        self._xml_processor = XMLProcessor(
            encoding_priority,
            preserve_prefix=config.xml.preserve_namespace_prefix,
        )
        self._json_processor = JSONProcessor(
            flatten=config.json.flatten,
            separator=config.json.separator,
        )
        self._csv_processor = CSVProcessor(
            key_separator=config.csv.key_separator,
            max_records_per_file=config.csv.max_records_per_file,
            preservation_method=config.csv.preservation_method,
        )

    @log_execution
    @memory_cleanup
    def convert(self, xml_path: str) -> ConversionResult:
        """
        Convert a single XML file to JSON or CSV format (in-memory).

        Args:
            xml_path: Path to XML file

        Returns:
            ConversionResult with all data in memory
        """
        file_path = Path(xml_path)
        start_time = datetime.datetime.now()

        try:
            file_size = file_path.stat().st_size

            json_data, doc_type, _ = self._xml_processor.process_file(file_path)

            if self._output_format == "json":
                content = self._json_processor.process_json(json_data)
            elif self._output_format == "csv":
                pairs = self._csv_processor.flatten_only(
                    json_data,
                    source_file=file_path.name,
                )
                content = [
                    {
                        "key": p.key,
                        "value": p.value,
                        "source_file": p.source_file,
                    }
                    for p in pairs
                ]
            else:
                raise ValueError(f"Invalid output format: {self._output_format}")

            elapsed = (datetime.datetime.now() - start_time).total_seconds()

            return ConversionResult(
                success=True,
                source_file=str(file_path),
                output_format=self._output_format,
                processing_time_seconds=elapsed,
                error_message="",
                file_size_bytes=file_size,
                ubl_document_type=doc_type,
                content=content,
            )

        except Exception as e:
            elapsed = (datetime.datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to convert {xml_path}: {type(e).__name__}: {e}")

            return ConversionResult(
                success=False,
                source_file=str(file_path),
                output_format=self._output_format,
                processing_time_seconds=elapsed,
                error_message=f"{type(e).__name__}: {str(e)}",
                file_size_bytes=0,
                ubl_document_type="",
                content=None,
            )


class BatchConverter:
    """Handles batch conversion of multiple XML files."""

    def __init__(
        self,
        config: UBLKitConfig,
        output_format: str,
        input_dir: str,
        output_dir: str,
    ) -> None:
        """
        Initialize BatchConverter.

        Args:
            config: UBLKit configuration
            output_format: Output format ("json" or "csv")
            input_dir: Input directory path
            output_dir: Output directory path
        """
        self._config = config
        self._output_format = output_format.lower()
        self._input_dir = Path(input_dir)
        self._output_dir = Path(output_dir)

        encoding_priority = _build_encoding_priority(config)

        self._xml_processor = XMLProcessor(
            encoding_priority,
            preserve_prefix=config.xml.preserve_namespace_prefix,
        )
        self._json_processor = JSONProcessor(
            flatten=config.json.flatten,
            separator=config.json.separator,
        )
        self._csv_processor = CSVProcessor(
            key_separator=config.csv.key_separator,
            max_records_per_file=config.csv.max_records_per_file,
            preservation_method=config.csv.preservation_method,
        )

    @log_execution
    @memory_cleanup
    def convert(self) -> ProcessingSummary:
        """
        Convert all XML files in input directory.

        Implements sampling-based garbage collection (every 10 files)
        to prevent memory accumulation without constant overhead.

        Returns:
            ProcessingSummary with results
        """
        self._output_dir.mkdir(parents=True, exist_ok=True)

        xml_files = list(self._input_dir.glob("*.xml"))

        if not xml_files:
            logger.warning(f"No XML files found in: {self._input_dir}")
            return ProcessingSummary(
                output_format=self._output_format,
                start_time=datetime.datetime.now(),
                end_time=datetime.datetime.now(),
            )

        logger.info(f"Found {len(xml_files)} XML files to process")

        summary = ProcessingSummary(
            output_format=self._output_format,
            start_time=datetime.datetime.now(),
        )

        if self._config.features.enable_dry_run:
            logger.info("DRY RUN MODE - No files will be written")
            for xml_file in xml_files:
                logger.info(f"Would process: {xml_file.name}")
            summary.end_time = datetime.datetime.now()
            return summary

        max_workers = self._config.processing.max_workers
        total_files = len(xml_files)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, xml_file): xml_file
                for xml_file in xml_files
            }

            completed = 0
            for future in as_completed(future_to_file):
                result = future.result()
                summary.add_result(result)

                completed += 1

                if completed % 10 == 0:
                    gc.collect(generation=0)

                if completed % 10 == 0 or completed == total_files:
                    progress_pct = (completed * 100) // total_files
                    logger.info(
                        f"Progress: {completed}/{total_files} files ({progress_pct}%)"
                    )

        summary.end_time = datetime.datetime.now()

        self._write_summary(summary)

        return summary

    def _process_single_file(self, xml_file: Path) -> ProcessingResult:
        """Process a single XML file and track all output paths."""
        start_time = datetime.datetime.now()

        try:
            file_size = xml_file.stat().st_size

            json_data, doc_type, _ = self._xml_processor.process_file(xml_file)

            output_path = self._output_dir / xml_file.stem
            output_files: List[Path] = []

            if self._output_format == "json":
                output_file = output_path.with_suffix(".json")
                processed_json = self._json_processor.process_json(json_data)
                self._json_processor.write_file(processed_json, output_file)
                output_files = [output_file]

            elif self._output_format == "csv":
                output_file = output_path.with_suffix(".csv")
                output_files = self._csv_processor.process_to_csv(
                    json_data,
                    output_file,
                    source_file=xml_file.name,
                )

            else:
                raise ValueError(f"Invalid output format: {self._output_format}")

            elapsed = (datetime.datetime.now() - start_time).total_seconds()

            return ProcessingResult(
                file_path=xml_file,
                success=True,
                output_paths=output_files,
                error_message=None,
                processing_time_seconds=elapsed,
                file_size_bytes=file_size,
                ubl_document_type=doc_type,
            )

        except Exception as e:
            elapsed = (datetime.datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to process {xml_file.name}: {type(e).__name__}: {e}")

            return ProcessingResult(
                file_path=xml_file,
                success=False,
                output_paths=None,
                error_message=f"{type(e).__name__}: {str(e)}",
                processing_time_seconds=elapsed,
                file_size_bytes=0,
                ubl_document_type="",
            )

    def _write_summary(self, summary: ProcessingSummary) -> None:
        """Write summary to JSON file."""
        summary_dir = Path(self._config.output.summary_dir)
        summary_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        summary_file = summary_dir / f"ublkit_summary_{timestamp}.json"

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Summary written to: {summary_file}")
