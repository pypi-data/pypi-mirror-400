"""Tests for FrontmatterParser."""

from datetime import date, datetime

import pytest

from obsidian_kb.storage.sqlite.frontmatter_parser import (
    FrontmatterParseResult,
    FrontmatterParser,
    ParsedProperty,
    PropertyValueType,
)


@pytest.fixture
def parser() -> FrontmatterParser:
    """Create parser instance."""
    return FrontmatterParser()


class TestParsedProperty:
    """Tests for ParsedProperty dataclass."""

    def test_create_string_property(self):
        """Test creating string property."""
        prop = ParsedProperty(
            key="status",
            value_type=PropertyValueType.STRING,
            property_value="active",
        )

        assert prop.key == "status"
        assert prop.value_type == PropertyValueType.STRING
        assert prop.property_value == "active"
        assert prop.list_index == 0

    def test_create_number_property(self):
        """Test creating number property."""
        prop = ParsedProperty(
            key="priority",
            value_type=PropertyValueType.NUMBER,
            property_value="5",
            value_number=5.0,
        )

        assert prop.key == "priority"
        assert prop.value_type == PropertyValueType.NUMBER
        assert prop.value_number == 5.0

    def test_create_link_property(self):
        """Test creating link property."""
        prop = ParsedProperty(
            key="participant",
            value_type=PropertyValueType.LINK,
            property_value="[[vshadrin]]",
            value_link_target="vshadrin",
        )

        assert prop.key == "participant"
        assert prop.value_type == PropertyValueType.LINK
        assert prop.value_link_target == "vshadrin"

    def test_create_date_property(self):
        """Test creating date property."""
        prop = ParsedProperty(
            key="date",
            value_type=PropertyValueType.DATE,
            property_value="2025-01-08",
            value_date="2025-01-08",
        )

        assert prop.key == "date"
        assert prop.value_type == PropertyValueType.DATE
        assert prop.value_date == "2025-01-08"


class TestFrontmatterParseResult:
    """Tests for FrontmatterParseResult dataclass."""

    def test_empty_result(self):
        """Test empty result."""
        result = FrontmatterParseResult()

        assert result.properties == []
        assert result.raw_frontmatter is None
        assert result.parse_errors == []
        assert result.success is True
        assert result.property_count == 0

    def test_result_with_properties(self):
        """Test result with properties."""
        result = FrontmatterParseResult(
            properties=[
                ParsedProperty(key="a", value_type=PropertyValueType.STRING),
                ParsedProperty(key="b", value_type=PropertyValueType.NUMBER),
            ],
            raw_frontmatter="a: 1\nb: 2",
        )

        assert result.property_count == 2
        assert result.success is True

    def test_result_with_errors(self):
        """Test result with parse errors."""
        result = FrontmatterParseResult(
            parse_errors=["YAML parse error: invalid syntax"],
        )

        assert result.success is False


class TestFrontmatterParserBasic:
    """Basic parsing tests for FrontmatterParser."""

    def test_parse_empty_content(self, parser: FrontmatterParser):
        """Test parsing empty content."""
        result = parser.parse("")

        assert result.success is True
        assert result.property_count == 0

    def test_parse_no_frontmatter(self, parser: FrontmatterParser):
        """Test parsing content without frontmatter."""
        content = "# Hello World\n\nSome content here."
        result = parser.parse(content)

        assert result.success is True
        assert result.property_count == 0

    def test_parse_simple_frontmatter(self, parser: FrontmatterParser):
        """Test parsing simple frontmatter."""
        content = """---
status: active
title: My Note
---

# Content here
"""
        result = parser.parse(content)

        assert result.success is True
        assert result.property_count == 2
        assert result.raw_frontmatter is not None

        keys = {p.key for p in result.properties}
        assert "status" in keys
        assert "title" in keys

    def test_parse_yaml_only(self, parser: FrontmatterParser):
        """Test parsing raw YAML."""
        yaml_content = "status: active\ncount: 5"
        result = parser.parse_yaml(yaml_content)

        assert result.success is True
        assert result.property_count == 2


