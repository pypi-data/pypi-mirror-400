"""Unit-тесты для стратегий поиска."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from obsidian_kb.search.strategies.chunk_level import ChunkLevelStrategy
from obsidian_kb.search.strategies.document_level import DocumentLevelStrategy
from obsidian_kb.types import (
    Chunk,
    ChunkSearchResult,
    Document,
    DocumentSearchResult,
    MatchType,
    RelevanceScore,
)


@pytest.fixture
def mock_chunk_repo():
    """Мок IChunkRepository."""
    repo = MagicMock()
    repo.vector_search = AsyncMock(return_value=[])
    repo.fts_search = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_document_repo():
    """Мок IDocumentRepository."""
    repo = MagicMock()
    repo.get_many = AsyncMock(return_value=[])
    repo.get = AsyncMock(return_value=None)  # Добавляем метод get для _build_results
    repo.find_by_property = AsyncMock(return_value=set())
    repo.find_by_tags = AsyncMock(return_value=set())
    repo.find_by_date_range = AsyncMock(return_value=set())
    repo.get_content = AsyncMock(return_value="")
    repo.get_properties = AsyncMock(return_value={})
    return repo


@pytest.fixture
def mock_embedding_service():
    """Мок IEmbeddingService."""
    service = MagicMock()
    # Используем AsyncMock с return_value - он автоматически поддерживает любые параметры
    service.get_embedding = AsyncMock(return_value=[0.1] * 768)
    service.get_embeddings_batch = AsyncMock(return_value=[[0.1] * 768])
    return service


class TestDocumentLevelStrategy:
    """Тесты для DocumentLevelStrategy."""

    @pytest.mark.asyncio
    async def test_search_with_filters(self, mock_document_repo):
        """Поиск с фильтрами."""
        strategy = DocumentLevelStrategy(mock_document_repo)
        
        # Мокаем фильтры
        doc1 = Document(
            document_id="test::file1.md",
            vault_name="test",
            file_path="file1.md",
            title="File 1",
            content="Content 1",
            tags=["python"],
        )
        doc2 = Document(
            document_id="test::file2.md",
            vault_name="test",
            file_path="file2.md",
            title="File 2",
            content="Content 2",
            tags=["python"],
        )
        
        mock_document_repo.find_by_tags = AsyncMock(return_value={"test::file1.md", "test::file2.md"})
        mock_document_repo.get_many = AsyncMock(return_value=[doc1, doc2])
        
        results = await strategy.search(
            vault_name="test",
            query="",
            parsed_filters={"tags": ["python"]},
            limit=10,
        )
        
        assert len(results) == 2
        assert all(isinstance(r, DocumentSearchResult) for r in results)
        assert all(r.score.match_type == MatchType.EXACT_METADATA for r in results)

    @pytest.mark.asyncio
    async def test_search_with_content(self, mock_document_repo):
        """Поиск с включением контента."""
        strategy = DocumentLevelStrategy(mock_document_repo)

        doc = Document(
            document_id="test::file.md",
            vault_name="test",
            file_path="file.md",
            title="File",
            content="",
            tags=["python"],
        )

        # Настраиваем моки для возврата document_ids через фильтры
        mock_document_repo.find_by_tags = AsyncMock(return_value={"test::file.md"})
        mock_document_repo.get_many = AsyncMock(return_value=[doc])
        mock_document_repo.get = AsyncMock(return_value=doc)
        mock_document_repo.get_content = AsyncMock(return_value="Full content here")
        mock_document_repo.get_properties = AsyncMock(return_value={"tags": "python"})

        results = await strategy.search(
            vault_name="test",
            query="",
            parsed_filters={"tags": ["python"]},
            limit=10,
            options={"include_content": True},
        )

        assert len(results) == 1
        assert results[0].document.content == "Full content here"

    @pytest.mark.asyncio
    async def test_search_empty_results(self, mock_document_repo):
        """Поиск без результатов."""
        strategy = DocumentLevelStrategy(mock_document_repo)
        mock_document_repo.get_many = AsyncMock(return_value=[])
        
        results = await strategy.search(
            vault_name="test",
            query="",
            parsed_filters={},
            limit=10,
        )
        
        assert len(results) == 0


class TestChunkLevelStrategy:
    """Тесты для ChunkLevelStrategy."""

    @pytest.mark.asyncio
    async def test_vector_search(self, mock_chunk_repo, mock_document_repo, mock_embedding_service):
        """Векторный поиск."""
        strategy = ChunkLevelStrategy(mock_document_repo, mock_chunk_repo, mock_embedding_service)
        
        chunk = Chunk(
            chunk_id="test::file.md::0",
            document_id="test::file.md",
            vault_name="test",
            chunk_index=0,
            section="Introduction",
            content="Content",
            vector=[],
        )
        chunk_result = ChunkSearchResult(
            chunk=chunk,
            score=RelevanceScore(value=0.8, match_type=MatchType.SEMANTIC),
        )
        
        doc = Document(
            document_id="test::file.md",
            vault_name="test",
            file_path="file.md",
            title="File",
            content="Content",
            tags=[],
        )
        
        mock_chunk_repo.vector_search = AsyncMock(return_value=[chunk_result])
        mock_document_repo.get_many = AsyncMock(return_value=[doc])
        # Настраиваем моки для _build_results
        mock_document_repo.get = AsyncMock(return_value=doc)
        mock_document_repo.get_properties = AsyncMock(return_value={})
        
        results = await strategy.search(
            vault_name="test",
            query="test",
            parsed_filters={},
            limit=10,
            options={"search_type": "vector"},
        )
        
        assert len(results) == 1
        assert isinstance(results[0], DocumentSearchResult)
        assert results[0].document.document_id == "test::file.md"

    @pytest.mark.asyncio
    async def test_fts_search(self, mock_chunk_repo, mock_document_repo, mock_embedding_service):
        """Полнотекстовый поиск."""
        strategy = ChunkLevelStrategy(mock_document_repo, mock_chunk_repo, mock_embedding_service)
        
        chunk = Chunk(
            chunk_id="test::file.md::0",
            document_id="test::file.md",
            vault_name="test",
            chunk_index=0,
            section="Introduction",
            content="Content",
            vector=[],
        )
        chunk_result = ChunkSearchResult(
            chunk=chunk,
            score=RelevanceScore(value=0.7, match_type=MatchType.KEYWORD),
        )
        
        doc = Document(
            document_id="test::file.md",
            vault_name="test",
            file_path="file.md",
            title="File",
            content="Content",
            tags=[],
        )
        
        mock_chunk_repo.fts_search = AsyncMock(return_value=[chunk_result])
        mock_document_repo.get_many = AsyncMock(return_value=[doc])
        mock_document_repo.get = AsyncMock(return_value=doc)
        mock_document_repo.get_properties = AsyncMock(return_value={})
        
        results = await strategy.search(
            vault_name="test",
            query="test",
            parsed_filters={},
            limit=10,
            options={"search_type": "fts"},
        )
        
        assert len(results) == 1
        assert results[0].score.match_type == MatchType.KEYWORD

    @pytest.mark.asyncio
    async def test_hybrid_search(self, mock_chunk_repo, mock_document_repo, mock_embedding_service):
        """Гибридный поиск."""
        strategy = ChunkLevelStrategy(mock_document_repo, mock_chunk_repo, mock_embedding_service)
        
        chunk1 = Chunk(
            chunk_id="test::file1.md::0",
            document_id="test::file1.md",
            vault_name="test",
            chunk_index=0,
            section="Introduction",
            content="Content 1",
            vector=[],
        )
        chunk_result1 = ChunkSearchResult(
            chunk=chunk1,
            score=RelevanceScore(value=0.8, match_type=MatchType.SEMANTIC),
        )
        
        chunk2 = Chunk(
            chunk_id="test::file2.md::0",
            document_id="test::file2.md",
            vault_name="test",
            chunk_index=0,
            section="Introduction",
            content="Content 2",
            vector=[],
        )
        chunk_result2 = ChunkSearchResult(
            chunk=chunk2,
            score=RelevanceScore(value=0.6, match_type=MatchType.KEYWORD),
        )
        
        doc1 = Document(
            document_id="test::file1.md",
            vault_name="test",
            file_path="file1.md",
            title="File 1",
            content="Content 1",
            tags=[],
        )
        doc2 = Document(
            document_id="test::file2.md",
            vault_name="test",
            file_path="file2.md",
            title="File 2",
            content="Content 2",
            tags=[],
        )
        
        mock_chunk_repo.vector_search = AsyncMock(return_value=[chunk_result1])
        mock_chunk_repo.fts_search = AsyncMock(return_value=[chunk_result2])
        mock_document_repo.get_many = AsyncMock(return_value=[doc1, doc2])
        # Настраиваем моки для _build_results - возвращаем документ по ID
        def mock_get(vault_name: str, doc_id: str):
            if doc_id == "test::file1.md":
                return doc1
            elif doc_id == "test::file2.md":
                return doc2
            return None
        mock_document_repo.get = AsyncMock(side_effect=mock_get)
        mock_document_repo.get_properties = AsyncMock(return_value={})
        
        results = await strategy.search(
            vault_name="test",
            query="test",
            parsed_filters={},
            limit=10,
            options={"search_type": "hybrid"},
        )
        
        assert len(results) >= 1
        # Проверяем, что результаты объединены
        assert any(r.document.document_id == "test::file1.md" for r in results)

    @pytest.mark.asyncio
    async def test_score_aggregation_max(self, mock_chunk_repo, mock_document_repo, mock_embedding_service):
        """Агрегация scores методом max."""
        strategy = ChunkLevelStrategy(mock_document_repo, mock_chunk_repo, mock_embedding_service, aggregation="max")
        
        chunk1 = Chunk(
            chunk_id="test::file.md::0",
            document_id="test::file.md",
            vault_name="test",
            chunk_index=0,
            section="Section 1",
            content="Content 1",
            vector=[],
        )
        chunk_result1 = ChunkSearchResult(
            chunk=chunk1,
            score=RelevanceScore(value=0.9, match_type=MatchType.SEMANTIC),
        )
        
        chunk2 = Chunk(
            chunk_id="test::file.md::1",
            document_id="test::file.md",
            vault_name="test",
            chunk_index=1,
            section="Section 2",
            content="Content 2",
            vector=[],
        )
        chunk_result2 = ChunkSearchResult(
            chunk=chunk2,
            score=RelevanceScore(value=0.7, match_type=MatchType.SEMANTIC),
        )
        
        doc = Document(
            document_id="test::file.md",
            vault_name="test",
            file_path="file.md",
            title="File",
            content="Content",
            tags=[],
        )
        
        mock_chunk_repo.vector_search = AsyncMock(return_value=[chunk_result1, chunk_result2])
        mock_document_repo.get_many = AsyncMock(return_value=[doc])
        mock_document_repo.get = AsyncMock(return_value=doc)
        mock_document_repo.get_properties = AsyncMock(return_value={})
        
        results = await strategy.search(
            vault_name="test",
            query="test",
            parsed_filters={},
            limit=10,
            options={"search_type": "vector"},
        )
        
        assert len(results) == 1
        # Score должен быть максимальным (0.9)
        assert results[0].score.value == 0.9

