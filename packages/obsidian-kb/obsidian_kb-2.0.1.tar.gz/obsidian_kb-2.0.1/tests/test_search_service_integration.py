"""Integration-тесты для SearchService (v5)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from obsidian_kb.search.service import SearchService
from obsidian_kb.types import (
    Chunk,
    ChunkSearchResult,
    Document,
    DocumentSearchResult,
    MatchType,
    RelevanceScore,
    RetrievalGranularity,
    SearchIntent,
    SearchRequest,
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
    repo.find_by_tags = AsyncMock(return_value=set())
    repo.find_by_property = AsyncMock(return_value=set())
    repo.find_by_date_range = AsyncMock(return_value=set())
    repo.get = AsyncMock(return_value=None)
    repo.get_properties = AsyncMock(return_value={})
    return repo


@pytest.fixture
def mock_embedding_service():
    """Мок IEmbeddingService."""
    service = MagicMock()
    async def mock_get_embedding(text: str, embedding_type: str = "doc"):
        return [0.1] * 768
    service.get_embedding = AsyncMock(side_effect=mock_get_embedding)
    return service


@pytest.fixture
def mock_intent_detector():
    """Мок IIntentDetector."""
    from obsidian_kb.types import IntentDetectionResult
    
    detector = MagicMock()
    detector.detect = MagicMock(
        return_value=IntentDetectionResult(
            intent=SearchIntent.SEMANTIC,
            confidence=0.9,
            signals={"has_text": True},
            recommended_granularity=RetrievalGranularity.CHUNK,
        )
    )
    return detector


@pytest.fixture
def search_service(mock_chunk_repo, mock_document_repo, mock_embedding_service, mock_intent_detector):
    """SearchService с моками."""
    return SearchService(
        chunk_repo=mock_chunk_repo,
        document_repo=mock_document_repo,
        embedding_service=mock_embedding_service,
        intent_detector=mock_intent_detector,
    )


class TestSearchServiceIntegration:
    """Integration-тесты для SearchService."""

    @pytest.mark.asyncio
    async def test_search_semantic_intent(self, search_service, mock_chunk_repo, mock_document_repo):
        """Поиск с SEMANTIC intent."""
        # Настраиваем моки
        chunk = Chunk(
            chunk_id="test::file.md::0",
            document_id="test::file.md",
            vault_name="test",
            chunk_index=0,
            section="Introduction",
            content="Python programming content",
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
            title="Python Guide",
            content="Content",
            tags=["python"],
        )
        
        mock_chunk_repo.vector_search = AsyncMock(return_value=[chunk_result])
        mock_document_repo.get_many = AsyncMock(return_value=[doc])
        mock_document_repo.get = AsyncMock(return_value=doc)
        mock_document_repo.get_properties = AsyncMock(return_value={"tags": "python"})

        request = SearchRequest(
            vault_name="test",
            query="python programming",
            limit=10,
        )
        
        response = await search_service.search(request)
        
        assert response.detected_intent == SearchIntent.SEMANTIC
        assert len(response.results) == 1
        assert response.results[0].document.title == "Python Guide"
        assert response.strategy_used == "chunk_level"

    @pytest.mark.asyncio
    async def test_search_metadata_filter_intent(self, search_service, mock_document_repo, mock_intent_detector):
        """Поиск с METADATA_FILTER intent."""
        from obsidian_kb.types import IntentDetectionResult
        
        # Настраиваем intent detector для METADATA_FILTER
        mock_intent_detector.detect = MagicMock(
            return_value=IntentDetectionResult(
                intent=SearchIntent.METADATA_FILTER,
                confidence=0.95,
                signals={"has_filters": True},
                recommended_granularity=RetrievalGranularity.DOCUMENT,
            )
        )
        
        doc = Document(
            document_id="test::file.md",
            vault_name="test",
            file_path="file.md",
            title="Python Guide",
            content="Content",
            tags=["python"],
        )
        
        mock_document_repo.find_by_tags = AsyncMock(return_value={"test::file.md"})
        mock_document_repo.get_many = AsyncMock(return_value=[doc])
        mock_document_repo.get = AsyncMock(return_value=doc)
        mock_document_repo.get_properties = AsyncMock(return_value={"tags": "python"})
        mock_document_repo.get_content = AsyncMock(return_value="Content")

        request = SearchRequest(
            vault_name="test",
            query="tags:python",
            limit=10,
        )
        
        response = await search_service.search(request)
        
        assert response.detected_intent == SearchIntent.METADATA_FILTER
        assert response.strategy_used == "document_level"
        assert len(response.results) == 1

    @pytest.mark.asyncio
    async def test_search_auto_granularity(self, search_service, mock_chunk_repo, mock_document_repo, mock_intent_detector):
        """Автоматический выбор granularity."""
        from obsidian_kb.types import IntentDetectionResult
        
        # Настраиваем intent detector для рекомендации CHUNK
        mock_intent_detector.detect = MagicMock(
            return_value=IntentDetectionResult(
                intent=SearchIntent.SEMANTIC,
                confidence=0.9,
                signals={"has_text": True},
                recommended_granularity=RetrievalGranularity.CHUNK,
            )
        )
        
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
        
        request = SearchRequest(
            vault_name="test",
            query="test",
            granularity=RetrievalGranularity.AUTO,
        )
        
        response = await search_service.search(request)
        
        assert response.strategy_used == "chunk_level"

    @pytest.mark.asyncio
    async def test_search_force_intent(self, search_service, mock_document_repo):
        """Принудительное указание intent."""
        doc = Document(
            document_id="test::file.md",
            vault_name="test",
            file_path="file.md",
            title="File",
            content="Content",
            tags=[],
        )
        
        mock_document_repo.get_many = AsyncMock(return_value=[doc])
        
        request = SearchRequest(
            vault_name="test",
            query="test",
            force_intent=SearchIntent.METADATA_FILTER,
        )
        
        response = await search_service.search(request)
        
        assert response.detected_intent == SearchIntent.METADATA_FILTER
        assert response.intent_confidence == 1.0

    @pytest.mark.asyncio
    async def test_search_multi_vault(self, search_service, mock_chunk_repo, mock_document_repo):
        """Поиск по нескольким vault'ам."""
        doc1 = Document(
            document_id="vault1::file1.md",
            vault_name="vault1",
            file_path="file1.md",
            title="File 1",
            content="Content 1",
            tags=[],
        )
        doc2 = Document(
            document_id="vault2::file2.md",
            vault_name="vault2",
            file_path="file2.md",
            title="File 2",
            content="Content 2",
            tags=[],
        )

        # Создаём чанки для результатов поиска
        chunk1 = Chunk(
            chunk_id="vault1::file1.md::0",
            document_id="vault1::file1.md",
            vault_name="vault1",
            chunk_index=0,
            section="Introduction",
            content="Content 1",
            vector=[],
        )
        chunk_result1 = ChunkSearchResult(
            chunk=chunk1,
            score=RelevanceScore(value=0.8, match_type=MatchType.SEMANTIC),
        )

        # Мокаем vector_search для возврата результатов
        mock_chunk_repo.vector_search = AsyncMock(return_value=[chunk_result1])

        # Мокаем поиск для каждого vault
        async def get_side_effect(vault_name, document_id):
            if "vault1" in document_id:
                return doc1
            return doc2

        mock_document_repo.get = AsyncMock(side_effect=get_side_effect)
        mock_document_repo.get_properties = AsyncMock(return_value={})
        mock_document_repo.get_many = AsyncMock(return_value=[doc1])

        request = SearchRequest(
            vault_name="",
            query="test",
            limit=10,
        )

        response = await search_service.search_multi_vault(["vault1", "vault2"], request)

        assert len(response.results) >= 1
        assert response.strategy_used == "multi_vault"

    @pytest.mark.asyncio
    async def test_search_execution_time(self, search_service, mock_chunk_repo, mock_document_repo):
        """Проверка измерения времени выполнения."""
        import asyncio
        
        # Добавляем задержку для проверки времени
        async def delayed_vector_search(*args, **kwargs):
            await asyncio.sleep(0.01)  # 10ms задержка
            return []
        
        mock_chunk_repo.vector_search = delayed_vector_search
        
        request = SearchRequest(
            vault_name="test",
            query="test",
        )
        
        response = await search_service.search(request)
        
        assert response.execution_time_ms > 0
        assert response.execution_time_ms >= 10  # Должно быть >= 10ms

    @pytest.mark.asyncio
    async def test_search_filters_applied(self, search_service, mock_document_repo, mock_intent_detector):
        """Проверка применения фильтров."""
        from obsidian_kb.types import IntentDetectionResult
        
        mock_intent_detector.detect = MagicMock(
            return_value=IntentDetectionResult(
                intent=SearchIntent.METADATA_FILTER,
                confidence=0.95,
                signals={"has_filters": True},
                recommended_granularity=RetrievalGranularity.DOCUMENT,
            )
        )
        
        mock_document_repo.get_many = AsyncMock(return_value=[])
        
        request = SearchRequest(
            vault_name="test",
            query="tags:python type:guide",
        )
        
        response = await search_service.search(request)
        
        assert response.filters_applied is not None
        # Фильтры должны быть извлечены из запроса