class TestFrontmatterParserStringValues:
    """Tests for string value parsing."""

    def test_parse_simple_string(self, parser: FrontmatterParser):
        """Test parsing simple string value."""
        result = parser.parse_yaml("status: active")

        assert result.property_count == 1
        prop = result.properties[0]
        assert prop.key == "status"
        assert prop.value_type == PropertyValueType.STRING
        assert prop.property_value == "active"

    def test_parse_quoted_string(self, parser: FrontmatterParser):
        """Test parsing quoted string value."""
        result = parser.parse_yaml('title: "My Great Note"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.STRING
        assert prop.property_value == "My Great Note"

    def test_parse_multiword_string(self, parser: FrontmatterParser):
        """Test parsing multi-word string."""
        result = parser.parse_yaml("title: Hello World Today")

        prop = result.properties[0]
        assert prop.property_value == "Hello World Today"

    def test_parse_null_value(self, parser: FrontmatterParser):
        """Test parsing null/empty value."""
        result = parser.parse_yaml("empty_field:")

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.STRING
        assert prop.property_value is None


class TestFrontmatterParserNumberValues:
    """Tests for number value parsing."""

    def test_parse_integer(self, parser: FrontmatterParser):
        """Test parsing integer value."""
        result = parser.parse_yaml("priority: 5")

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.NUMBER
        assert prop.value_number == 5.0
        assert prop.property_value == "5"

    def test_parse_float(self, parser: FrontmatterParser):
        """Test parsing float value."""
        result = parser.parse_yaml("score: 3.14")

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.NUMBER
        assert prop.value_number == 3.14

    def test_parse_negative_number(self, parser: FrontmatterParser):
        """Test parsing negative number."""
        result = parser.parse_yaml("offset: -10")

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.NUMBER
        assert prop.value_number == -10.0

    def test_parse_zero(self, parser: FrontmatterParser):
        """Test parsing zero."""
        result = parser.parse_yaml("count: 0")

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.NUMBER
        assert prop.value_number == 0.0


class TestFrontmatterParserDateValues:
    """Tests for date value parsing."""

    def test_parse_yaml_date(self, parser: FrontmatterParser):
        """Test parsing YAML native date."""
        result = parser.parse_yaml("date: 2025-01-08")

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.DATE
        assert prop.value_date == "2025-01-08"

    def test_parse_date_string(self, parser: FrontmatterParser):
        """Test parsing date as string."""
        result = parser.parse_yaml('date: "2025-01-08"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.DATE
        assert prop.value_date == "2025-01-08"

    def test_parse_date_with_slashes(self, parser: FrontmatterParser):
        """Test parsing date with slashes."""
        result = parser.parse_yaml('date: "2025/01/08"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.DATE
        assert prop.value_date == "2025-01-08"

    def test_parse_datetime_object(self, parser: FrontmatterParser):
        """Test parsing datetime object (from YAML)."""
        # YAML parses this as datetime
        yaml_content = "created: 2025-01-08"
        result = parser.parse_yaml(yaml_content)

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.DATE


class TestFrontmatterParserBooleanValues:
    """Tests for boolean value parsing."""

    def test_parse_true(self, parser: FrontmatterParser):
        """Test parsing true value."""
        result = parser.parse_yaml("active: true")

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.BOOLEAN
        assert prop.property_value == "true"

    def test_parse_false(self, parser: FrontmatterParser):
        """Test parsing false value."""
        result = parser.parse_yaml("archived: false")

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.BOOLEAN
        assert prop.property_value == "false"

    def test_parse_yes(self, parser: FrontmatterParser):
        """Test parsing 'yes' as boolean."""
        result = parser.parse_yaml('published: "yes"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.BOOLEAN
        assert prop.property_value == "yes"

    def test_parse_no(self, parser: FrontmatterParser):
        """Test parsing 'no' as boolean."""
        result = parser.parse_yaml('draft: "no"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.BOOLEAN
        assert prop.property_value == "no"


class TestFrontmatterParserLinkValues:
    """Tests for wikilink value parsing."""

    def test_parse_simple_link(self, parser: FrontmatterParser):
        """Test parsing simple [[link]]."""
        result = parser.parse_yaml('participant: "[[vshadrin]]"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.LINK
        assert prop.value_link_target == "vshadrin"
        assert prop.property_value == "[[vshadrin]]"

    def test_parse_link_with_alias(self, parser: FrontmatterParser):
        """Test parsing link with alias [[target|alias]]."""
        result = parser.parse_yaml('person: "[[john-doe|John Doe]]"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.LINK
        assert prop.value_link_target == "john-doe"

    def test_parse_link_with_path(self, parser: FrontmatterParser):
        """Test parsing link with path."""
        result = parser.parse_yaml('reference: "[[folder/note]]"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.LINK
        assert prop.value_link_target == "folder/note"


class TestFrontmatterParserListValues:
    """Tests for list/array value parsing."""

    def test_parse_string_list(self, parser: FrontmatterParser):
        """Test parsing string list."""
        result = parser.parse_yaml("tags: [meeting, q1, planning]")

        assert result.property_count == 3

        # All have same key, different list_index
        for i, prop in enumerate(result.properties):
            assert prop.key == "tags"
            assert prop.list_index == i
            assert prop.value_type == PropertyValueType.STRING

        values = [p.property_value for p in result.properties]
        assert "meeting" in values
        assert "q1" in values
        assert "planning" in values

    def test_parse_number_list(self, parser: FrontmatterParser):
        """Test parsing number list."""
        result = parser.parse_yaml("scores: [10, 20, 30]")

        assert result.property_count == 3

        for prop in result.properties:
            assert prop.value_type == PropertyValueType.NUMBER

        numbers = [p.value_number for p in result.properties]
        assert numbers == [10.0, 20.0, 30.0]

    def test_parse_mixed_list(self, parser: FrontmatterParser):
        """Test parsing mixed type list."""
        result = parser.parse_yaml('items: [1, "two", true]')

        assert result.property_count == 3

        types = [p.value_type for p in result.properties]
        assert PropertyValueType.NUMBER in types
        assert PropertyValueType.STRING in types
        assert PropertyValueType.BOOLEAN in types

    def test_parse_link_list(self, parser: FrontmatterParser):
        """Test parsing list of links."""
        result = parser.parse_yaml('participants: ["[[alice]]", "[[bob]]"]')

        assert result.property_count == 2

        for prop in result.properties:
            assert prop.value_type == PropertyValueType.LINK

        targets = [p.value_link_target for p in result.properties]
        assert "alice" in targets
        assert "bob" in targets

    def test_parse_multiline_list(self, parser: FrontmatterParser):
        """Test parsing multiline list."""
        yaml_content = """tags:
  - meeting
  - planning
  - q1"""
        result = parser.parse_yaml(yaml_content)

        assert result.property_count == 3

    def test_parse_empty_list(self, parser: FrontmatterParser):
        """Test parsing empty list."""
        result = parser.parse_yaml("tags: []")

        assert result.property_count == 0


class TestFrontmatterParserComplexExample:
    """Tests for complex frontmatter examples."""

    def test_parse_full_example(self, parser: FrontmatterParser):
        """Test parsing the full example from requirements."""
        content = """---
type: 1-1
participant: "[[vshadrin]]"
date: 2025-01-08
status: active
tags: [meeting, q1]
priority: 1
---

# Meeting Notes

Content here...
"""
        result = parser.parse(content)

        assert result.success is True
        # 1 type + 1 participant + 1 date + 1 status + 2 tags + 1 priority = 7
        assert result.property_count == 7

        # Check type
        type_props = [p for p in result.properties if p.key == "type"]
        assert len(type_props) == 1
        assert type_props[0].value_type == PropertyValueType.STRING
        assert type_props[0].property_value == "1-1"

        # Check participant
        participant_props = [p for p in result.properties if p.key == "participant"]
        assert len(participant_props) == 1
        assert participant_props[0].value_type == PropertyValueType.LINK
        assert participant_props[0].value_link_target == "vshadrin"

        # Check date
        date_props = [p for p in result.properties if p.key == "date"]
        assert len(date_props) == 1
        assert date_props[0].value_type == PropertyValueType.DATE
        assert date_props[0].value_date == "2025-01-08"

        # Check status
        status_props = [p for p in result.properties if p.key == "status"]
        assert len(status_props) == 1
        assert status_props[0].property_value == "active"

        # Check tags
        tags_props = [p for p in result.properties if p.key == "tags"]
        assert len(tags_props) == 2
        tag_values = {p.property_value for p in tags_props}
        assert tag_values == {"meeting", "q1"}
        # Check list indices
        indices = {p.list_index for p in tags_props}
        assert indices == {0, 1}

        # Check priority
        priority_props = [p for p in result.properties if p.key == "priority"]
        assert len(priority_props) == 1
        assert priority_props[0].value_type == PropertyValueType.NUMBER
        assert priority_props[0].value_number == 1.0

    def test_parse_nested_object(self, parser: FrontmatterParser):
        """Test parsing nested object (converted to JSON string)."""
        yaml_content = """metadata:
  author: John
  version: 1.0"""
        result = parser.parse_yaml(yaml_content)

        assert result.property_count == 1
        prop = result.properties[0]
        assert prop.key == "metadata"
        assert prop.value_type == PropertyValueType.STRING
        assert '"author"' in prop.property_value
        assert '"John"' in prop.property_value


class TestFrontmatterParserErrorHandling:
    """Tests for error handling."""

    def test_parse_invalid_yaml(self, parser: FrontmatterParser):
        """Test parsing invalid YAML."""
        content = """---
invalid: [unclosed
---
"""
        result = parser.parse(content)

        assert result.success is False
        assert len(result.parse_errors) > 0

    def test_parse_non_dict_yaml(self, parser: FrontmatterParser):
        """Test parsing YAML that's not a dict."""
        result = parser.parse_yaml("- item1\n- item2")

        assert result.success is False
        assert "Expected dict" in result.parse_errors[0]


class TestFrontmatterParserHelpers:
    """Tests for helper methods."""

    def test_extract_all_links(self, parser: FrontmatterParser):
        """Test extracting all links from result."""
        yaml_content = """
author: "[[john]]"
reviewers:
  - "[[alice]]"
  - "[[bob]]"
status: active
"""
        result = parser.parse_yaml(yaml_content)
        links = parser.extract_all_links(result)

        assert len(links) == 3
        assert "john" in links
        assert "alice" in links
        assert "bob" in links

    def test_get_properties_by_key(self, parser: FrontmatterParser):
        """Test getting properties by key."""
        yaml_content = "tags: [a, b, c]\nstatus: active"
        result = parser.parse_yaml(yaml_content)

        tags = parser.get_properties_by_key(result, "tags")
        assert len(tags) == 3

        status = parser.get_properties_by_key(result, "status")
        assert len(status) == 1

    def test_to_dict(self, parser: FrontmatterParser):
        """Test converting result back to dict."""
        yaml_content = """status: active
tags: [a, b]
count: 5"""
        result = parser.parse_yaml(yaml_content)
        output = parser.to_dict(result)

        assert output["status"] == "active"
        assert output["tags"] == ["a", "b"]
        assert output["count"] == 5.0


class TestFrontmatterParserEdgeCases:
    """Tests for edge cases."""

    def test_parse_special_characters_in_value(self, parser: FrontmatterParser):
        """Test parsing values with special characters."""
        result = parser.parse_yaml('note: "Status: active (v1.0)"')

        prop = result.properties[0]
        assert prop.property_value == "Status: active (v1.0)"

    def test_parse_unicode_values(self, parser: FrontmatterParser):
        """Test parsing Unicode values."""
        result = parser.parse_yaml('title: "Заметка на русском"')

        prop = result.properties[0]
        assert prop.property_value == "Заметка на русском"

    def test_parse_version_not_as_number(self, parser: FrontmatterParser):
        """Test that version-like strings are not parsed as numbers."""
        result = parser.parse_yaml('version: "1.2.3"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.STRING
        assert prop.property_value == "1.2.3"

    def test_parse_leading_zero_not_as_number(self, parser: FrontmatterParser):
        """Test that strings with leading zeros are not parsed as numbers."""
        result = parser.parse_yaml('code: "007"')

        prop = result.properties[0]
        assert prop.value_type == PropertyValueType.STRING
        assert prop.property_value == "007"

    def test_parse_empty_frontmatter(self, parser: FrontmatterParser):
        """Test parsing empty frontmatter block."""
        content = """---
---

# Content
"""
        result = parser.parse(content)

        assert result.success is True
        assert result.property_count == 0

    def test_parse_whitespace_only_frontmatter(self, parser: FrontmatterParser):
        """Test parsing whitespace-only frontmatter."""
        content = """---

---

# Content
"""
        result = parser.parse(content)

        assert result.success is True
        assert result.property_count == 0
