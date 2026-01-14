"""Модуль оптимизации поиска: fine-tuning, re-ranking, query expansion.

Оптимизирован для использования через MCP с агентами (Claude, Cursor и др.).
"""

import hashlib
import logging
import math
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from obsidian_kb.embedding_service import EmbeddingService
from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.types import SearchResult

logger = logging.getLogger(__name__)


@dataclass
class RankingFeatures:
    """Признаки для ранжирования результатов поиска."""

    vector_score: float
    fts_score: float
    title_match: float  # Совпадение в заголовке (0-1)
    tag_match: float  # Совпадение тегов (0-1)
    recency: float  # Свежесть документа (0-1)
    popularity: float  # Популярность на основе обратной связи (0-1)
    link_count: int  # Количество ссылок на документ
    content_length: int  # Длина контента
    section_relevance: float  # Релевантность секции (0-1)
    content_match_ratio: float = 0.0  # Соотношение совпадений в контенте (0-1)
    length_score: float = 0.5  # Оценка оптимальности длины контента (0-1)


class AdaptiveAlphaCalculator:
    """Калькулятор адаптивного alpha для hybrid search."""

    @staticmethod
    def calculate(query: str, query_vector: list[float] | None = None) -> float:
        """Вычисление адаптивного alpha на основе характеристик запроса.

        Args:
            query: Поисковый запрос
            query_vector: Вектор запроса (опционально, для будущих улучшений)

        Returns:
            Alpha значение (0.0 - 1.0)
        """
        base_alpha = 0.7

        # Фактор 1: Длина запроса
        word_count = len(query.split())
        if word_count < 3:
            # Короткие запросы лучше работают с векторным поиском
            base_alpha = 0.8
        elif word_count > 10:
            # Длинные запросы могут содержать больше конкретных терминов
            base_alpha = 0.6

        # Фактор 2: Наличие технических терминов
        has_technical = bool(re.search(r'\d+|#[A-Za-z]+|`[^`]+`|[\w]+\.[\w]+', query))
        if has_technical:
            # Технические термины лучше находятся через FTS
            base_alpha -= 0.1

        # Фактор 3: Наличие кавычек (точное совпадение)
        if '"' in query or "'" in query:
            # Точные совпадения лучше через FTS
            base_alpha -= 0.15

        # Фактор 4: Вопросы (начинаются с вопросительных слов)
        question_words = ["что", "как", "где", "когда", "почему", "кто", "which", "what", "how", "where", "when", "why", "who"]
        if any(query.lower().startswith(word) for word in question_words):
            # Вопросы лучше обрабатываются семантически
            base_alpha += 0.1

        return max(0.3, min(0.9, base_alpha))


class QueryExpander:
    """Расширение поисковых запросов для улучшения recall."""

    def __init__(self, embedding_service: EmbeddingService, db_manager: LanceDBManager):
        """Инициализация expander'а.

        Args:
            embedding_service: Сервис для получения embeddings
            db_manager: Менеджер БД для поиска похожих документов
        """
        self.embedding_service = embedding_service
        self.db_manager = db_manager

    async def expand(self, query: str, vault_name: str, max_expansions: int = 3) -> list[str]:
        """Расширение запроса синонимами и связанными терминами.

        Args:
            query: Исходный запрос
            vault_name: Имя vault'а
            max_expansions: Максимальное количество расширений

        Returns:
            Список расширенных запросов (включая исходный)
        """
        expanded = [query]

        try:
            # Получаем embedding для исходного запроса
            query_embedding = await self.embedding_service.get_embedding(query, embedding_type="query")

            # Находим похожие документы для извлечения терминов
            # Используем репозиторий чанков вместо прямого вызова db_manager
            chunk_results = await self.db_manager.chunks.vector_search(
                vault_name, query_embedding, limit=5
            )
            # Конвертируем ChunkSearchResult в SearchResult для совместимости
            similar = [cr.to_legacy() for cr in chunk_results]

            # Извлекаем ключевые термины из похожих документов
            all_terms: set[str] = set()
            for result in similar:
                # Простое извлечение ключевых слов (можно улучшить через TF-IDF)
                words = re.findall(r'\b\w{4,}\b', result.content.lower())
                # Фильтруем стоп-слова
                stop_words = {
                    "это", "что", "как", "для", "при", "или", "the", "and", "or", "for", "with", "from"
                }
                meaningful_words = [w for w in words if w not in stop_words]
                all_terms.update(meaningful_words[:5])  # Топ-5 слов из каждого документа

            # Добавляем уникальные термины к запросу
            for term in list(all_terms)[:max_expansions]:
                if term not in query.lower():
                    expanded.append(f"{query} {term}")

        except Exception as e:
            logger.warning(f"Query expansion failed: {e}, using original query")
            return [query]

        return expanded[:max_expansions + 1]  # Ограничиваем количество


