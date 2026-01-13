"""
Configuration management for ublkit.

Handles loading, validation, and access to configuration from ublkit.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml
from py_logex import logger

DEFAULT_ENCODING_PRIORITY = ["utf-8", "utf-16", "iso-8859-1", "cp1252"]
VALID_ENCODINGS = {"utf-8", "utf-16", "iso-8859-1", "ascii", "cp1252"}
VALID_CSV_METHODS = {"apostrophe", "quotes", "brackets"}
_CONFIG_CACHE: Dict[str, UBLKitConfig] = {}


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    file: str = "ublkit.log"
    rotation: str = "500 MB"
    retention: str = "10 days"
    compression: str = "zip"


@dataclass
class ProcessingConfig:
    """Processing configuration."""

    max_workers: int = 4
    encoding: str = "utf-8"


@dataclass
class CSVConfig:
    """CSV output configuration."""

    max_records_per_file: int = 50000
    preservation_method: str = "apostrophe"
    key_separator: str = " | "


@dataclass
class OutputConfig:
    """Output directories configuration."""

    summary_dir: str = "./summaries"
    logs_dir: str = "./logs"


@dataclass
class FeaturesConfig:
    """Feature flags configuration."""

    enable_dry_run: bool = False


@dataclass
class XMLConfig:
    """XML processing configuration."""

    preserve_namespace_prefix: bool = False


@dataclass
class JSONConfig:
    """JSON output configuration."""

    flatten: bool = False
    separator: str = "/"


@dataclass
class UBLKitConfig:
    """
    Main configuration class for ublkit.

    Loads and validates configuration from ublkit.yaml file.
    """

    logging: LoggingConfig
    processing: ProcessingConfig
    csv: CSVConfig
    output: OutputConfig
    features: FeaturesConfig
    xml: XMLConfig
    json: JSONConfig

    @classmethod
    def from_yaml(cls, config_path: str) -> UBLKitConfig:
        """
        Load configuration from YAML file with caching.

        Args:
            config_path: Path to ublkit.yaml configuration file

        Returns:
            UBLKitConfig instance with loaded configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
            ValueError: If config file has invalid values
        """
        cache_key = str(Path(config_path).resolve())
        if cache_key in _CONFIG_CACHE:
            logger.debug(f"Using cached configuration from: {config_path}")
            return _CONFIG_CACHE[cache_key]

        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        logger.debug(f"Loading configuration from: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid configuration file: {config_path}")

        logging_data = data.get("logging", {})
        logging_config = LoggingConfig(
            level=logging_data.get("level", "INFO"),
            file=logging_data.get("file", "ublkit.log"),
            rotation=logging_data.get("rotation", "500 MB"),
            retention=logging_data.get("retention", "10 days"),
            compression=logging_data.get("compression", "zip"),
        )

        processing_data = data.get("processing", {})
        processing_config = ProcessingConfig(
            max_workers=processing_data.get("max_workers", 4),
            encoding=processing_data.get("encoding", "utf-8"),
        )

        if processing_config.max_workers < 1:
            raise ValueError("processing.max_workers must be >= 1")

        if processing_config.encoding not in VALID_ENCODINGS:
            raise ValueError(
                f"processing.encoding must be one of: {', '.join(VALID_ENCODINGS)}"
            )

        csv_data = data.get("csv", {})
        csv_config = CSVConfig(
            max_records_per_file=csv_data.get("max_records_per_file", 50000),
            preservation_method=csv_data.get("preservation_method", "apostrophe"),
            key_separator=csv_data.get("key_separator", " | "),
        )

        if csv_config.max_records_per_file < 1:
            raise ValueError("csv.max_records_per_file must be >= 1")

        if csv_config.preservation_method not in VALID_CSV_METHODS:
            raise ValueError(
                f"csv.preservation_method must be one of: {', '.join(VALID_CSV_METHODS)}"
            )

        output_data = data.get("output", {})
        output_config = OutputConfig(
            summary_dir=output_data.get("summary_dir", "./summaries"),
            logs_dir=output_data.get("logs_dir", "./logs"),
        )

        features_data = data.get("features", {})
        features_config = FeaturesConfig(
            enable_dry_run=features_data.get("enable_dry_run", False),
        )

        xml_data = data.get("xml", {})
        xml_config = XMLConfig(
            preserve_namespace_prefix=xml_data.get("preserve_namespace_prefix", False),
        )

        json_data = data.get("json", {})
        json_config = JSONConfig(
            flatten=json_data.get("flatten", False),
            separator=json_data.get("separator", "/"),
        )

        logger.info(f"Configuration loaded successfully from: {config_path}")

        config = cls(
            logging=logging_config,
            processing=processing_config,
            csv=csv_config,
            output=output_config,
            features=features_config,
            xml=xml_config,
            json=json_config,
        )

        _CONFIG_CACHE[cache_key] = config
        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "logging": {
                "level": self.logging.level,
                "file": self.logging.file,
                "rotation": self.logging.rotation,
                "retention": self.logging.retention,
                "compression": self.logging.compression,
            },
            "processing": {
                "max_workers": self.processing.max_workers,
                "encoding": self.processing.encoding,
            },
            "csv": {
                "max_records_per_file": self.csv.max_records_per_file,
                "preservation_method": self.csv.preservation_method,
                "key_separator": self.csv.key_separator,
            },
            "output": {
                "summary_dir": self.output.summary_dir,
                "logs_dir": self.output.logs_dir,
            },
            "features": {
                "enable_dry_run": self.features.enable_dry_run,
            },
            "xml": {
                "preserve_namespace_prefix": self.xml.preserve_namespace_prefix,
            },
            "json": {
                "flatten": self.json.flatten,
                "separator": self.json.separator,
            },
        }
