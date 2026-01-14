"""Frontmatter parser for normalizing YAML frontmatter to typed properties.

This module provides parsing of YAML frontmatter from Obsidian markdown files
into normalized, typed property records suitable for SQLite storage.

Supports:
- Type detection (string, number, date, boolean, link, list)
- [[wikilink]] extraction from property values
- Date normalization to ISO 8601
- Array handling with list_index
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class PropertyValueType(str, Enum):
    """Types of property values in frontmatter."""

    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    LINK = "link"
    LIST = "list"


@dataclass
class ParsedProperty:
    """A single parsed property from frontmatter.

    Represents a normalized property record ready for database storage.
    For list values, multiple ParsedProperty instances are created with
    different list_index values.

    Attributes:
        key: Property key (e.g., "status", "tags")
        value_type: Detected type of the value
        property_value: String representation of value (for all types)
        value_number: Numeric value if type is NUMBER
        value_date: ISO 8601 date string if type is DATE
        value_link_target: Normalized link target if type is LINK
        list_index: Index in array (0 for non-array values)
    """

    key: str
    value_type: PropertyValueType
    property_value: str | None = None
    value_number: float | None = None
    value_date: str | None = None
    value_link_target: str | None = None
    list_index: int = 0


@dataclass
class FrontmatterParseResult:
    """Result of parsing frontmatter from a document.

    Attributes:
        properties: List of parsed properties
        raw_frontmatter: Original YAML string
        parse_errors: List of any parsing errors encountered
    """

    properties: list[ParsedProperty] = field(default_factory=list)
    raw_frontmatter: str | None = None
    parse_errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if parsing was successful (no errors)."""
        return len(self.parse_errors) == 0

    @property
    def property_count(self) -> int:
        """Get total number of property records."""
        return len(self.properties)