class ReRanker:
    """Re-ranking результатов поиска для улучшения precision.
    
    Использует кэширование embeddings для улучшения производительности
    и всегда применяет reranking для максимальной точности результатов.
    """

    def __init__(self, embedding_service: EmbeddingService):
        """Инициализация re-ranker'а.

        Args:
            embedding_service: Сервис для получения embeddings (с встроенным кэшем)
        """
        self.embedding_service = embedding_service
        # Кэш для embeddings превью контента (ключ: hash(content_preview))
        self._content_cache: dict[str, list[float]] = {}
        self._cache_size = 1000  # Максимальный размер кэша

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Вычисление косинусного сходства между векторами.

        Args:
            vec1: Первый вектор
            vec2: Второй вектор

        Returns:
            Косинусное сходство (0-1)
        """
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _get_cache_key(self, text: str) -> str:
        """Генерация ключа кэша для текста.
        
        Args:
            text: Текст для кэширования
            
        Returns:
            SHA256 хеш текста
        """
        return hashlib.sha256(text.encode()).hexdigest()

    async def rerank(
        self, query: str, results: list[SearchResult], top_k: int = 10, cross_weight: float = 0.4
    ) -> list[SearchResult]:
        """Переранжирование результатов на основе cross-encoder подхода.
        
        Всегда применяет reranking для максимальной точности результатов.
        Использует кэширование для улучшения производительности.

        Args:
            query: Поисковый запрос
            results: Исходные результаты поиска
            top_k: Количество результатов для возврата
            cross_weight: Вес cross-encoder score (0-1, по умолчанию 0.4)

        Returns:
            Переранжированные результаты
        """
        # Для пустых результатов возвращаем как есть
        if not results:
            return results

        try:
            # Получаем embedding запроса (использует встроенный кэш EmbeddingService)
            query_embedding = await self.embedding_service.get_embedding(query, embedding_type="query")

            # Вычисляем улучшенные scores с кэшированием
            cache_hits = 0
            cache_misses = 0
            reranked = []
            for result in results:
                # Получаем embedding результата (ограничиваем длину для производительности)
                content_preview = result.content[:500]  # Первые 500 символов
                
                # Проверяем кэш для превью контента
                cache_key = self._get_cache_key(content_preview)
                if cache_key in self._content_cache:
                    result_embedding = self._content_cache[cache_key]
                    cache_hits += 1
                    logger.debug(f"Cache hit for content preview (chunk_id: {result.chunk_id[:20]}...)")
                else:
                    # Получаем embedding (использует встроенный кэш EmbeddingService)
                    result_embedding = await self.embedding_service.get_embedding(
                        content_preview, embedding_type="doc"
                    )
                    cache_misses += 1
                    
                    # Сохраняем в локальный кэш
                    if len(self._content_cache) >= self._cache_size:
                        # Удаляем самый старый элемент (FIFO)
                        oldest_key = next(iter(self._content_cache))
                        del self._content_cache[oldest_key]
                    self._content_cache[cache_key] = result_embedding

                # Комбинируем оригинальный score с cross-encoder score
                cross_score = self._cosine_similarity(query_embedding, result_embedding)

                # Взвешенная комбинация (для точности используем больше веса cross-encoder)
                original_weight = 1.0 - cross_weight
                final_score = original_weight * result.score + cross_weight * cross_score

                # Создаём новый результат с обновлённым score
                reranked.append(
                    SearchResult(
                        chunk_id=result.chunk_id,
                        vault_name=result.vault_name,
                        file_path=result.file_path,
                        title=result.title,
                        section=result.section,
                        content=result.content,
                        tags=result.tags,
                        score=final_score,
                        created_at=result.created_at,
                        modified_at=result.modified_at,
                    )
                )

            # Сортируем и возвращаем топ-k
            reranked.sort(key=lambda x: x.score, reverse=True)
            
            # Логируем метрики reranking для отслеживания эффективности
            total_cache_checks = cache_hits + cache_misses
            cache_hit_rate = (cache_hits / total_cache_checks * 100) if total_cache_checks > 0 else 0.0
            logger.info(
                f"Reranked {len(results)} results (returning top {min(top_k, len(reranked))}), "
                f"cache: {cache_hits}/{total_cache_checks} hits ({cache_hit_rate:.1f}%)"
            )
            
            return reranked[:top_k]

        except Exception as e:
            logger.warning(f"Re-ranking failed: {e}, returning original results")
            return results[:top_k]


class FeatureExtractor:
    """Извлечение признаков для ранжирования."""

    @staticmethod
    def extract(result: SearchResult, query: str, query_embedding: list[float] | None = None) -> RankingFeatures:
        """Извлечение признаков для ранжирования.

        Args:
            result: Результат поиска
            query: Поисковый запрос
            query_embedding: Вектор запроса (опционально)

        Returns:
            RankingFeatures с извлечёнными признаками
        """
        # Title match
        title_lower = result.title.lower()
        query_lower = query.lower()
        query_words = query_lower.split()
        if query_words:
            title_match = sum(1 for word in query_words if word in title_lower) / len(query_words)
        else:
            title_match = 0.0

        # Tag match
        if result.tags:
            tag_match = sum(
                1 for tag in result.tags if any(word in tag.lower() for word in query_words)
            ) / len(result.tags)
        else:
            tag_match = 0.0

        # Recency (0-1, где 1 = самый свежий)
        if result.modified_at:
            days_old = (datetime.now() - result.modified_at).days
            recency = max(0.0, 1.0 - (days_old / 365.0))  # Нормализация на год
        else:
            recency = 0.5  # Среднее значение если дата неизвестна

        # Section relevance (улучшенная: учитываем точное совпадение и частичное)
        section_lower = result.section.lower()
        section_words = section_lower.split()
        if query_words and section_words:
            # Точное совпадение слов
            exact_matches = sum(1 for word in query_words if word in section_words)
            # Частичное совпадение (подстрока)
            partial_matches = sum(1 for word in query_words if any(word in sw or sw in word for sw in section_words))
            section_relevance = (exact_matches * 1.0 + partial_matches * 0.5) / len(query_words)
        else:
            section_relevance = 0.0
        
        # Content match (количество совпадений в контенте)
        content_lower = result.content.lower()
        content_matches = sum(1 for word in query_words if word in content_lower) if query_words else 0
        content_match_ratio = content_matches / max(len(query_words), 1) if query_words else 0.0
        
        # Длина контента (нормализованная, предпочитаем среднюю длину)
        optimal_length = 500  # Оптимальная длина чанка
        length_score = 1.0 - abs(len(result.content) - optimal_length) / optimal_length
        length_score = max(0.0, min(1.0, length_score))

        return RankingFeatures(
            vector_score=result.score,
            fts_score=result.score,  # В hybrid search уже объединённый
            title_match=title_match,
            tag_match=tag_match,
            recency=recency,
            popularity=0.5,  # По умолчанию, можно улучшить через feedback систему
            link_count=len(result.tags) if hasattr(result, "tags") else 0,  # Используем tags как proxy
            content_length=len(result.content),
            section_relevance=section_relevance,
            content_match_ratio=content_match_ratio,
            length_score=length_score,
        )


class RankingModel:
    """Модель ранжирования на основе признаков."""

    def __init__(self, weights: dict[str, float] | None = None):
        """Инициализация модели.

        Args:
            weights: Веса признаков (по умолчанию используются оптимальные значения)
        """
        self.weights = weights or {
            "vector_score": 0.25,
            "fts_score": 0.15,
            "title_match": 0.15,
            "tag_match": 0.1,
            "recency": 0.08,
            "popularity": 0.08,
            "link_count": 0.04,
            "section_relevance": 0.1,
            "content_match_ratio": 0.05,
            "length_score": 0.0,  # Небольшой бонус за оптимальную длину
        }

        # Нормализация весов
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def predict_score(self, features: RankingFeatures) -> float:
        """Предсказание финального score на основе признаков.

        Args:
            features: Признаки результата поиска

        Returns:
            Финальный score (0-1)
        """
        score = (
            self.weights["vector_score"] * features.vector_score
            + self.weights["fts_score"] * features.fts_score
            + self.weights["title_match"] * features.title_match
            + self.weights["tag_match"] * features.tag_match
            + self.weights["recency"] * features.recency
            + self.weights["popularity"] * features.popularity
            + self.weights["link_count"] * min(features.link_count / 10.0, 1.0)  # Нормализация
            + self.weights["section_relevance"] * features.section_relevance
            + self.weights.get("content_match_ratio", 0.0) * features.content_match_ratio
            + self.weights.get("length_score", 0.0) * features.length_score
        )

        return min(1.0, max(0.0, score))

    def apply_ranking(self, results: list[SearchResult], query: str) -> list[SearchResult]:
        """Применение ранжирования к результатам.

        Args:
            results: Результаты поиска
            query: Поисковый запрос

        Returns:
            Переранжированные результаты
        """
        feature_extractor = FeatureExtractor()
        ranked = []

        for result in results:
            features = feature_extractor.extract(result, query)
            new_score = self.predict_score(features)

            ranked.append(
                SearchResult(
                    chunk_id=result.chunk_id,
                    vault_name=result.vault_name,
                    file_path=result.file_path,
                    title=result.title,
                    section=result.section,
                    content=result.content,
                    tags=result.tags,
                    score=new_score,
                    created_at=result.created_at,
                    modified_at=result.modified_at,
                )
            )

        # Сортируем по новому score
        ranked.sort(key=lambda x: x.score, reverse=True)
        return ranked


class AgentQueryNormalizer:
    """Нормализация запросов от агентов (Claude, Cursor и др.).

    Агенты часто добавляют служебные слова, которые нужно убрать для улучшения поиска.
    """

    # Паттерны служебных слов, которые агенты часто добавляют
    AGENT_PATTERNS = [
        r"найди\s+",
        r"найти\s+",
        r"покажи\s+",
        r"ищи\s+",
        r"find\s+",
        r"search\s+for\s+",
        r"show\s+me\s+",
        r"что\s+написано\s+про\s+",
        r"информация\s+о\s+",
        r"расскажи\s+про\s+",
        r"give\s+me\s+",
        r"look\s+for\s+",
        r"get\s+me\s+",
    ]

    @classmethod
    def normalize(cls, query: str) -> str:
        """Нормализация агентного запроса.

        Args:
            query: Исходный запрос от агента

        Returns:
            Нормализованный запрос
        """
        normalized = query.strip()

        # Убираем служебные слова агентов
        for pattern in cls.AGENT_PATTERNS:
            normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE)

        # Убираем лишние пробелы
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized if normalized else query  # Возвращаем исходный если всё удалилось


class AgentQueryCache:
    """LRU кэш для агентных запросов.

    Агенты часто делают похожие запросы, кэширование помогает ускорить ответ.
    Использует LRU (Least Recently Used) стратегию для управления размером кэша.
    """

    def __init__(self, max_size: int = 100):
        """Инициализация кэша.

        Args:
            max_size: Максимальный размер кэша
        """
        self.cache: dict[str, tuple[list[SearchResult], int]] = {}  # (results, access_time)
        self.max_size = max_size
        self.access_counter = 0

    def _cache_key(self, vault_name: str, query: str, where: str | None = None) -> str:
        """Генерация ключа кэша.

        Args:
            vault_name: Имя vault'а
            query: Поисковый запрос
            where: WHERE clause для фильтрации (опционально)

        Returns:
            Хеш-ключ для кэша
        """
        # Нормализуем запрос перед хешированием
        normalized = AgentQueryNormalizer.normalize(query)
        # Включаем фильтры в ключ кэша
        where_part = f"::{where}" if where else ""
        key_str = f"{vault_name}::{normalized.lower().strip()}{where_part}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get_or_search(
        self,
        vault_name: str,
        query: str,
        search_func: Callable[[], Any],
        where: str | None = None,
    ) -> list[SearchResult]:
        """Получить из кэша или выполнить поиск.

        Args:
            vault_name: Имя vault'а
            query: Поисковый запрос
            search_func: Асинхронная функция поиска
            where: WHERE clause для фильтрации (опционально)

        Returns:
            Результаты поиска
        """
        key = self._cache_key(vault_name, query, where)

        if key in self.cache:
            # Обновляем время доступа (LRU)
            self.access_counter += 1
            results, _ = self.cache[key]
            self.cache[key] = (results, self.access_counter)
            logger.debug(f"Cache hit for query: {query[:50]}")
            return results

        # Выполняем поиск
        results = await search_func()

        # Сохраняем в кэш (LRU eviction)
        self.access_counter += 1
        if len(self.cache) >= self.max_size:
            # Удаляем самый старый (наименьший access_time)
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
            logger.debug(f"Evicted cache entry: {oldest_key[:20]}...")

        self.cache[key] = (results, self.access_counter)
        logger.debug(f"Cached query: {query[:50]}")
        return results

    def clear(self) -> None:
        """Очистка кэша."""
        self.cache.clear()
        logger.debug("Query cache cleared")


class SearchOptimizer:
    """Главный класс для оптимизации поиска.

    Оптимизирован для использования через MCP с агентами (Claude, Cursor и др.).
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        db_manager: LanceDBManager,
        enable_rerank: bool = True,
        enable_query_expansion: bool = False,
        enable_feature_ranking: bool = True,
        enable_agent_normalization: bool = True,
        enable_query_cache: bool = True,
        cache_size: int = 100,
    ):
        """Инициализация оптимизатора.

        Args:
            embedding_service: Сервис для получения embeddings
            db_manager: Менеджер БД
            enable_rerank: Включить re-ranking
            enable_query_expansion: Включить расширение запросов
            enable_feature_ranking: Включить feature-based ranking
            enable_agent_normalization: Включить нормализацию агентных запросов
            enable_query_cache: Включить кэширование запросов
            cache_size: Размер кэша запросов
        """
        self.embedding_service = embedding_service
        self.db_manager = db_manager
        self.enable_rerank = enable_rerank
        self.enable_query_expansion = enable_query_expansion
        self.enable_feature_ranking = enable_feature_ranking
        self.enable_agent_normalization = enable_agent_normalization
        self.enable_query_cache = enable_query_cache

        self.alpha_calculator = AdaptiveAlphaCalculator()
        self.query_expander = QueryExpander(embedding_service, db_manager) if enable_query_expansion else None
        self.reranker = ReRanker(embedding_service) if enable_rerank else None
        self.ranking_model = RankingModel() if enable_feature_ranking else None
        self.query_cache = AgentQueryCache(max_size=cache_size) if enable_query_cache else None

    async def optimize_search(
        self,
        vault_name: str,
        query: str,
        query_vector: list[float],
        limit: int = 10,
        adaptive_alpha: bool = True,
        use_cache: bool = True,
        where: str | None = None,
        document_ids: set[str] | None = None,
    ) -> list[SearchResult]:
        """Оптимизированный поиск с применением всех улучшений (v4).

        Оптимизирован для использования через MCP с агентами.

        Args:
            vault_name: Имя vault'а
            query: Поисковый запрос (может быть от агента)
            query_vector: Вектор запроса
            limit: Максимум результатов
            adaptive_alpha: Использовать адаптивный alpha
            use_cache: Использовать кэш запросов
            where: WHERE clause для фильтрации чанков (SQL-подобный синтаксис)
            document_ids: Опциональный фильтр по document_id для двухэтапных запросов (v4)

        Returns:
            Оптимизированные результаты поиска
        """
        # 1. Нормализация агентного запроса
        search_query = query
        if self.enable_agent_normalization:
            search_query = AgentQueryNormalizer.normalize(query)
            if search_query != query:
                logger.debug(f"Normalized agent query: '{query}' -> '{search_query}'")

        # 2. Проверка кэша
        async def _perform_search() -> list[SearchResult]:
            # Вычисляем адаптивный alpha если включено
            if adaptive_alpha:
                alpha = self.alpha_calculator.calculate(search_query, query_vector)
            else:
                from obsidian_kb.config import settings

                alpha = settings.hybrid_alpha

            # Выполняем hybrid search через репозитории
            # Получаем результаты от vector и fts поиска
            vector_results = await self.db_manager.chunks.vector_search(
                vault_name, query_vector, limit=limit * 2, where=where, filter_document_ids=document_ids
            )
            fts_results = await self.db_manager.chunks.fts_search(
                vault_name, search_query, limit=limit * 2, where=where, filter_document_ids=document_ids
            )
            
            # Объединяем результаты используя RRF (Reciprocal Rank Fusion)
            from obsidian_kb.search.strategies.chunk_level import ChunkLevelStrategy
            # Используем временный экземпляр стратегии для объединения
            temp_strategy = ChunkLevelStrategy(
                self.db_manager.documents,
                self.db_manager.chunks,
                self.embedding_service,
                aggregation="rrf"
            )
            # Конвертируем ChunkSearchResult в формат для объединения
            merged_results = temp_strategy._merge_results(
                vector_results,
                fts_results,
                alpha=alpha
            )
            # Конвертируем обратно в SearchResult для совместимости
            results = [cr.to_legacy() for cr in merged_results]

            if not results:
                return []

            # Re-ranking всегда включен для максимальной точности результатов
            # Для небольших vault'ов reranking быстрый и значительно улучшает качество
            if self.reranker:
                # Используем reranking для всех результатов (не только если len > limit)
                # Это особенно важно для точности в небольших vault'ах
                results = await self.reranker.rerank(search_query, results, top_k=limit * 2, cross_weight=0.4)

            # Feature-based ranking если включено
            if self.ranking_model:
                results = self.ranking_model.apply_ranking(results, search_query)

            return results[:limit]

        # Используем кэш если включен
        if self.enable_query_cache and use_cache and self.query_cache:
            results = await self.query_cache.get_or_search(vault_name, search_query, _perform_search, where=where)
        else:
            results = await _perform_search()

        return results

