"""Unit-тесты для ChunkRepository."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from obsidian_kb.storage.chunk_repository import ChunkRepository
from obsidian_kb.types import Chunk, ChunkSearchResult, MatchType, RelevanceScore, SearchResult


@pytest.fixture
def mock_db_manager():
    """Мок LanceDBManager."""
    manager = MagicMock()
    manager.vector_search = AsyncMock(return_value=[])
    manager.fts_search = AsyncMock(return_value=[])
    manager.delete_file = AsyncMock()
    manager._ensure_table = AsyncMock(return_value=MagicMock())
    manager._get_db = MagicMock(return_value=MagicMock())
    return manager


@pytest.fixture
def chunk_repository(mock_db_manager):
    """ChunkRepository с моком db_manager."""
    return ChunkRepository(mock_db_manager)


class TestChunkRepository:
    """Тесты для ChunkRepository."""

    @pytest.mark.asyncio
    async def test_upsert_warning(self, chunk_repository, caplog):
        """Проверка предупреждения при вызове upsert."""
        chunks = [
            Chunk(
                chunk_id="test::file.md::0",
                document_id="test::file.md",
                vault_name="test",
                chunk_index=0,
                section="Introduction",
                content="Content",
                vector=[],
            )
        ]
        await chunk_repository.upsert("test", chunks)
        assert "ChunkRepository.upsert() called" in caplog.text

    @pytest.mark.asyncio
    async def test_delete_by_document(self, chunk_repository, mock_db_manager):
        """Удаление чанков документа."""
        # Мокаем get_by_document для возврата пустого списка
        chunk_repository.get_by_document = AsyncMock(return_value=[])
        mock_db_manager.delete_file = AsyncMock()
        
        result = await chunk_repository.delete_by_document("test", "test::file.md")
        
        assert result == 0
        mock_db_manager.delete_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_document(self, chunk_repository, mock_db_manager):
        """Получение чанков документа."""
        # Мокаем таблицу и результаты
        mock_table = MagicMock()

        # Данные для мока
        row_data = {
            "chunk_id": "test::file.md::0",
            "document_id": "test::file.md",
            "vault_name": "test",
            "chunk_index": 0,
            "section": "Introduction",
            "content": "Content",
        }

        # Создаём правильный мок для Arrow таблицы с to_pylist()
        mock_arrow_table = MagicMock()
        mock_arrow_table.to_pylist.return_value = [row_data]
        mock_table.search.return_value.where.return_value.to_arrow.return_value = mock_arrow_table

        mock_db_manager._ensure_table = AsyncMock(return_value=mock_table)

        chunks = await chunk_repository.get_by_document("test", "test::file.md")

        assert len(chunks) == 1
        assert chunks[0].chunk_id == "test::file.md::0"
        assert chunks[0].chunk_index == 0

    @pytest.mark.asyncio
    async def test_vector_search(self, chunk_repository, mock_db_manager):
        """Векторный поиск."""
        # Создаём мок SearchResult (без links, так как SearchResult не имеет этого поля)
        search_result = SearchResult(
            chunk_id="test::file.md::0",
            vault_name="test",
            file_path="file.md",
            title="Test File",
            section="Introduction",
            content="Test content",
            score=0.85,
            tags=["tag1"],
            created_at=datetime(2024, 1, 1),
            modified_at=datetime(2024, 1, 1),
        )
        mock_db_manager.vector_search = AsyncMock(return_value=[search_result])
        
        results = await chunk_repository.vector_search(
            vault_name="test",
            query_vector=[0.1] * 768,
            limit=10,
        )
        
        assert len(results) == 1
        assert isinstance(results[0], ChunkSearchResult)
        assert results[0].chunk.chunk_id == "test::file.md::0"
        assert results[0].score.value == 0.85
        assert results[0].score.match_type == MatchType.SEMANTIC

    @pytest.mark.asyncio
    async def test_fts_search(self, chunk_repository, mock_db_manager):
        """Полнотекстовый поиск."""
        search_result = SearchResult(
            chunk_id="test::file.md::0",
            vault_name="test",
            file_path="file.md",
            title="Test File",
            section="Introduction",
            content="Test content",
            score=0.75,
            tags=["tag1"],
            created_at=datetime(2024, 1, 1),
            modified_at=datetime(2024, 1, 1),
        )
        mock_db_manager.fts_search = AsyncMock(return_value=[search_result])
        
        results = await chunk_repository.fts_search(
            vault_name="test",
            query="test",
            limit=10,
        )
        
        assert len(results) == 1
        assert isinstance(results[0], ChunkSearchResult)
        assert results[0].score.match_type == MatchType.KEYWORD

    @pytest.mark.asyncio
    async def test_vector_search_with_filters(self, chunk_repository, mock_db_manager):
        """Векторный поиск с фильтрами."""
        mock_db_manager.vector_search = AsyncMock(return_value=[])
        
        await chunk_repository.vector_search(
            vault_name="test",
            query_vector=[0.1] * 768,
            limit=10,
            filter_document_ids={"test::file.md"},
            where="tags = 'python'",
        )
        
        mock_db_manager.vector_search.assert_called_once_with(
            vault_name="test",
            query_vector=[0.1] * 768,
            limit=10,
            where="tags = 'python'",
            document_ids={"test::file.md"},
        )

    def test_search_result_to_chunk_result(self, chunk_repository):
        """Конвертация SearchResult в ChunkSearchResult."""
        search_result = SearchResult(
            chunk_id="test::file.md::5",
            vault_name="test",
            file_path="file.md",
            title="Test File",
            section="Section 5",
            content="Content",
            score=0.8,
            tags=["tag1"],
            created_at=datetime(2024, 1, 1),
            modified_at=datetime(2024, 1, 1),
        )
        
        result = chunk_repository._search_result_to_chunk_result(search_result)
        
        assert isinstance(result, ChunkSearchResult)
        assert result.chunk.chunk_id == "test::file.md::5"
        assert result.chunk.chunk_index == 5
        assert result.chunk.document_id == "test::file.md"
        assert result.score.value == 0.8
        assert result.score.match_type == MatchType.SEMANTIC

    def test_row_to_chunk(self, chunk_repository):
        """Конвертация строки БД в Chunk."""
        row = {
            "chunk_id": "test::file.md::0",
            "document_id": "test::file.md",
            "vault_name": "test",
            "chunk_index": 0,
            "section": "Introduction",
            "content": "Content",
            "vector": [0.1] * 768,
            "inline_tags": ["tag1"],
            "links": ["Link1"],
        }
        
        chunk = chunk_repository._row_to_chunk(row)
        
        assert isinstance(chunk, Chunk)
        assert chunk.chunk_id == "test::file.md::0"
        assert chunk.document_id == "test::file.md"
        assert chunk.vault_name == "test"
        assert chunk.chunk_index == 0
        assert chunk.section == "Introduction"
        assert chunk.content == "Content"
        assert len(chunk.vector) == 768
        assert chunk.inline_tags == ["tag1"]
        assert chunk.links == ["Link1"]

