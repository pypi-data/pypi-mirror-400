"""Тесты для DocumentRecordBuilder (storage/builders/document_builder.py).

Phase 5: Тестовая инфраструктура v0.7.0
"""

import json
from datetime import datetime

import pytest

from obsidian_kb.core.data_normalizer import DataNormalizer
from obsidian_kb.storage.builders.document_builder import DocumentRecordBuilder
from obsidian_kb.types import DocumentChunk


@pytest.fixture
def normalizer():
    """Фикстура для DataNormalizer."""
    return DataNormalizer()


@pytest.fixture
def builder(normalizer):
    """Фикстура для DocumentRecordBuilder."""
    return DocumentRecordBuilder(normalizer)


@pytest.fixture
def sample_chunk():
    """Базовый чанк для тестов."""
    return DocumentChunk(
        id="test_vault::notes/test.md::0",
        vault_name="test_vault",
        file_path="notes/test.md",
        title="Test Document",
        section="Introduction",
        content="This is a test content for the chunk.",
        tags=["python", "testing"],
        frontmatter_tags=["python", "docs"],
        inline_tags=["testing"],
        links=["related_note", "another_note"],
        created_at=datetime(2024, 1, 1, 10, 0, 0),
        modified_at=datetime(2024, 1, 15, 14, 30, 0),
        metadata={
            "type": "note",
            "author": "tester",
            "priority": 1,
            "draft": True,
            "tags": ["python", "docs"],
        },
    )


class TestDocumentRecordBuilderInit:
    """Тесты инициализации DocumentRecordBuilder."""

    def test_with_normalizer(self, normalizer):
        """Инициализация с переданным normalizer."""
        builder = DocumentRecordBuilder(normalizer)
        assert builder._normalizer is normalizer

    def test_without_normalizer(self):
        """Инициализация без normalizer создаёт дефолтный."""
        builder = DocumentRecordBuilder()
        assert builder._normalizer is not None
        assert isinstance(builder._normalizer, DataNormalizer)


class TestBuildRecord:
    """Тесты для метода build_record."""

    def test_basic_record(self, builder, sample_chunk):
        """Базовое построение записи документа."""
        record = builder.build_record(sample_chunk, "test_vault")

        assert record["document_id"] == "test_vault::notes/test.md"
        assert record["vault_name"] == "test_vault"
        assert record["file_path"] == "notes/test.md"
        assert record["file_name"] == "test.md"
        assert record["file_extension"] == ".md"
        assert record["title"] == "Test Document"
        assert record["content_type"] == "markdown"
        assert record["chunk_count"] == 0  # Будет обновлено позже

    def test_date_formatting(self, builder, sample_chunk):
        """Форматирование дат."""
        record = builder.build_record(sample_chunk, "test_vault")

        assert record["created_at"] == "2024-01-01T10:00:00"
        assert record["modified_at"] == "2024-01-15T14:30:00"

    def test_no_created_at(self, builder):
        """Документ без даты создания."""
        chunk = DocumentChunk(
            id="vault::file.md::0",
            vault_name="vault",
            file_path="file.md",
            title="Title",
            section="",
            content="Content",
            tags=[],
            frontmatter_tags=[],
            inline_tags=[],
            links=[],
            created_at=None,
            modified_at=datetime(2024, 1, 15, 12, 0, 0),
            metadata={},
        )
        record = builder.build_record(chunk, "vault")
        assert record["created_at"] == ""

    def test_with_content_hash(self, builder, sample_chunk):
        """Запись с переданным content_hash."""
        record = builder.build_record(
            sample_chunk, "test_vault", content_hash="abc123"
        )
        assert record["content_hash"] == "abc123"

    def test_content_type_detection(self, builder):
        """Определение типа контента."""
        test_cases = [
            ("file.md", "markdown"),
            ("document.pdf", "pdf"),
            ("image.png", "image"),
            ("image.jpg", "image"),
            ("image.jpeg", "image"),
            ("image.gif", "image"),
            ("image.svg", "image"),
            ("unknown.xyz", "unknown"),
        ]

        for file_path, expected_type in test_cases:
            chunk = DocumentChunk(
                id=f"vault::{file_path}::0",
                vault_name="vault",
                file_path=file_path,
                title="Title",
                section="",
                content="",
                tags=[],
                frontmatter_tags=[],
                inline_tags=[],
                links=[],
                created_at=None,
                modified_at=datetime.now(),
                metadata={},
            )
            record = builder.build_record(chunk, "vault")
            assert record["content_type"] == expected_type, f"Failed for {file_path}"


