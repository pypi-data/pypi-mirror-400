"""Тесты для модуля normalization."""

import pytest

from obsidian_kb.normalization import DataNormalizer


class TestDataNormalizer:
    """Тесты для DataNormalizer."""
    
    def test_normalize_tag(self):
        """Тест нормализации одного тега."""
        assert DataNormalizer.normalize_tag("Meeting") == "meeting"
        assert DataNormalizer.normalize_tag("  TAG  ") == "tag"
        assert DataNormalizer.normalize_tag("") == ""
        assert DataNormalizer.normalize_tag(None) == ""
        assert DataNormalizer.normalize_tag("Tag-Name") == "tag-name"
    
    def test_normalize_tags(self):
        """Тест нормализации списка тегов."""
        assert DataNormalizer.normalize_tags(["Tag1", "Tag2"]) == ["tag1", "tag2"]
        assert DataNormalizer.normalize_tags(["Tag1", "tag1"]) == ["tag1"]  # Дубликаты
        assert DataNormalizer.normalize_tags("SingleTag") == ["singletag"]
        assert DataNormalizer.normalize_tags([]) == []
        assert DataNormalizer.normalize_tags(None) == []
        assert DataNormalizer.normalize_tags(["  Tag1  ", "  Tag2  "]) == ["tag1", "tag2"]
    
    def test_normalize_link(self):
        """Тест нормализации одной ссылки."""
        assert DataNormalizer.normalize_link("muratov") == "muratov"
        assert DataNormalizer.normalize_link("07_PEOPLE/muratov/profile") == "profile"
        assert DataNormalizer.normalize_link("link|display") == "link"  # Уже извлеченная из [[...]]
        assert DataNormalizer.normalize_link("file.md") == "file"
        assert DataNormalizer.normalize_link("path/to/file.md") == "file"
        assert DataNormalizer.normalize_link("") == ""
        assert DataNormalizer.normalize_link(None) == ""
        assert DataNormalizer.normalize_link("  LINK  ") == "link"
    
    def test_normalize_links(self):
        """Тест нормализации списка ссылок."""
        assert DataNormalizer.normalize_links(["muratov", "person"]) == ["muratov", "person"]
        assert DataNormalizer.normalize_links(["muratov", "MURATOV"]) == ["muratov"]  # Дубликаты
        assert DataNormalizer.normalize_links(["path/to/file", "other"]) == ["file", "other"]
        assert DataNormalizer.normalize_links([]) == []
        assert DataNormalizer.normalize_links(None) == []
    
    def test_normalize_doc_type(self):
        """Тест нормализации типа документа."""
        assert DataNormalizer.normalize_doc_type("Person") == "person"
        assert DataNormalizer.normalize_doc_type("  1-1  ") == "1-1"
        assert DataNormalizer.normalize_doc_type("") == ""
        assert DataNormalizer.normalize_doc_type(None) == ""
        assert DataNormalizer.normalize_doc_type("Meeting") == "meeting"
    
    def test_escape_sql_string(self):
        """Тест экранирования SQL строк."""
        assert DataNormalizer.escape_sql_string("test") == "test"
        assert DataNormalizer.escape_sql_string("test'value") == "test''value"
        assert DataNormalizer.escape_sql_string("") == ""
        assert DataNormalizer.escape_sql_string("O'Brien") == "O''Brien"

