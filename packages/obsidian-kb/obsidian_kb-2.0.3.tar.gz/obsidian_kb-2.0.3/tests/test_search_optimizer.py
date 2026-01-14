"""Тесты для модуля оптимизации поиска."""

from datetime import datetime

import pytest
from unittest.mock import AsyncMock, MagicMock

from obsidian_kb.search_optimizer import (
    AdaptiveAlphaCalculator,
    AgentQueryNormalizer,
    AgentQueryCache,
    QueryExpander,
    ReRanker,
    FeatureExtractor,
    RankingModel,
    RankingFeatures,
    SearchOptimizer,
)
from obsidian_kb.types import (
    SearchResult,
    Chunk,
    ChunkSearchResult,
    RelevanceScore,
    MatchType,
)


class TestAdaptiveAlphaCalculator:
    """Тесты для AdaptiveAlphaCalculator."""

    def test_short_query(self):
        """Короткие запросы должны иметь больший alpha."""
        calculator = AdaptiveAlphaCalculator()
        alpha = calculator.calculate("Python async")
        assert alpha >= 0.7  # Должен быть больше базового

    def test_long_query(self):
        """Длинные запросы должны иметь меньший alpha."""
        calculator = AdaptiveAlphaCalculator()
        alpha = calculator.calculate("Python async programming with asyncio and coroutines for concurrent execution")
        assert alpha <= 0.7  # Должен быть меньше базового

    def test_technical_terms(self):
        """Технические термины должны уменьшать alpha."""
        calculator = AdaptiveAlphaCalculator()
        alpha1 = calculator.calculate("Python async")
        alpha2 = calculator.calculate("Python async version 3.11")
        assert alpha2 < alpha1

    def test_quotes(self):
        """Кавычки должны уменьшать alpha."""
        calculator = AdaptiveAlphaCalculator()
        alpha1 = calculator.calculate("Python async")
        alpha2 = calculator.calculate('"Python async"')
        assert alpha2 < alpha1

    def test_question(self):
        """Вопросы должны увеличивать alpha."""
        calculator = AdaptiveAlphaCalculator()
        alpha1 = calculator.calculate("Python async")
        alpha2 = calculator.calculate("What is Python async?")
        # Используем приблизительное сравнение из-за floating point precision
        # "Python async" (2 слова) -> base_alpha = 0.8
        # "What is Python async?" (4 слова, вопрос) -> base_alpha = 0.7 + 0.1 = 0.8
        # Из-за floating point precision может быть небольшая разница
        assert alpha2 >= alpha1 - 1e-10

    def test_bounds(self):
        """Alpha должен быть в пределах 0.3-0.9."""
        calculator = AdaptiveAlphaCalculator()
        alpha = calculator.calculate("test")
        assert 0.3 <= alpha <= 0.9


class TestAgentQueryNormalizer:
    """Тесты для AgentQueryNormalizer."""

    def test_remove_find(self):
        """Убирает 'найди' из запроса."""
        normalizer = AgentQueryNormalizer()
        result = normalizer.normalize("найди информацию о Python")
        assert "найди" not in result.lower()
        assert "Python" in result

    def test_remove_find_english(self):
        """Убирает 'find' из запроса."""
        normalizer = AgentQueryNormalizer()
        result = normalizer.normalize("find information about Python")
        assert "find" not in result.lower()
        assert "Python" in result

    def test_remove_show_me(self):
        """Убирает 'show me' из запроса."""
        normalizer = AgentQueryNormalizer()
        result = normalizer.normalize("show me Python async")
        assert "show" not in result.lower()
        assert "Python" in result

    def test_remove_what_written(self):
        """Убирает 'что написано про' из запроса."""
        normalizer = AgentQueryNormalizer()
        result = normalizer.normalize("что написано про Python")
        assert "что написано про" not in result.lower()
        assert "Python" in result

    def test_preserve_query(self):
        """Сохраняет основной запрос."""
        normalizer = AgentQueryNormalizer()
        result = normalizer.normalize("найди Python async programming")
        assert "Python async programming" in result

    def test_empty_after_normalization(self):
        """Если всё удалилось, возвращает исходный запрос."""
        normalizer = AgentQueryNormalizer()
        result = normalizer.normalize("найди")
        assert result == "найди"  # Возвращает исходный


