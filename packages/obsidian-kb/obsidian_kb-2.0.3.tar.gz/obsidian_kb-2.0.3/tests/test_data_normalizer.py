"""Тесты для DataNormalizer (core/data_normalizer.py).

Phase 5: Тестовая инфраструктура v0.7.0
"""

import json
from datetime import date, datetime

import pytest

from obsidian_kb.core.data_normalizer import DataNormalizer


class TestNormalizeTag:
    """Тесты для normalize_tag."""

    def test_basic_tag(self):
        """Базовая нормализация тега."""
        assert DataNormalizer.normalize_tag("Python") == "python"
        assert DataNormalizer.normalize_tag("REACT") == "react"

    def test_tag_with_spaces(self):
        """Тег с пробелами по краям."""
        assert DataNormalizer.normalize_tag("  python  ") == "python"

    def test_empty_tag(self):
        """Пустой тег возвращает пустую строку."""
        assert DataNormalizer.normalize_tag("") == ""
        assert DataNormalizer.normalize_tag("   ") == ""

    def test_none_tag(self):
        """None возвращает пустую строку."""
        assert DataNormalizer.normalize_tag(None) == ""

    def test_non_string_tag(self):
        """Не-строковое значение возвращает пустую строку."""
        assert DataNormalizer.normalize_tag(123) == ""
        assert DataNormalizer.normalize_tag([]) == ""


class TestNormalizeTags:
    """Тесты для normalize_tags."""

    def test_basic_list(self):
        """Нормализация списка тегов."""
        result = DataNormalizer.normalize_tags(["Python", "REACT", "vue"])
        assert result == ["python", "react", "vue"]

    def test_string_input(self):
        """Строка конвертируется в список из одного тега."""
        result = DataNormalizer.normalize_tags("python")
        assert result == ["python"]

    def test_removes_duplicates(self):
        """Дубликаты удаляются."""
        result = DataNormalizer.normalize_tags(["python", "Python", "PYTHON"])
        assert result == ["python"]

    def test_preserves_order(self):
        """Порядок сохраняется."""
        result = DataNormalizer.normalize_tags(["zebra", "apple", "mango"])
        assert result == ["zebra", "apple", "mango"]

    def test_removes_empty_tags(self):
        """Пустые теги удаляются."""
        result = DataNormalizer.normalize_tags(["python", "", "  ", "react"])
        assert result == ["python", "react"]

    def test_empty_input(self):
        """Пустой ввод возвращает пустой список."""
        assert DataNormalizer.normalize_tags([]) == []
        assert DataNormalizer.normalize_tags(None) == []


class TestNormalizeLink:
    """Тесты для normalize_link."""

    def test_basic_link(self):
        """Базовая нормализация ссылки."""
        assert DataNormalizer.normalize_link("MyNote") == "mynote"

    def test_link_with_display(self):
        """Ссылка с отображаемым текстом."""
        assert DataNormalizer.normalize_link("MyNote|Display Text") == "mynote"

    def test_link_with_path(self):
        """Ссылка с путём."""
        assert DataNormalizer.normalize_link("folder/subfolder/MyNote") == "mynote"

    def test_link_with_extension(self):
        """Ссылка с расширением .md."""
        assert DataNormalizer.normalize_link("MyNote.md") == "mynote"

    def test_complex_link(self):
        """Сложная ссылка с путём, расширением и отображением."""
        result = DataNormalizer.normalize_link("folder/MyNote.md|Displayed")
        assert result == "mynote"

    def test_empty_link(self):
        """Пустая ссылка."""
        assert DataNormalizer.normalize_link("") == ""
        assert DataNormalizer.normalize_link(None) == ""

    def test_link_with_spaces(self):
        """Ссылка с пробелами."""
        assert DataNormalizer.normalize_link("  My Note  ") == "my note"