class FrontmatterParser:
    """Parser for YAML frontmatter in Obsidian markdown files.

    Extracts frontmatter, parses YAML, and normalizes values to typed
    property records suitable for SQLite storage.

    Usage:
        parser = FrontmatterParser()

        # Parse from full markdown content
        result = parser.parse("---\\nstatus: active\\n---\\n# Title")

        # Parse from raw YAML
        result = parser.parse_yaml("status: active\\ntags: [a, b]")

        for prop in result.properties:
            print(f"{prop.key}: {prop.value_type} = {prop.property_value}")
    """

    # Regex for extracting frontmatter block
    FRONTMATTER_PATTERN = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n?",
        re.DOTALL,
    )

    # Regex for detecting [[wikilinks]]
    WIKILINK_PATTERN = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")

    # Regex for ISO date formats
    DATE_PATTERNS = [
        re.compile(r"^\d{4}-\d{2}-\d{2}$"),  # YYYY-MM-DD
        re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),  # ISO 8601 with time
        re.compile(r"^\d{4}/\d{2}/\d{2}$"),  # YYYY/MM/DD
    ]

    def __init__(self) -> None:
        """Initialize the frontmatter parser."""
        pass

    def parse(self, content: str) -> FrontmatterParseResult:
        """Parse frontmatter from markdown content.

        Extracts the YAML frontmatter block from the beginning of
        the content and parses it into typed properties.

        Args:
            content: Full markdown content with potential frontmatter

        Returns:
            FrontmatterParseResult with parsed properties
        """
        result = FrontmatterParseResult()

        if not content:
            return result

        # Extract frontmatter block
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            return result

        yaml_content = match.group(1)
        result.raw_frontmatter = yaml_content

        return self._parse_yaml_content(yaml_content, result)

    def parse_yaml(self, yaml_content: str) -> FrontmatterParseResult:
        """Parse raw YAML content into properties.

        Args:
            yaml_content: Raw YAML string (without --- delimiters)

        Returns:
            FrontmatterParseResult with parsed properties
        """
        result = FrontmatterParseResult()
        result.raw_frontmatter = yaml_content

        if not yaml_content or not yaml_content.strip():
            return result

        return self._parse_yaml_content(yaml_content, result)

    def _parse_yaml_content(
        self,
        yaml_content: str,
        result: FrontmatterParseResult,
    ) -> FrontmatterParseResult:
        """Parse YAML content and populate result.

        Args:
            yaml_content: Raw YAML string
            result: Result object to populate

        Returns:
            Populated FrontmatterParseResult
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            result.parse_errors.append(f"YAML parse error: {e}")
            logger.warning(f"Failed to parse YAML frontmatter: {e}")
            return result

        if not isinstance(data, dict):
            if data is not None:
                result.parse_errors.append(
                    f"Expected dict, got {type(data).__name__}"
                )
            return result

        # Process each key-value pair
        for key, value in data.items():
            if key is None:
                continue

            key_str = str(key)
            properties = self._parse_value(key_str, value)
            result.properties.extend(properties)

        return result

    def _parse_value(
        self,
        key: str,
        value: Any,
        list_index: int = 0,
    ) -> list[ParsedProperty]:
        """Parse a single value into one or more properties.

        Args:
            key: Property key
            value: Property value (any type)
            list_index: Index for list items

        Returns:
            List of ParsedProperty instances
        """
        # Handle None
        if value is None:
            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.STRING,
                    property_value=None,
                    list_index=list_index,
                )
            ]

        # Handle lists/arrays
        if isinstance(value, list):
            properties = []
            for idx, item in enumerate(value):
                # Recursively parse each item with its index
                item_props = self._parse_value(key, item, list_index=idx)
                properties.extend(item_props)
            return properties

        # Handle nested dicts (flatten to JSON string)
        if isinstance(value, dict):
            import json

            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.STRING,
                    property_value=json.dumps(value, ensure_ascii=False),
                    list_index=list_index,
                )
            ]

        # Handle boolean
        if isinstance(value, bool):
            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.BOOLEAN,
                    property_value=str(value).lower(),
                    list_index=list_index,
                )
            ]

        # Handle numbers (int, float)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.NUMBER,
                    property_value=str(value),
                    value_number=float(value),
                    list_index=list_index,
                )
            ]

        # Handle date/datetime objects
        if isinstance(value, datetime):
            iso_date = value.date().isoformat()
            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.DATE,
                    property_value=iso_date,
                    value_date=iso_date,
                    list_index=list_index,
                )
            ]

        if isinstance(value, date):
            iso_date = value.isoformat()
            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.DATE,
                    property_value=iso_date,
                    value_date=iso_date,
                    list_index=list_index,
                )
            ]

        # Handle strings
        str_value = str(value)
        return self._parse_string_value(key, str_value, list_index)

    def _parse_string_value(
        self,
        key: str,
        value: str,
        list_index: int,
    ) -> list[ParsedProperty]:
        """Parse a string value, detecting special types.

        Args:
            key: Property key
            value: String value
            list_index: Index for list items

        Returns:
            List with single ParsedProperty
        """
        # Check for wikilink
        link_target = self._extract_link(value)
        if link_target:
            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.LINK,
                    property_value=value,
                    value_link_target=link_target,
                    list_index=list_index,
                )
            ]

        # Check for date string
        parsed_date = self._parse_date_string(value)
        if parsed_date:
            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.DATE,
                    property_value=parsed_date,
                    value_date=parsed_date,
                    list_index=list_index,
                )
            ]

        # Check for boolean strings
        if value.lower() in ("true", "false", "yes", "no"):
            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.BOOLEAN,
                    property_value=value.lower(),
                    list_index=list_index,
                )
            ]

        # Check for numeric strings
        numeric_value = self._try_parse_number(value)
        if numeric_value is not None:
            return [
                ParsedProperty(
                    key=key,
                    value_type=PropertyValueType.NUMBER,
                    property_value=value,
                    value_number=numeric_value,
                    list_index=list_index,
                )
            ]

        # Default to string
        return [
            ParsedProperty(
                key=key,
                value_type=PropertyValueType.STRING,
                property_value=value,
                list_index=list_index,
            )
        ]

    def _extract_link(self, value: str) -> str | None:
        """Extract wikilink target from a value.

        Args:
            value: String that may contain [[wikilink]]

        Returns:
            Link target (without brackets) or None
        """
        match = self.WIKILINK_PATTERN.search(value)
        if match:
            return match.group(1).strip()
        return None

    def _parse_date_string(self, value: str) -> str | None:
        """Try to parse a string as a date.

        Args:
            value: String that may be a date

        Returns:
            ISO 8601 date string or None
        """
        value = value.strip()

        # Check against known patterns
        for pattern in self.DATE_PATTERNS:
            if pattern.match(value):
                try:
                    # Try parsing with different formats
                    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S"):
                        try:
                            dt = datetime.strptime(value[:10], fmt[:8] if "T" in fmt else fmt)
                            return dt.date().isoformat()
                        except ValueError:
                            continue
                except Exception:
                    pass

        # Try direct ISO parse for YYYY-MM-DD
        if len(value) >= 10 and value[4] in "-/" and value[7] in "-/":
            try:
                year = int(value[0:4])
                month = int(value[5:7])
                day = int(value[8:10])
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                pass

        return None

    def _try_parse_number(self, value: str) -> float | None:
        """Try to parse a string as a number.

        Args:
            value: String that may be a number

        Returns:
            Float value or None
        """
        value = value.strip()

        # Don't parse strings that look like versions, IDs, etc.
        if value.count(".") > 1:  # e.g., "1.2.3"
            return None

        if value.startswith("0") and len(value) > 1 and not value.startswith("0."):
            # Don't parse "007" as a number
            return None

        try:
            return float(value)
        except ValueError:
            return None

    def extract_all_links(self, result: FrontmatterParseResult) -> list[str]:
        """Extract all link targets from parsed properties.

        Args:
            result: Parsed frontmatter result

        Returns:
            List of unique link targets
        """
        links = []
        seen = set()

        for prop in result.properties:
            if prop.value_link_target and prop.value_link_target not in seen:
                links.append(prop.value_link_target)
                seen.add(prop.value_link_target)

        return links

    def get_properties_by_key(
        self,
        result: FrontmatterParseResult,
        key: str,
    ) -> list[ParsedProperty]:
        """Get all properties with a specific key.

        Args:
            result: Parsed frontmatter result
            key: Property key to filter by

        Returns:
            List of properties with matching key
        """
        return [p for p in result.properties if p.key == key]

    def to_dict(self, result: FrontmatterParseResult) -> dict[str, Any]:
        """Convert parsed properties back to a dict.

        Reconstructs a dictionary from parsed properties.
        List values are reconstructed from multiple properties
        with the same key.

        Args:
            result: Parsed frontmatter result

        Returns:
            Dictionary representation
        """
        output: dict[str, Any] = {}
        list_keys: set[str] = set()

        # First pass: identify list keys
        key_counts: dict[str, int] = {}
        for prop in result.properties:
            key_counts[prop.key] = key_counts.get(prop.key, 0) + 1

        for key, count in key_counts.items():
            if count > 1:
                list_keys.add(key)
                output[key] = []

        # Second pass: populate values
        for prop in result.properties:
            value = self._property_to_value(prop)

            if prop.key in list_keys:
                output[prop.key].append(value)
            else:
                output[prop.key] = value

        return output

    def _property_to_value(self, prop: ParsedProperty) -> Any:
        """Convert a ParsedProperty back to its original value type.

        Args:
            prop: Parsed property

        Returns:
            Value in appropriate Python type
        """
        if prop.value_type == PropertyValueType.NUMBER:
            return prop.value_number

        if prop.value_type == PropertyValueType.BOOLEAN:
            return prop.property_value in ("true", "yes")

        if prop.value_type == PropertyValueType.DATE:
            return prop.value_date

        if prop.value_type == PropertyValueType.LINK:
            return prop.property_value  # Keep original format with [[]]

        return prop.property_value
