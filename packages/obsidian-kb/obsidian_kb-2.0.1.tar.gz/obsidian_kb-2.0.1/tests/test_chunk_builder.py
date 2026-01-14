"""Тесты для ChunkRecordBuilder (storage/builders/chunk_builder.py).

Phase 5: Тестовая инфраструктура v0.7.0
"""

from datetime import datetime

import pytest

from obsidian_kb.core.data_normalizer import DataNormalizer
from obsidian_kb.storage.builders.chunk_builder import ChunkRecordBuilder
from obsidian_kb.types import DocumentChunk


@pytest.fixture
def normalizer():
    """Фикстура для DataNormalizer."""
    return DataNormalizer()


@pytest.fixture
def builder(normalizer):
    """Фикстура для ChunkRecordBuilder."""
    return ChunkRecordBuilder(normalizer)


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
        frontmatter_tags=["python"],
        inline_tags=["testing"],
        links=["related_note", "another_note"],
        created_at=datetime(2024, 1, 1, 10, 0, 0),
        modified_at=datetime(2024, 1, 15, 14, 30, 0),
        metadata={"type": "note", "author": "tester"},
    )


@pytest.fixture
def sample_embedding():
    """Базовый embedding для тестов."""
    return [0.1, 0.2, 0.3, 0.4, 0.5]


class TestChunkRecordBuilderInit:
    """Тесты инициализации ChunkRecordBuilder."""

    def test_with_normalizer(self, normalizer):
        """Инициализация с переданным normalizer."""
        builder = ChunkRecordBuilder(normalizer)
        assert builder._normalizer is normalizer

    def test_without_normalizer(self):
        """Инициализация без normalizer создаёт дефолтный."""
        builder = ChunkRecordBuilder()
        assert builder._normalizer is not None
        assert isinstance(builder._normalizer, DataNormalizer)


class TestBuildRecord:
    """Тесты для метода build_record."""

    def test_basic_record(self, builder, sample_chunk, sample_embedding):
        """Базовое построение записи."""
        record = builder.build_record(sample_chunk, sample_embedding, "test_vault")

        assert record["chunk_id"] == "test_vault::notes/test.md::0"
        assert record["document_id"] == "test_vault::notes/test.md"
        assert record["vault_name"] == "test_vault"
        assert record["chunk_index"] == 0
        assert record["section"] == "Introduction"
        assert record["content"] == "This is a test content for the chunk."
        assert record["vector"] == sample_embedding
        assert record["links"] == ["related_note", "another_note"]
        assert record["inline_tags"] == ["testing"]

    def test_chunk_index_extraction(self, builder, sample_embedding):
        """Извлечение chunk_index из id."""
        chunk = DocumentChunk(
            id="vault::file.md::5",
            vault_name="vault",
            file_path="file.md",
            title="Title",
            section="Section",
            content="Content",
            tags=[],
            frontmatter_tags=[],
            inline_tags=[],
            links=[],
            created_at=None,
            modified_at=datetime.now(),
            metadata={},
        )
        record = builder.build_record(chunk, sample_embedding, "vault")
        assert record["chunk_index"] == 5

    def test_invalid_chunk_index(self, builder, sample_embedding):
        """Неверный формат chunk_index возвращает 0."""
        chunk = DocumentChunk(
            id="invalid_id_format",
            vault_name="vault",
            file_path="file.md",
            title="Title",
            section="Section",
            content="Content",
            tags=[],
            frontmatter_tags=[],
            inline_tags=[],
            links=[],
            created_at=None,
            modified_at=datetime.now(),
            metadata={},
        )
        record = builder.build_record(chunk, sample_embedding, "vault")
        assert record["chunk_index"] == 0

    def test_empty_lists(self, builder, sample_embedding):
        """Чанк с пустыми списками."""
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
            modified_at=datetime.now(),
            metadata={},
        )
        record = builder.build_record(chunk, sample_embedding, "vault")
        assert record["links"] == []
        assert record["inline_tags"] == []

    def test_large_embedding(self, builder, sample_chunk):
        """Чанк с большим embedding (1024 dimensions)."""
        large_embedding = [0.01 * i for i in range(1024)]
        record = builder.build_record(sample_chunk, large_embedding, "test_vault")
        assert len(record["vector"]) == 1024


class TestBuildBatch:
    """Тесты для метода build_batch."""

    def test_basic_batch(self, builder, sample_chunk, sample_embedding):
        """Базовое построение батча."""
        chunks = [sample_chunk]
        embeddings = [sample_embedding]

        records = builder.build_batch(chunks, embeddings, "test_vault")

        assert len(records) == 1
        assert records[0]["chunk_id"] == sample_chunk.id

    def test_multiple_chunks(self, builder, sample_embedding):
        """Батч с несколькими чанками."""
        chunks = []
        embeddings = []
        for i in range(5):
            chunk = DocumentChunk(
                id=f"vault::file.md::{i}",
                vault_name="vault",
                file_path="file.md",
                title="Title",
                section=f"Section {i}",
                content=f"Content {i}",
                tags=[],
                frontmatter_tags=[],
                inline_tags=[],
                links=[],
                created_at=None,
                modified_at=datetime.now(),
                metadata={},
            )
            chunks.append(chunk)
            embeddings.append([0.1 * i] * 5)

        records = builder.build_batch(chunks, embeddings, "vault")

        assert len(records) == 5
        for i, record in enumerate(records):
            assert record["chunk_index"] == i
            assert record["section"] == f"Section {i}"

    def test_mismatched_lengths_raises(self, builder, sample_chunk, sample_embedding):
        """Несоответствие количества чанков и embeddings вызывает ошибку."""
        chunks = [sample_chunk, sample_chunk]
        embeddings = [sample_embedding]  # Только один embedding

        with pytest.raises(ValueError) as exc_info:
            builder.build_batch(chunks, embeddings, "test_vault")

        assert "doesn't match" in str(exc_info.value)

    def test_empty_batch(self, builder):
        """Пустой батч возвращает пустой список."""
        records = builder.build_batch([], [], "vault")
        assert records == []