class TestBuildPropertiesRecords:
    """Тесты для метода build_properties_records."""

    def test_basic_properties(self, builder, sample_chunk):
        """Базовое извлечение свойств."""
        properties = builder.build_properties_records(sample_chunk, "test_vault")

        # tags пропускаются
        property_keys = [p["property_key"] for p in properties]
        assert "tags" not in property_keys
        assert "type" in property_keys
        assert "author" in property_keys
        assert "priority" in property_keys
        assert "draft" in property_keys

    def test_property_structure(self, builder, sample_chunk):
        """Структура записи свойства."""
        properties = builder.build_properties_records(sample_chunk, "test_vault")

        # Найдём свойство author
        author_prop = next(p for p in properties if p["property_key"] == "author")

        assert author_prop["property_id"] == "test_vault::notes/test.md::author"
        assert author_prop["document_id"] == "test_vault::notes/test.md"
        assert author_prop["vault_name"] == "test_vault"
        assert author_prop["property_value"] == "tester"  # Нормализованное
        assert author_prop["property_value_raw"] == "tester"
        assert author_prop["property_type"] == "string"

    def test_property_types(self, builder, sample_chunk):
        """Определение типов свойств."""
        properties = builder.build_properties_records(sample_chunk, "test_vault")

        types = {p["property_key"]: p["property_type"] for p in properties}

        assert types["type"] == "string"
        assert types["author"] == "string"
        assert types["priority"] == "number"
        assert types["draft"] == "boolean"

    def test_custom_document_id(self, builder, sample_chunk):
        """Использование кастомного document_id."""
        custom_id = "custom::document::id"
        properties = builder.build_properties_records(
            sample_chunk, "test_vault", document_id=custom_id
        )

        for prop in properties:
            assert prop["document_id"] == custom_id
            assert prop["property_id"].startswith(custom_id)

    def test_empty_metadata(self, builder):
        """Чанк с пустым metadata."""
        chunk = DocumentChunk(
            id="vault::file.md::0",
            vault_name="vault",
            file_path="file.md",
            title="Title",
            section="",
            content="",
            tags=[],
            frontmatter_tags=[],
            inline_tags=[],
            links=[],
            created_at=None,
            modified_at=datetime.now(),
            metadata={},
        )
        properties = builder.build_properties_records(chunk, "vault")
        assert properties == []


class TestBuildMetadataRecord:
    """Тесты для метода build_metadata_record."""

    def test_basic_metadata(self, builder, sample_chunk):
        """Базовое построение записи metadata."""
        record = builder.build_metadata_record(sample_chunk, "test_vault")

        assert record["document_id"] == "test_vault::notes/test.md"
        assert record["vault_name"] == "test_vault"
        assert record["frontmatter_tags"] == ["python", "docs"]
        assert "metadata_json" in record
        assert "metadata_hash" in record

    def test_metadata_json_format(self, builder, sample_chunk):
        """metadata_json содержит сериализованный JSON."""
        record = builder.build_metadata_record(sample_chunk, "test_vault")

        metadata = json.loads(record["metadata_json"])
        assert metadata["type"] == "note"
        assert metadata["author"] == "tester"

    def test_metadata_hash_consistency(self, builder, sample_chunk):
        """Хеш metadata консистентен."""
        record1 = builder.build_metadata_record(sample_chunk, "test_vault")
        record2 = builder.build_metadata_record(sample_chunk, "test_vault")

        assert record1["metadata_hash"] == record2["metadata_hash"]


class TestHelperMethods:
    """Тесты вспомогательных методов."""

    def test_get_full_path(self, builder):
        """_get_full_path возвращает Path."""
        from pathlib import Path

        result = builder._get_full_path("notes/test.md")
        assert isinstance(result, Path)
        assert str(result) == "notes/test.md"

    def test_get_file_size(self, builder):
        """_get_file_size возвращает 0 (TODO: реализация)."""
        result = builder._get_file_size("notes/test.md")
        assert result == 0
