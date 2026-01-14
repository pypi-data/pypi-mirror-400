"""Сервис поиска - оркестрация процесса поиска."""

import logging
import time
from typing import TYPE_CHECKING, Any, Optional

from obsidian_kb.config import settings

logger = logging.getLogger(__name__)
from obsidian_kb.query_parser import QueryParser
from obsidian_kb.search.intent_detector import IntentDetector
from obsidian_kb.search.strategies.chunk_level import ChunkLevelStrategy
from obsidian_kb.search.strategies.document_level import DocumentLevelStrategy
from obsidian_kb.types import (
    IntentDetectionResult,
    RetrievalGranularity,
    SearchIntent,
    SearchRequest,
    SearchResponse,
)

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IChunkRepository, IDocumentRepository, IEmbeddingService, IIntentDetector, ISearchStrategy


class SearchService:
    """Реализация ISearchService для оркестрации поиска."""

    def __init__(
        self,
        chunk_repo: "IChunkRepository",
        document_repo: "IDocumentRepository",
        embedding_service: "IEmbeddingService",
        intent_detector: Optional["IIntentDetector"] = None,
    ) -> None:
        """Инициализация сервиса поиска.
        
        Args:
            chunk_repo: Репозиторий чанков
            document_repo: Репозиторий документов
            embedding_service: Сервис для генерации embeddings
            intent_detector: Детектор intent (если None, создаётся новый)
        """
        self._chunks = chunk_repo
        self._documents = document_repo
        self._embeddings = embedding_service
        self._intent_detector = intent_detector or IntentDetector()
        
        # Инициализация стратегий
        aggregation_method = settings.chunk_aggregation_method
        self._strategies: dict[str, "ISearchStrategy"] = {
            "document_level": DocumentLevelStrategy(document_repo, chunk_repo),
            "chunk_level": ChunkLevelStrategy(
                document_repo, chunk_repo, embedding_service, aggregation=aggregation_method
            ),
        }

    async def search(
        self,
        request: SearchRequest,
    ) -> SearchResponse:
        """Выполнение поиска.
        
        Args:
            request: Структурированный запрос
            
        Returns:
            Структурированный ответ с результатами
        """
        start_time = time.time()
        
        # 1. Парсинг запроса (выполняем один раз)
        parsed = QueryParser.parse(request.query)
        parsed_filters = self._extract_filters(parsed)
        text_query = parsed.text_query or ""
        
        # 2. Определение intent на ИСХОДНОМ запросе ДО нормализации
        # Критично: QueryParser.parse() вызывает QueryNormalizer.normalize(), который удаляет
        # стоп-слова ("что", "зачем"), что ломает определение intent для EXPLORATORY запросов
        # См. ROUND_3_ISSUES_ANALYSIS.md для деталей
        if request.force_intent:
            intent_result = IntentDetectionResult(
                intent=request.force_intent,
                confidence=1.0,
                signals={"forced": True},
                recommended_granularity=self._intent_to_granularity(request.force_intent),
            )
        else:
            # Проверяем intent на исходном запросе ДО нормализации
            # Передаем text_query для правильного определения METADATA_FILTER
            intent_result = self._intent_detector.detect(request.query, parsed_filters, text_query=text_query)
            # Логируем для отладки (только если включен DEBUG уровень)
            logger.debug(
                f"Intent detected: {intent_result.intent.value} "
                f"(confidence: {intent_result.confidence:.2f}, "
                f"signals: {intent_result.signals})"
            )
        
        # 3. Выбор стратегии
        granularity = request.granularity
        if granularity == RetrievalGranularity.AUTO:
            granularity = intent_result.recommended_granularity
        
        # Если текстовый запрос пустой или очень короткий, но есть фильтры, используем document-level стратегию
        # ChunkLevelStrategy требует непустой текстовый запрос для семантического поиска
        # Короткие запросы (меньше 3 символов) или запросы только с одним словом лучше обрабатывать через document-level с фильтрами
        text_query_trimmed = text_query.strip() if text_query else ""
        has_meaningful_text = text_query_trimmed and len(text_query_trimmed) >= 3
        
        # Если текстовый запрос состоит только из одного слова и есть фильтры, используем document-level
        # Это особенно важно для запросов типа "type:person Муратов", где после парсинга остается только имя
        # Одно слово лучше обрабатывать через фильтры, а не через семантический поиск
        is_single_word = text_query_trimmed and len(text_query_trimmed.split()) == 1
        
        if parsed_filters and (not has_meaningful_text or is_single_word):
            logger.debug(
                f"Query with filters detected (text: '{text_query_trimmed}', single_word: {is_single_word}), "
                f"using document-level strategy"
            )
            granularity = RetrievalGranularity.DOCUMENT
        
        strategy = self._select_strategy(granularity)
        
        # 4. Выполнение поиска
        results = await strategy.search(
            vault_name=request.vault_name,
            query=text_query,
            parsed_filters=parsed_filters,
            limit=request.limit,
            options={
                "include_content": request.include_content,
                "max_content_length": request.max_content_length,
                "search_type": request.search_type,
            },
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            request=request,
            detected_intent=intent_result.intent,
            intent_confidence=intent_result.confidence,
            results=results,
            total_found=len(results),
            execution_time_ms=elapsed_ms,
            has_more=len(results) >= request.limit,
            strategy_used=strategy.name,
            filters_applied=parsed_filters,
        )

    async def search_multi_vault(
        self,
        vault_names: list[str],
        request: SearchRequest,
    ) -> SearchResponse:
        """Поиск по нескольким vault'ам."""
        start_time = time.time()
        all_results = []
        
        for vault_name in vault_names:
            vault_request = SearchRequest(
                vault_name=vault_name,
                query=request.query,
                limit=request.limit,
                search_type=request.search_type,
                granularity=request.granularity,
                include_content=request.include_content,
                max_content_length=request.max_content_length,
                force_intent=request.force_intent,
            )
            response = await self.search(vault_request)
            all_results.extend(response.results)
        
        # Сортируем и ограничиваем
        all_results.sort(key=lambda r: r.score.value, reverse=True)
        all_results = all_results[:request.limit]
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Определяем intent для ответа (используем исходный запрос, как в search())
        parsed = QueryParser.parse(request.query)
        parsed_filters = self._extract_filters(parsed)
        text_query = parsed.text_query or ""
        intent_result = self._intent_detector.detect(request.query, parsed_filters, text_query=text_query)
        
        return SearchResponse(
            request=request,
            detected_intent=intent_result.intent,
            intent_confidence=intent_result.confidence,
            results=all_results,
            total_found=len(all_results),
            execution_time_ms=elapsed_ms,
            has_more=len(all_results) >= request.limit,
            strategy_used="multi_vault",
            filters_applied=parsed_filters,
        )

    def get_available_strategies(self) -> list[str]:
        """Список доступных стратегий поиска."""
        return list(self._strategies.keys())

    def _select_strategy(self, granularity: RetrievalGranularity) -> "ISearchStrategy":
        """Выбор стратегии на основе гранулярности."""
        if granularity == RetrievalGranularity.DOCUMENT:
            return self._strategies["document_level"]
        return self._strategies["chunk_level"]

    def _extract_filters(self, parsed: Any) -> dict[str, Any]:
        """Извлечение фильтров из ParsedQuery."""
        filters: dict[str, Any] = {}
        if parsed.tags:
            filters["tags"] = parsed.tags
        if parsed.tags_or:
            filters["tags_or"] = parsed.tags_or
        if parsed.tags_not:
            filters["tags_not"] = parsed.tags_not
        if parsed.inline_tags:
            filters["inline_tags"] = parsed.inline_tags
        if parsed.inline_tags_or:
            filters["inline_tags_or"] = parsed.inline_tags_or
        if parsed.inline_tags_not:
            filters["inline_tags_not"] = parsed.inline_tags_not
        if parsed.doc_type:
            filters["doc_type"] = parsed.doc_type
        if parsed.doc_type_or:
            filters["doc_type_or"] = parsed.doc_type_or
        if parsed.doc_type_not:
            filters["doc_type_not"] = parsed.doc_type_not
        if parsed.links:
            filters["links"] = parsed.links
        if parsed.links_or:
            filters["links_or"] = parsed.links_or
        if parsed.links_not:
            filters["links_not"] = parsed.links_not
        if parsed.date_filters:
            filters["date_filters"] = parsed.date_filters
        return filters

    @staticmethod
    def _intent_to_granularity(intent: SearchIntent) -> RetrievalGranularity:
        """Маппинг intent → granularity."""
        document_intents = {
            SearchIntent.METADATA_FILTER,
            SearchIntent.KNOWN_ITEM,
            SearchIntent.PROCEDURAL,
        }
        if intent in document_intents:
            return RetrievalGranularity.DOCUMENT
        return RetrievalGranularity.CHUNK