class TestNormalizeLinks:
    """Тесты для normalize_links."""

    def test_basic_list(self):
        """Нормализация списка ссылок."""
        result = DataNormalizer.normalize_links(["NoteA", "NoteB"])
        assert result == ["notea", "noteb"]

    def test_removes_duplicates(self):
        """Дубликаты удаляются."""
        result = DataNormalizer.normalize_links(["Note", "NOTE", "note"])
        assert result == ["note"]

    def test_empty_input(self):
        """Пустой ввод."""
        assert DataNormalizer.normalize_links([]) == []
        assert DataNormalizer.normalize_links(None) == []


class TestNormalizeDocType:
    """Тесты для normalize_doc_type."""

    def test_basic_doc_type(self):
        """Базовая нормализация типа документа."""
        assert DataNormalizer.normalize_doc_type("Meeting") == "meeting"
        assert DataNormalizer.normalize_doc_type("  Note  ") == "note"

    def test_empty_doc_type(self):
        """Пустой тип документа."""
        assert DataNormalizer.normalize_doc_type("") == ""
        assert DataNormalizer.normalize_doc_type(None) == ""


class TestNormalizeString:
    """Тесты для normalize_string."""

    def test_basic_string(self):
        """Базовая нормализация строки."""
        assert DataNormalizer.normalize_string("Hello World") == "hello world"

    def test_string_with_spaces(self):
        """Строка с пробелами по краям."""
        assert DataNormalizer.normalize_string("  hello  ") == "hello"

    def test_empty_string(self):
        """Пустая строка."""
        assert DataNormalizer.normalize_string("") == ""
        assert DataNormalizer.normalize_string(None) == ""


class TestEscapeSqlString:
    """Тесты для escape_sql_string."""

    def test_basic_escape(self):
        """Базовое экранирование."""
        assert DataNormalizer.escape_sql_string("test") == "test"

    def test_escape_single_quotes(self):
        """Экранирование одинарных кавычек."""
        assert DataNormalizer.escape_sql_string("it's") == "it''s"
        assert DataNormalizer.escape_sql_string("'test'") == "''test''"

    def test_empty_string(self):
        """Пустая строка."""
        assert DataNormalizer.escape_sql_string("") == ""


class TestNormalizePropertyValue:
    """Тесты для normalize_property_value."""

    def test_string_value(self):
        """Строковое значение."""
        assert DataNormalizer.normalize_property_value("Hello") == "hello"

    def test_number_value(self):
        """Числовое значение."""
        assert DataNormalizer.normalize_property_value(42) == "42"
        assert DataNormalizer.normalize_property_value(3.14) == "3.14"

    def test_boolean_value(self):
        """Булево значение."""
        assert DataNormalizer.normalize_property_value(True) == "true"
        assert DataNormalizer.normalize_property_value(False) == "false"

    def test_list_value(self):
        """Списочное значение."""
        result = DataNormalizer.normalize_property_value(["Tag1", "TAG2"])
        assert result == "tag1,tag2"

    def test_other_value(self):
        """Другие типы значений."""
        assert DataNormalizer.normalize_property_value({"key": "value"}) == "{'key': 'value'}"


class TestGetPropertyType:
    """Тесты для get_property_type."""

    def test_string_type(self):
        """Строковый тип."""
        assert DataNormalizer.get_property_type("hello") == "string"

    def test_number_type(self):
        """Числовой тип."""
        assert DataNormalizer.get_property_type(42) == "number"
        assert DataNormalizer.get_property_type(3.14) == "number"

    def test_date_type(self):
        """Датовый тип."""
        assert DataNormalizer.get_property_type(date(2024, 1, 1)) == "date"
        assert DataNormalizer.get_property_type(datetime(2024, 1, 1, 12, 0)) == "date"

    def test_array_type(self):
        """Списочный тип."""
        assert DataNormalizer.get_property_type([1, 2, 3]) == "array"

    def test_boolean_type(self):
        """Булев тип."""
        assert DataNormalizer.get_property_type(True) == "boolean"
        assert DataNormalizer.get_property_type(False) == "boolean"

    def test_unknown_type(self):
        """Неизвестный тип возвращает string."""
        assert DataNormalizer.get_property_type({"key": "value"}) == "string"