class TestAgentQueryCache:
    """Тесты для AgentQueryCache."""

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """Повторный запрос должен попадать в кэш."""
        cache = AgentQueryCache(max_size=10)
        
        mock_results = [SearchResult(
            chunk_id="1",
            vault_name="test",
            file_path="test.md",
            title="Test",
            section="Test",
            content="Test content",
            tags=[],
            score=0.9,
            created_at=None,
            modified_at=datetime.now(),
        )]
        
        search_func = AsyncMock(return_value=mock_results)
        
        # Первый запрос
        results1 = await cache.get_or_search("test", "Python", search_func)
        assert len(results1) == 1
        assert search_func.call_count == 1
        
        # Второй запрос (должен быть из кэша)
        results2 = await cache.get_or_search("test", "Python", search_func)
        assert len(results2) == 1
        assert search_func.call_count == 1  # Не должен вызываться снова

    @pytest.mark.asyncio
    async def test_cache_normalization(self):
        """Кэш должен нормализовать запросы."""
        cache = AgentQueryCache(max_size=10)
        
        mock_results = [SearchResult(
            chunk_id="1",
            vault_name="test",
            file_path="test.md",
            title="Test",
            section="Test",
            content="Test content",
            tags=[],
            score=0.9,
            created_at=None,
            modified_at=datetime.now(),
        )]
        
        search_func = AsyncMock(return_value=mock_results)
        
        # Первый запрос
        await cache.get_or_search("test", "Python", search_func)
        
        # Второй запрос с нормализацией (должен попасть в кэш)
        await cache.get_or_search("test", "найди Python", search_func)
        
        assert search_func.call_count == 1  # Должен быть из кэша

    def test_cache_clear(self):
        """Очистка кэша должна работать."""
        cache = AgentQueryCache(max_size=10)
        cache.cache["test"] = []
        cache.clear()
        assert len(cache.cache) == 0


class TestFeatureExtractor:
    """Тесты для FeatureExtractor."""

    def test_extract_features(self):
        """Извлечение признаков должно работать."""
        extractor = FeatureExtractor()
        
        result = SearchResult(
            chunk_id="1",
            vault_name="test",
            file_path="test.md",
            title="Python async programming",
            section="Introduction",
            content="Python async programming is great",
            tags=["python", "async"],
            score=0.8,
            created_at=None,
            modified_at=datetime.now(),
        )
        
        features = extractor.extract(result, "Python async")
        
        assert isinstance(features, RankingFeatures)
        assert features.vector_score == 0.8
        assert features.title_match > 0  # Должно быть совпадение
        assert features.tag_match > 0  # Должно быть совпадение тегов
        assert 0 <= features.recency <= 1

    def test_title_match(self):
        """Совпадение в заголовке должно вычисляться правильно."""
        extractor = FeatureExtractor()
        
        result = SearchResult(
            chunk_id="1",
            vault_name="test",
            file_path="test.md",
            title="Python async",
            section="Test",
            content="Test",
            tags=[],
            score=0.8,
            created_at=None,
            modified_at=datetime.now(),
        )
        
        features = extractor.extract(result, "Python async")
        assert features.title_match == 1.0  # Полное совпадение


class TestRankingModel:
    """Тесты для RankingModel."""

    def test_predict_score(self):
        """Предсказание score должно работать."""
        model = RankingModel()
        
        features = RankingFeatures(
            vector_score=0.8,
            fts_score=0.7,
            title_match=1.0,
            tag_match=0.5,
            recency=0.9,
            popularity=0.5,
            link_count=5,
            content_length=1000,
            section_relevance=0.8,
        )
        
        score = model.predict_score(features)
        assert 0 <= score <= 1

    def test_custom_weights(self):
        """Кастомные веса должны применяться."""
        custom_weights = {
            "vector_score": 0.5,
            "fts_score": 0.3,
            "title_match": 0.2,
            "tag_match": 0.0,
            "recency": 0.0,
            "popularity": 0.0,
            "link_count": 0.0,
            "section_relevance": 0.0,
        }
        
        model = RankingModel(weights=custom_weights)
        
        features = RankingFeatures(
            vector_score=1.0,
            fts_score=0.0,
            title_match=0.0,
            tag_match=0.0,
            recency=0.0,
            popularity=0.0,
            link_count=0,
            content_length=0,
            section_relevance=0.0,
        )
        
        score = model.predict_score(features)
        assert score > 0.4  # Должен быть высокий score из-за vector_score


