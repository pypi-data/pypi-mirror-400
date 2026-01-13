"""
XML Processing Module for ublkit.

Handles XML validation, reading, namespace extraction, and XML-to-JSON mapping.
Optimized for speed and robustness.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lxml import etree
from py_logex import logger

from ublkit.utils.decorators import log_execution


class XMLValidator:
    """Validates XML files for well-formedness."""

    @log_execution
    def validate_well_formedness(
        self, xml_content: bytes
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if XML content is well-formed.

        Args:
            xml_content: Raw XML bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            etree.fromstring(xml_content)
            return True, None
        except etree.XMLSyntaxError as e:
            return False, f"XML syntax error: {e}"


class XMLReader:
    """Reads XML files with automatic encoding detection."""

    def __init__(self, encoding_priority: List[str]) -> None:
        """
        Initialize XMLReader with encoding priority list.

        Args:
            encoding_priority: List of encodings to try in order
        """
        self._encoding_priority = encoding_priority

    @log_execution
    def read_file(self, file_path: Path) -> Tuple[bytes, str]:
        """
        Read XML file with automatic encoding detection.

        Args:
            file_path: Path to XML file

        Returns:
            Tuple of (xml_content_bytes, encoding_used)

        Raises:
            IOError: If file cannot be read with any encoding
        """
        last_error = None

        for encoding in self._encoding_priority:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                xml_bytes = content.encode("utf-8")
                logger.debug(f"Successfully read file with encoding: {encoding}")
                return xml_bytes, encoding
            except (UnicodeDecodeError, UnicodeError) as e:
                last_error = e
                continue

        raise IOError(
            f"Failed to read file with any supported encoding. "
            f"Tried: {', '.join(self._encoding_priority)}. "
            f"Last error: {last_error}"
        )

    @log_execution
    def parse_xml(self, xml_content: bytes) -> etree._Element:
        """
        Parse XML content into lxml Element tree.

        Args:
            xml_content: Raw XML bytes

        Returns:
            Parsed XML Element tree
        """
        return etree.fromstring(xml_content)


class NamespaceExtractor:
    """Extracts namespace prefix mappings from XML documents."""

    def __init__(self) -> None:
        """Initialize NamespaceExtractor."""
        self._uri_to_prefix: Dict[str, str] = {}
        self._default_namespace: Optional[str] = None

    @log_execution
    def extract_namespaces(self, xml_tree: etree._Element) -> None:
        """
        Extract all namespace declarations from the XML root element.

        Args:
            xml_tree: Parsed XML element tree
        """
        self._uri_to_prefix = {}
        self._default_namespace = None

        nsmap = xml_tree.nsmap

        for prefix, uri in nsmap.items():
            if prefix is None:
                self._default_namespace = uri
                logger.debug(f"Default namespace: {uri}")
            else:
                self._uri_to_prefix[uri] = prefix
                logger.debug(f"Namespace mapping: {prefix} -> {uri}")

    def get_prefix_for_uri(self, uri: str) -> Optional[str]:
        """Get the prefix for a namespace URI."""
        if uri == self._default_namespace:
            return None
        return self._uri_to_prefix.get(uri)

    def is_default_namespace(self, uri: str) -> bool:
        """Check if URI is the default namespace."""
        return uri == self._default_namespace


class XMLToJSONMapper:
    """
    Maps XML elements to JSON-compatible dictionaries.

    Optimized for speed with minimal allocations and efficient iteration.
    """

    def __init__(
        self, namespace_extractor: NamespaceExtractor, preserve_prefix: bool = False
    ) -> None:
        """Initialize XMLToJSONMapper."""
        self._namespace_extractor = namespace_extractor
        self._preserve_prefix = preserve_prefix

    @log_execution
    def map_to_json(self, xml_tree: etree._Element) -> Dict[str, Any]:
        """
        Convert XML element tree to JSON-compatible dictionary.

        Args:
            xml_tree: Parsed XML element tree

        Returns:
            Dictionary representing the XML structure
        """
        root_dict = self._element_to_dict(xml_tree)

        root_name = self._get_element_name(xml_tree)
        return {root_name: root_dict}

    def _element_to_dict(self, element: etree._Element) -> Any:
        """
        Recursively convert an XML element to dictionary.

        Optimized for speed - uses minimal allocations and efficient iteration.
        Preserves tail text by appending to element value with space separator.
        """
        result: Dict[str, Any] = {}

        if element.attrib:
            for key, value in element.attrib.items():
                attr_name = self._get_attribute_name(key)
                result[attr_name] = value

        element_text = element.text.strip() if element.text else ""
        if element_text:
            result["value"] = element_text

        children_dict: Dict[str, List[Any]] = {}

        for child in element:
            child_name = self._get_element_name(child)
            child_value = self._element_to_dict(child)

            if child_name not in children_dict:
                children_dict[child_name] = []
            children_dict[child_name].append(child_value)

        for key, value_list in children_dict.items():
            if len(value_list) == 1:
                result[key] = value_list[0]
            else:
                result[key] = value_list

        if element.tail:
            tail_text = element.tail.strip()
            if tail_text:
                if "value" in result:
                    result["value"] = f"{result['value']} {tail_text}"
                else:
                    result["value"] = tail_text

        return result if result else {}

    def _get_element_name(self, element: etree._Element) -> str:
        """
        Get element name with optional namespace prefix preservation.
        """
        tag = element.tag

        if isinstance(tag, str) and tag.startswith("{"):
            uri, local_name = tag.split("}", 1)
            uri = uri[1:]

            if self._preserve_prefix:
                prefix = self._namespace_extractor.get_prefix_for_uri(uri)
                if prefix:
                    return f"{prefix}:{local_name}"
            return local_name

        if isinstance(tag, str) and ":" in tag:
            if self._preserve_prefix:
                return tag
            return tag.split(":", 1)[1]

        return str(tag) if not isinstance(tag, str) else tag

    def _get_attribute_name(self, attr_name: str) -> str:
        """Get attribute name with optional namespace prefix preservation."""
        if "{" in attr_name and attr_name.startswith("{"):
            uri, local_name = attr_name[1:].split("}", 1)

            if self._preserve_prefix:
                prefix = self._namespace_extractor.get_prefix_for_uri(uri)
                if prefix:
                    return f"@{prefix}:{local_name}"
            return f"@{local_name}"

        return f"@{attr_name}"

    def extract_document_type(self, xml_tree: etree._Element) -> str:
        """
        Extract UBL document type from root element.

        Args:
            xml_tree: Parsed XML element tree

        Returns:
            Document type (e.g., "Invoice", "CreditNote")
        """
        root_name = self._get_element_name(xml_tree)

        if ":" in root_name:
            return root_name.split(":")[-1]

        return root_name


class XMLProcessor:
    """
    High-level XML processor orchestrator.

    Combines validation, reading, and conversion in a single interface.
    """

    def __init__(
        self, encoding_priority: List[str], preserve_prefix: bool = False
    ) -> None:
        """Initialize XMLProcessor."""
        self._validator = XMLValidator()
        self._reader = XMLReader(encoding_priority)
        self._namespace_extractor = NamespaceExtractor()
        self._mapper = XMLToJSONMapper(self._namespace_extractor, preserve_prefix)

    def process_file(self, file_path: Path) -> Tuple[Dict[str, Any], str, str]:
        """
        Process XML file to JSON dictionary.

        Args:
            file_path: Path to XML file

        Returns:
            Tuple of (json_dict, document_type, encoding_used)

        Raises:
            IOError: If file cannot be read
            etree.XMLSyntaxError: If XML is malformed
        """
        xml_content, encoding = self._reader.read_file(file_path)

        is_valid, error = self._validator.validate_well_formedness(xml_content)
        if not is_valid:
            raise ValueError(error)

        xml_tree = self._reader.parse_xml(xml_content)

        self._namespace_extractor.extract_namespaces(xml_tree)

        doc_type = self._mapper.extract_document_type(xml_tree)

        json_dict = self._mapper.map_to_json(xml_tree)

        return json_dict, doc_type, encoding
