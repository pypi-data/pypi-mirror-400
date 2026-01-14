"""Стратегия поиска на уровне чанков."""

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any

from obsidian_kb.config import settings
from obsidian_kb.search.strategies.base import BaseSearchStrategy
from obsidian_kb.types import ChunkSearchResult, DocumentSearchResult, MatchType, RelevanceScore

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IChunkRepository, IEmbeddingService

logger = logging.getLogger(__name__)


class ChunkLevelStrategy(BaseSearchStrategy):
    """Стратегия поиска, группирующая чанки по документам.
    
    Используется для:
    - Семантического поиска
    - Exploratory запросов
    """

    def __init__(
        self,
        document_repo: "IDocumentRepository",
        chunk_repo: "IChunkRepository",
        embedding_service: "IEmbeddingService",
        aggregation: str = "max",  # max | mean | rrf
    ) -> None:
        """Инициализация стратегии.
        
        Args:
            document_repo: Репозиторий документов
            chunk_repo: Репозиторий чанков
            embedding_service: Сервис для генерации embeddings
            aggregation: Метод агрегации scores (max, mean, rrf)
        """
        super().__init__(document_repo)
        self._chunks = chunk_repo
        self._embeddings = embedding_service
        self._aggregation = aggregation

    @property
    def name(self) -> str:
        """Имя стратегии."""
        return "chunk_level"

    async def search(
        self,
        vault_name: str,
        query: str,
        parsed_filters: dict[str, Any],
        limit: int = 10,
        options: dict[str, Any] | None = None,
    ) -> list[DocumentSearchResult]:
        """Выполнение поиска на уровне чанков с группировкой по документам.
        
        Args:
            vault_name: Имя vault'а
            query: Текстовый запрос
            parsed_filters: Извлечённые фильтры
            limit: Максимум результатов
            options: Дополнительные опции (search_type)
        """
        try:
            start_time = time.time()
            options = options or {}
            search_type = options.get("search_type", "hybrid")
            
            # Проверяем, что есть query для chunk-level поиска
            if not query or not query.strip():
                logger.warning("ChunkLevelStrategy requires a non-empty query")
                return []
            
            # 1. Получаем document_ids для pre-filtering (если есть фильтры)
            filter_time_start = time.time()
            filter_doc_ids: set[str] | None = None
            if parsed_filters:
                filter_doc_ids = await self._apply_filters(vault_name, parsed_filters)
                if filter_doc_ids is not None and not filter_doc_ids:
                    return []  # Фильтры не вернули документов
            filter_time = (time.time() - filter_time_start) * 1000
            if filter_time > 10:  # Логируем только если > 10мс
                logger.debug(f"[PERF] ChunkLevelStrategy.filter: {filter_time:.1f}ms")
            
            # 2. Выполняем chunk-level поиск
            search_time_start = time.time()
            chunk_results = await self._execute_search(
                vault_name, query, search_type,
                limit=limit * 3,  # Запрашиваем больше для группировки
                filter_document_ids=filter_doc_ids,
            )
            search_time = (time.time() - search_time_start) * 1000
            
            if not chunk_results:
                return []
            
            # 3. Группируем по документам
            grouping_time_start = time.time()
            grouped = self._group_by_document(chunk_results)
            grouping_time = (time.time() - grouping_time_start) * 1000
            
            # 4. Агрегируем scores и строим результаты
            build_time_start = time.time()
            results = await self._build_results(vault_name, grouped)
            build_time = (time.time() - build_time_start) * 1000
            
            # 5. Сортируем и ограничиваем
            sort_time_start = time.time()
            results.sort(key=lambda r: r.score.value, reverse=True)
            sort_time = (time.time() - sort_time_start) * 1000
            
            total_time = (time.time() - start_time) * 1000
            
            # Логируем детальное время выполнения
            logger.debug(
                f"[PERF] ChunkLevelStrategy.search('{query[:50]}...'): "
                f"total={total_time:.1f}ms, "
                f"search={search_time:.1f}ms, "
                f"build={build_time:.1f}ms, "
                f"grouping={grouping_time:.1f}ms, "
                f"sort={sort_time:.1f}ms, "
                f"results={len(results[:limit])}"
            )
            
            return results[:limit]
        except Exception as e:
            logger.error(f"Error in ChunkLevelStrategy.search for vault '{vault_name}': {e}")
            return []

    async def _execute_search(
        self,
        vault_name: str,
        query: str,
        search_type: str,
        limit: int,
        filter_document_ids: set[str] | None,
    ) -> list[ChunkSearchResult]:
        """Выполнение поиска нужного типа."""
        try:
            if search_type == "vector":
                embedding_start = time.time()
                embedding = await self._embeddings.get_embedding(query, embedding_type="query")
                embedding_time = (time.time() - embedding_start) * 1000
                
                vector_start = time.time()
                results = await self._chunks.vector_search(
                    vault_name, embedding, limit, filter_document_ids
                )
                vector_time = (time.time() - vector_start) * 1000
                
                logger.debug(
                    f"[PERF] ChunkLevelStrategy._execute_search(vector): "
                    f"embedding={embedding_time:.1f}ms, "
                    f"vector_search={vector_time:.1f}ms, "
                    f"total={embedding_time + vector_time:.1f}ms"
                )
                return results
            elif search_type == "fts":
                fts_start = time.time()
                results = await self._chunks.fts_search(
                    vault_name, query, limit, filter_document_ids
                )
                fts_time = (time.time() - fts_start) * 1000
                
                logger.debug(
                    f"[PERF] ChunkLevelStrategy._execute_search(fts): "
                    f"fts_search={fts_time:.1f}ms"
                )
                return results
            else:  # hybrid
                # ОПТИМИЗАЦИЯ: Вычисляем embedding один раз для гибридного поиска
                embedding_start = time.time()
                embedding = await self._embeddings.get_embedding(query, embedding_type="query")
                embedding_time = (time.time() - embedding_start) * 1000
                
                # Выполняем оба поиска параллельно
                search_start = time.time()
                vector_results, fts_results = await asyncio.gather(
                    self._chunks.vector_search(
                        vault_name, embedding, limit, filter_document_ids
                    ),
                    self._chunks.fts_search(
                        vault_name, query, limit, filter_document_ids
                    ),
                    return_exceptions=True,
                )
                search_time = (time.time() - search_start) * 1000
                
                # Обрабатываем исключения
                if isinstance(vector_results, Exception):
                    logger.error(f"Vector search failed: {vector_results}")
                    vector_results = []
                if isinstance(fts_results, Exception):
                    logger.error(f"FTS search failed: {fts_results}")
                    fts_results = []
                
                merge_start = time.time()
                results = self._merge_results(vector_results, fts_results)
                merge_time = (time.time() - merge_start) * 1000
                
                logger.debug(
                    f"[PERF] ChunkLevelStrategy._execute_search(hybrid): "
                    f"embedding={embedding_time:.1f}ms, "
                    f"parallel_search={search_time:.1f}ms, "
                    f"merge={merge_time:.1f}ms, "
                    f"total={embedding_time + search_time + merge_time:.1f}ms"
                )
                return results
        except Exception as e:
            logger.error(f"Error executing {search_type} search: {e}")
            return []

    def _group_by_document(
        self,
        chunk_results: list[ChunkSearchResult],
    ) -> dict[str, list[ChunkSearchResult]]:
        """Группировка чанков по документам."""
        groups: dict[str, list[ChunkSearchResult]] = {}
        for result in chunk_results:
            doc_id = result.chunk.document_id
            if doc_id not in groups:
                groups[doc_id] = []
            groups[doc_id].append(result)
        return groups

    async def _build_results(
        self,
        vault_name: str,
        grouped: dict[str, list[ChunkSearchResult]],
    ) -> list[DocumentSearchResult]:
        """Построение DocumentSearchResult из групп."""
        if not grouped:
            return []
        
        # ОПТИМИЗАЦИЯ: Получаем все документы и их properties параллельно батчами
        doc_ids = list(grouped.keys())
        
        # Получаем документы батчами
        documents_map: dict[str, Any] = {}
        properties_map: dict[str, dict[str, Any]] = {}
        
        # Батчинг для получения документов и properties параллельно
        batch_size = 20  # Размер батча для параллельных запросов
        
        for i in range(0, len(doc_ids), batch_size):
            batch_ids = doc_ids[i:i + batch_size]
            
            # Параллельно получаем документы и properties
            tasks = []
            for doc_id in batch_ids:
                tasks.append(self._documents.get(vault_name, doc_id))
                tasks.append(self._documents.get_properties(vault_name, doc_id))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Распределяем результаты
            for idx, doc_id in enumerate(batch_ids):
                doc_result = results[idx * 2]
                props_result = results[idx * 2 + 1]
                
                if isinstance(doc_result, Exception):
                    logger.warning(f"Error getting document {doc_id}: {doc_result}")
                    continue
                if isinstance(props_result, Exception):
                    logger.warning(f"Error getting properties for {doc_id}: {props_result}")
                    props_result = {}
                
                if doc_result:
                    documents_map[doc_id] = doc_result
                    properties_map[doc_id] = props_result if isinstance(props_result, dict) else {}
        
        # Строим результаты
        results = []
        for doc_id, chunks in grouped.items():
            try:
                if doc_id not in documents_map:
                    logger.warning(f"Document {doc_id} not found, skipping")
                    continue
                
                # Сортируем чанки по score
                chunks.sort(key=lambda c: c.score.value, reverse=True)
                
                # Агрегируем score
                aggregated_score = self._aggregate_scores(chunks)
                
                # Получаем документ и properties из кэша
                doc = documents_map[doc_id]
                properties = properties_map.get(doc_id, {})
                
                # Добавляем properties и теги
                doc.properties = properties
                
                # Извлекаем теги
                if "tags" in properties:
                    tags_value = properties["tags"]
                    if isinstance(tags_value, list):
                        doc.tags = tags_value
                    elif isinstance(tags_value, str):
                        doc.tags = [t.strip() for t in tags_value.split(",")]
                
                results.append(DocumentSearchResult(
                    document=doc,
                    score=aggregated_score,
                    matched_chunks=chunks[:3],  # Топ-3 чанка
                    matched_sections=list(set([c.chunk.section for c in chunks[:5] if c.chunk.section])),
                ))
            except Exception as e:
                logger.warning(f"Error building result for document {doc_id}: {e}")
                continue
        
        return results

    def _aggregate_scores(self, chunks: list[ChunkSearchResult]) -> RelevanceScore:
        """Агрегация scores чанков в document score."""
        if not chunks:
            return RelevanceScore.exact_match()
        
        if self._aggregation == "max":
            best = max(chunks, key=lambda c: c.score.value)
            return RelevanceScore(
                value=best.score.value,
                match_type=best.score.match_type,
                confidence=best.score.confidence,
                components={"max_chunk": best.score.value, "chunk_count": len(chunks)},
            )
        elif self._aggregation == "mean":
            mean_value = sum(c.score.value for c in chunks) / len(chunks)
            return RelevanceScore(
                value=mean_value,
                match_type=MatchType.HYBRID,
                confidence=0.8,
                components={"mean": mean_value, "chunk_count": len(chunks)},
            )
        else:  # rrf
            rrf_score = sum(1 / (60 + i + 1) for i in range(len(chunks)))
            normalized = min(1.0, rrf_score / 0.1)  # Нормализация
            return RelevanceScore(
                value=normalized,
                match_type=MatchType.HYBRID,
                confidence=0.85,
                components={"rrf": rrf_score, "chunk_count": len(chunks)},
            )

    def _merge_results(
        self,
        vector_results: list[ChunkSearchResult],
        fts_results: list[ChunkSearchResult],
        alpha: float | None = None,
    ) -> list[ChunkSearchResult]:
        """Объединение vector и FTS результатов через RRF."""
        if alpha is None:
            alpha = settings.hybrid_alpha
        
        # RRF fusion
        chunk_scores: dict[str, float] = {}
        chunk_results: dict[str, ChunkSearchResult] = {}
        k = 60
        
        # Добавляем vector результаты
        for rank, result in enumerate(vector_results, 1):
            chunk_id = result.chunk.chunk_id
            chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + alpha * (1 / (k + rank))
            if chunk_id not in chunk_results:
                chunk_results[chunk_id] = result
        
        # Добавляем FTS результаты
        for rank, result in enumerate(fts_results, 1):
            chunk_id = result.chunk.chunk_id
            chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + (1 - alpha) * (1 / (k + rank))
            if chunk_id not in chunk_results:
                chunk_results[chunk_id] = result
        
        # Сортируем по RRF score
        sorted_ids = sorted(chunk_scores.keys(), key=lambda x: chunk_scores[x], reverse=True)
        
        # Создаём объединённые результаты с новыми scores
        merged = []
        for chunk_id in sorted_ids:
            chunk_result = chunk_results[chunk_id]
            # Обновляем score на основе RRF
            rrf_value = min(1.0, chunk_scores[chunk_id])
            merged.append(ChunkSearchResult(
                chunk=chunk_result.chunk,
                score=RelevanceScore(
                    value=rrf_value,
                    match_type=MatchType.HYBRID,
                    confidence=0.85,
                    components={"vector": chunk_result.score.value, "rrf": rrf_value},
                ),
            ))
        
        return merged