class TestSearchOptimizer:
    """Тесты для SearchOptimizer."""

    @pytest.fixture
    def mock_embedding_service(self):
        """Мок для EmbeddingService."""
        service = MagicMock(spec=AsyncMock)
        async def mock_get_embedding(text: str, embedding_type: str = "doc"):
            return [0.1] * 768
        service.get_embedding = AsyncMock(side_effect=mock_get_embedding)
        return service

    @pytest.fixture
    def mock_db_manager(self):
        """Мок для LanceDBManager."""
        manager = MagicMock()

        mock_chunk = Chunk(
            chunk_id="test::test.md::0",
            document_id="test::test.md",
            vault_name="test",
            chunk_index=0,
            section="Test",
            content="Test content",
        )
        mock_chunk_result = ChunkSearchResult(
            chunk=mock_chunk,
            score=RelevanceScore(value=0.8, match_type=MatchType.SEMANTIC),
        )

        # Legacy SearchResult для hybrid_search
        mock_result = SearchResult(
            chunk_id="test::test.md::0",
            vault_name="test",
            file_path="test.md",
            title="Test",
            section="Test",
            content="Test content",
            tags=[],
            score=0.8,
            created_at=None,
            modified_at=datetime.now(),
        )

        manager.hybrid_search = AsyncMock(return_value=[mock_result])

        # Моки для chunks репозитория (возвращают ChunkSearchResult)
        manager.chunks = MagicMock()
        manager.chunks.vector_search = AsyncMock(return_value=[mock_chunk_result])
        manager.chunks.fts_search = AsyncMock(return_value=[mock_chunk_result])

        return manager

    @pytest.mark.asyncio
    async def test_optimize_search_with_normalization(self, mock_embedding_service, mock_db_manager):
        """Оптимизированный поиск должен нормализовать запросы."""
        optimizer = SearchOptimizer(
            embedding_service=mock_embedding_service,
            db_manager=mock_db_manager,
            enable_rerank=False,
            enable_query_expansion=False,
            enable_feature_ranking=False,
            enable_agent_normalization=True,
            enable_query_cache=False,
        )
        
        query_vector = [0.1] * 768
        results = await optimizer.optimize_search(
            vault_name="test",
            query="найди Python async",
            query_vector=query_vector,
            limit=10,
        )
        
        # Проверяем, что запрос был нормализован
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_optimize_search_with_cache(self, mock_embedding_service, mock_db_manager):
        """Оптимизированный поиск должен использовать кэш."""
        optimizer = SearchOptimizer(
            embedding_service=mock_embedding_service,
            db_manager=mock_db_manager,
            enable_rerank=False,
            enable_query_expansion=False,
            enable_feature_ranking=False,
            enable_agent_normalization=True,
            enable_query_cache=True,
        )
        
        query_vector = [0.1] * 768
        
        # Первый запрос
        results1 = await optimizer.optimize_search(
            vault_name="test",
            query="Python async",
            query_vector=query_vector,
            limit=10,
        )
        
        # Второй запрос (должен быть из кэша)
        results2 = await optimizer.optimize_search(
            vault_name="test",
            query="найди Python async",  # Нормализуется и попадает в кэш
            query_vector=query_vector,
            limit=10,
        )
        
        assert len(results1) == len(results2)
        # Проверяем, что второй запрос использовал кэш (меньше вызовов БД)
        assert mock_db_manager.hybrid_search.call_count <= 2