class TestSerializeMetadata:
    """Тесты для serialize_metadata."""

    def test_basic_metadata(self):
        """Базовая сериализация."""
        metadata = {"title": "Test", "count": 42}
        result = DataNormalizer.serialize_metadata(metadata)
        assert result == {"title": "Test", "count": 42}

    def test_date_serialization(self):
        """Сериализация дат."""
        metadata = {
            "created": date(2024, 1, 15),
            "modified": datetime(2024, 1, 15, 12, 30, 0),
        }
        result = DataNormalizer.serialize_metadata(metadata)
        assert result["created"] == "2024-01-15"
        assert result["modified"] == "2024-01-15T12:30:00"

    def test_nested_dict(self):
        """Вложенный словарь."""
        metadata = {
            "nested": {
                "date": date(2024, 1, 1),
                "value": "test",
            }
        }
        result = DataNormalizer.serialize_metadata(metadata)
        assert result["nested"]["date"] == "2024-01-01"
        assert result["nested"]["value"] == "test"

    def test_list_with_dates(self):
        """Список с датами."""
        metadata = {
            "dates": [date(2024, 1, 1), date(2024, 1, 2), "not a date"]
        }
        result = DataNormalizer.serialize_metadata(metadata)
        assert result["dates"] == ["2024-01-01", "2024-01-02", "not a date"]


class TestComputeMetadataHash:
    """Тесты для compute_metadata_hash."""

    def test_consistent_hash(self):
        """Хеш для одинаковых данных одинаков."""
        metadata = {"title": "Test", "author": "User"}
        hash1 = DataNormalizer.compute_metadata_hash(metadata)
        hash2 = DataNormalizer.compute_metadata_hash(metadata)
        assert hash1 == hash2

    def test_different_hash_for_different_data(self):
        """Разные данные дают разные хеши."""
        hash1 = DataNormalizer.compute_metadata_hash({"title": "Test1"})
        hash2 = DataNormalizer.compute_metadata_hash({"title": "Test2"})
        assert hash1 != hash2

    def test_hash_is_sha256(self):
        """Хеш имеет длину SHA256."""
        hash_result = DataNormalizer.compute_metadata_hash({"test": "data"})
        assert len(hash_result) == 64  # SHA256 hex = 64 characters

    def test_key_order_independent(self):
        """Порядок ключей не влияет на хеш."""
        hash1 = DataNormalizer.compute_metadata_hash({"a": 1, "b": 2})
        hash2 = DataNormalizer.compute_metadata_hash({"b": 2, "a": 1})
        assert hash1 == hash2


class TestComputeContentHash:
    """Тесты для compute_content_hash."""

    def test_consistent_hash(self):
        """Хеш для одинакового контента одинаков."""
        hash1 = DataNormalizer.compute_content_hash("Hello World")
        hash2 = DataNormalizer.compute_content_hash("Hello World")
        assert hash1 == hash2

    def test_different_hash(self):
        """Разный контент даёт разные хеши."""
        hash1 = DataNormalizer.compute_content_hash("Hello")
        hash2 = DataNormalizer.compute_content_hash("World")
        assert hash1 != hash2

    def test_truncated_hash(self):
        """Хеш обрезается до 16 символов."""
        hash_result = DataNormalizer.compute_content_hash("test")
        assert len(hash_result) == 16


class TestNormalizeVaultName:
    """Тесты для normalize_vault_name."""

    def test_basic_vault_name(self):
        """Базовая нормализация имени vault."""
        assert DataNormalizer.normalize_vault_name("MyVault") == "myvault"

    def test_vault_name_with_spaces(self):
        """Пробелы заменяются на подчёркивания."""
        assert DataNormalizer.normalize_vault_name("My Vault") == "my_vault"

    def test_vault_name_with_surrounding_spaces(self):
        """Пробелы по краям убираются."""
        assert DataNormalizer.normalize_vault_name("  vault  ") == "vault"

    def test_empty_vault_name(self):
        """Пустое имя vault."""
        assert DataNormalizer.normalize_vault_name("") == ""
        assert DataNormalizer.normalize_vault_name(None) == ""
