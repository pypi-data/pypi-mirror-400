"""Сервис векторного и гибридного поиска.

Вынесен из lance_db.py в рамках Phase 3 рефакторинга (v0.7.0).
"""

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

import lancedb
import lancedb.table
import pyarrow as pa

from obsidian_kb.config import settings
from obsidian_kb.core.data_normalizer import DataNormalizer
from obsidian_kb.core.ttl_cache import TTLCache
from obsidian_kb.schema_migrations import get_schema_for_table_type
from obsidian_kb.types import (
    DatabaseError,
    SearchResult,
    VaultNotFoundError,
)

if TYPE_CHECKING:
    from obsidian_kb.core.connection_manager import DBConnectionManager

logger = logging.getLogger(__name__)


class VectorSearchService:
    """Сервис векторного, полнотекстового и гибридного поиска.

    Отвечает за:
    - Векторный поиск (similarity search) по embeddings
    - Полнотекстовый поиск (FTS/BM25)
    - Гибридный поиск (комбинация vector + FTS)

    Attributes:
        DOCUMENT_CACHE_TTL_SECONDS: TTL для кэша метаданных документов
    """

    DOCUMENT_CACHE_TTL_SECONDS: float = 300.0

    def __init__(
        self,
        connection_manager: "DBConnectionManager",
        normalizer: DataNormalizer | None = None,
        cache: TTLCache | None = None,
    ) -> None:
        """Инициализация сервиса поиска.

        Args:
            connection_manager: Менеджер подключений к БД
            normalizer: Нормализатор данных (опционально)
            cache: TTL-кэш для метаданных документов (опционально)
        """
        self._connection_manager = connection_manager
        self._normalizer = normalizer if normalizer is not None else DataNormalizer()
        self._document_info_cache = cache if cache is not None else TTLCache(
            ttl_seconds=self.DOCUMENT_CACHE_TTL_SECONDS,
            max_size=10000,
        )

    def _get_db(self) -> lancedb.DBConnection:
        """Получение подключения к БД из пула."""
        return self._connection_manager.get_or_create_connection()

    def _normalize_vault_name(self, vault_name: str) -> str:
        """Нормализация имени vault'а для использования в именах таблиц."""
        import re

        safe_name = re.sub(r"[^a-zA-Z0-9_\-.]", "_", vault_name)
        safe_name = re.sub(r"_+", "_", safe_name)
        safe_name = safe_name.strip("_")
        return safe_name

    def _get_table_name(self, vault_name: str, table_type: str = "chunks") -> str:
        """Получение имени таблицы для vault'а и типа таблицы."""
        safe_name = self._normalize_vault_name(vault_name)
        return f"vault_{safe_name}_{table_type}"

    async def _ensure_table(
        self, vault_name: str, table_type: str = "chunks"
    ) -> lancedb.table.Table:
        """Создание или получение таблицы для vault'а.

        Если таблица не существует, создаётся пустая таблица с правильной схемой.
        Это обеспечивает совместимость с ожидаемым поведением LanceDBManager.

        Args:
            vault_name: Имя vault'а
            table_type: Тип таблицы (documents, chunks, document_properties, metadata)

        Returns:
            Таблица LanceDB
        """
        table_name = self._get_table_name(vault_name, table_type)
        db = self._get_db()

        def _ensure_table_sync() -> lancedb.table.Table:
            try:
                # Пытаемся открыть существующую таблицу
                table = db.open_table(table_name)
                # Проверяем схему
                schema = table.schema
                expected_schema = get_schema_for_table_type(
                    table_type, settings.embedding_dimensions
                )

                # Проверяем, соответствует ли схема ожидаемой
                schema_match = True
                if len(schema) != len(expected_schema):
                    schema_match = False
                else:
                    expected_field_names = {field.name for field in expected_schema}
                    actual_field_names = {field.name for field in schema}
                    if expected_field_names != actual_field_names:
                        schema_match = False

                # Если схема не соответствует, пересоздаём таблицу
                if not schema_match:
                    logger.info(
                        f"Table {table_name} schema is outdated. Recreating table."
                    )
                    logger.warning("Old data will be lost. Please reindex the vault.")
                    db.drop_table(table_name)
                    expected_schema = get_schema_for_table_type(
                        table_type, settings.embedding_dimensions
                    )
                    empty_table = pa.Table.from_pylist([], schema=expected_schema)
                    return db.create_table(table_name, empty_table, mode="overwrite")

                return table
            except Exception:
                # Создаём новую таблицу с пустыми данными для определения схемы
                expected_schema = get_schema_for_table_type(
                    table_type, settings.embedding_dimensions
                )
                empty_table = pa.Table.from_pylist([], schema=expected_schema)
                return db.create_table(table_name, empty_table, mode="overwrite")

        return await asyncio.to_thread(_ensure_table_sync)

    async def _create_fts_index(
        self, table: lancedb.table.Table, table_type: str = "chunks"
    ) -> None:
        """Создание FTS индекса для полнотекстового поиска.

        Args:
            table: Таблица LanceDB
            table_type: Тип таблицы (chunks или documents)
        """
        try:

            def _create_index() -> None:
                try:
                    if table_type == "documents":
                        try:
                            table.create_fts_index("title", replace=True)
                        except Exception as e:
                            logger.debug(f"Could not create FTS index on 'title': {e}")
                        try:
                            table.create_fts_index("file_path", replace=True)
                        except Exception as e:
                            logger.debug(
                                f"Could not create FTS index on 'file_path': {e}"
                            )
                    else:
                        table.create_fts_index("content", replace=True)
                except Exception as e:
                    if (
                        "already exists" not in str(e).lower()
                        and "already has" not in str(e).lower()
                    ):
                        raise

            await asyncio.to_thread(_create_index)
            logger.debug(f"FTS index created/updated for {table_type}")

        except Exception as e:
            logger.warning(f"Failed to create FTS index: {e}")

    def _dict_to_search_result(self, row: dict[str, Any], score: float) -> SearchResult:
        """Конвертация строки из БД в SearchResult.

        Args:
            row: Строка из БД
            score: Релевантность

        Returns:
            SearchResult
        """
        created_at = None
        if row.get("created_at"):
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except (ValueError, TypeError):
                pass

        modified_at = datetime.now()
        if row.get("modified_at"):
            try:
                modified_at = datetime.fromisoformat(row["modified_at"])
            except (ValueError, TypeError):
                pass

        return SearchResult(
            chunk_id=row["id"],
            vault_name=row["vault_name"],
            file_path=row["file_path"],
            title=row["title"],
            section=row["section"],
            content=row["content"],
            tags=row.get("tags", []),
            score=score,
            created_at=created_at,
            modified_at=modified_at,
        )

    async def _get_document_info_cached(
        self,
        vault_name: str,
        document_id: str,
    ) -> dict[str, Any] | None:
        """Получение метаданных документа с кэшированием и TTL.

        Args:
            vault_name: Имя vault'а
            document_id: ID документа

        Returns:
            Словарь с метаданными документа или None если документ не найден
        """
        cache_key = f"{vault_name}::{document_id}"

        cached_value = self._document_info_cache.get(cache_key)
        if cached_value is not None:
            if isinstance(cached_value, dict) and cached_value.get("__not_found__"):
                return None
            return cached_value

        try:
            documents_table = await self._ensure_table(vault_name, "documents")

            def _get_info() -> dict[str, Any] | None:
                try:
                    arrow_table = (
                        documents_table.search()
                        .where(f"document_id = '{document_id}'")
                        .to_arrow()
                    )
                    if arrow_table.num_rows > 0:
                        row = {
                            col: arrow_table[col][0].as_py()
                            for col in arrow_table.column_names
                        }
                        return row
                    return None
                except Exception:
                    return None

            doc_info = await asyncio.to_thread(_get_info)
            self._document_info_cache.set(
                cache_key, doc_info if doc_info else {"__not_found__": True}
            )
            return doc_info
        except Exception:
            return None

    def invalidate_document_cache(
        self, vault_name: str, document_id: str | None = None
    ) -> int:
        """Инвалидация кэша метаданных документов.

        Args:
            vault_name: Имя vault'а
            document_id: ID конкретного документа (если None — инвалидирует весь vault)

        Returns:
            Количество инвалидированных записей
        """
        if document_id:
            cache_key = f"{vault_name}::{document_id}"
            self._document_info_cache.invalidate(cache_key)
            return 1
        else:
            prefix = f"{vault_name}::"
            return self._document_info_cache.invalidate_prefix(prefix)

    async def vector_search(
        self,
        vault_name: str,
        query_vector: list[float],
        limit: int = 10,
        where: str | None = None,
        document_ids: set[str] | None = None,
    ) -> list[SearchResult]:
        """Векторный поиск по embeddings.

        Args:
            vault_name: Имя vault'а
            query_vector: Вектор запроса
            limit: Максимум результатов
            where: Дополнительное условие фильтрации чанков (SQL WHERE)
            document_ids: Опциональный фильтр по document_id для двухэтапных запросов

        Returns:
            Список результатов поиска, отсортированных по релевантности

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            chunks_table = await self._ensure_table(vault_name, "chunks")

            def _search() -> list[dict[str, Any]]:
                try:
                    query = chunks_table.search(query_vector).limit(limit)

                    if document_ids:
                        where_clause = " OR ".join(
                            [f"document_id = '{doc_id}'" for doc_id in document_ids]
                        )
                        if where:
                            query = query.where(f"({where}) AND ({where_clause})")
                        else:
                            query = query.where(where_clause)
                    elif where:
                        query = query.where(where)

                    arrow_table = query.to_arrow()
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    return arrow_table.to_pylist()
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            results = await asyncio.to_thread(_search)

            # Обогащение результатов метаданными из таблицы documents
            enriched_results: list[SearchResult] = []
            documents_cache: dict[str, dict[str, Any]] = {}

            # Собираем все уникальные document_id
            unique_doc_ids = set()
            for row in results:
                doc_id = row.get("document_id")
                if doc_id:
                    unique_doc_ids.add(doc_id)

            # Получаем метаданные параллельно батчами
            if unique_doc_ids:
                batch_size = 20
                doc_ids_list = list(unique_doc_ids)

                for i in range(0, len(doc_ids_list), batch_size):
                    batch_ids = doc_ids_list[i : i + batch_size]
                    tasks = [
                        self._get_document_info_cached(vault_name, doc_id)
                        for doc_id in batch_ids
                    ]
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                    for doc_id, doc_info in zip(batch_ids, batch_results):
                        if isinstance(doc_info, Exception):
                            logger.debug(
                                f"Error getting document info for {doc_id}: {doc_info}"
                            )
                            continue
                        if doc_info:
                            documents_cache[doc_id] = {
                                "file_path": doc_info.get("file_path", ""),
                                "title": doc_info.get("title", ""),
                                "created_at": doc_info.get("created_at"),
                                "modified_at": doc_info.get(
                                    "modified_at", datetime.now().isoformat()
                                ),
                            }

            # Строим результаты с метаданными из кэша
            for row in results:
                document_id = row.get("document_id")

                distance = row.get("_distance", 1.0)
                score = max(0.0, min(1.0, 1.0 - distance))

                doc_meta = documents_cache.get(document_id, {})
                enriched_row = {
                    "id": row.get("chunk_id", ""),
                    "vault_name": row.get("vault_name", vault_name),
                    "file_path": doc_meta.get("file_path", ""),
                    "title": doc_meta.get("title", ""),
                    "section": row.get("section", ""),
                    "content": row.get("content", ""),
                    "tags": [],
                    "created_at": doc_meta.get("created_at"),
                    "modified_at": doc_meta.get(
                        "modified_at", datetime.now().isoformat()
                    ),
                }
                enriched_results.append(self._dict_to_search_result(enriched_row, score))

            return enriched_results

        except VaultNotFoundError:
            raise
        except Exception as e:
            context = {
                "vault_name": vault_name,
                "query_vector_dim": len(query_vector),
                "limit": limit,
                "where": where,
                "document_ids_count": len(document_ids) if document_ids else 0,
            }
            logger.error(
                f"Error in vector search for vault '{vault_name}': {e}", extra=context
            )
            raise DatabaseError(
                f"Failed to perform vector search: {e}", context=context
            ) from e

    async def fts_search(
        self,
        vault_name: str,
        query: str,
        limit: int = 10,
        where: str | None = None,
        document_ids: set[str] | None = None,
    ) -> list[SearchResult]:
        """Полнотекстовый поиск (BM25).

        Args:
            vault_name: Имя vault'а
            query: Текст запроса
            limit: Максимум результатов
            where: SQL WHERE условие для фильтрации чанков
            document_ids: Опциональный фильтр по document_id для двухэтапных запросов

        Returns:
            Список результатов поиска, отсортированных по релевантности

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            chunks_table = await self._ensure_table(vault_name, "chunks")

            # Проверяем и создаем FTS индекс, если его нет
            try:
                await self._create_fts_index(chunks_table, "chunks")
            except Exception as e:
                logger.debug(f"FTS index check failed (may already exist): {e}")

            def _search() -> list[dict[str, Any]]:
                try:
                    search_query = (
                        chunks_table.search(query, query_type="fts")
                        if query.strip()
                        else chunks_table.search(query=None)
                    )

                    if document_ids:
                        where_clause = " OR ".join(
                            [f"document_id = '{doc_id}'" for doc_id in document_ids]
                        )
                        if where:
                            search_query = search_query.where(
                                f"({where}) AND ({where_clause})"
                            )
                        else:
                            search_query = search_query.where(where_clause)
                    elif where:
                        search_query = search_query.where(where)

                    arrow_table = search_query.limit(limit).to_arrow()
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    return arrow_table.to_pylist()
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            results = await asyncio.to_thread(_search)

            # Обогащение результатов метаданными из таблицы documents
            enriched_results: list[SearchResult] = []
            documents_cache: dict[str, dict[str, Any]] = {}

            # Собираем все уникальные document_id
            unique_doc_ids = set()
            for row in results:
                doc_id = row.get("document_id")
                if doc_id:
                    unique_doc_ids.add(doc_id)

            # Получаем метаданные параллельно батчами (устранение N+1)
            if unique_doc_ids:
                batch_size = 20
                doc_ids_list = list(unique_doc_ids)

                for i in range(0, len(doc_ids_list), batch_size):
                    batch_ids = doc_ids_list[i : i + batch_size]
                    tasks = [
                        self._get_document_info_cached(vault_name, doc_id)
                        for doc_id in batch_ids
                    ]
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                    for doc_id, doc_info in zip(batch_ids, batch_results):
                        if isinstance(doc_info, Exception):
                            logger.debug(
                                f"Error getting document info for {doc_id}: {doc_info}"
                            )
                            continue
                        if doc_info:
                            documents_cache[doc_id] = {
                                "file_path": doc_info.get("file_path", ""),
                                "title": doc_info.get("title", ""),
                                "created_at": doc_info.get("created_at"),
                                "modified_at": doc_info.get(
                                    "modified_at", datetime.now().isoformat()
                                ),
                            }

            # Строим результаты с метаданными из кэша
            for row in results:
                document_id = row.get("document_id")

                fts_score = row.get("_score", 0.0)
                score = min(1.0, fts_score / 10.0) if fts_score > 0 else 0.0

                doc_meta = documents_cache.get(document_id, {})
                enriched_row = {
                    "id": row.get("chunk_id", ""),
                    "vault_name": row.get("vault_name", vault_name),
                    "file_path": doc_meta.get("file_path", ""),
                    "title": doc_meta.get("title", ""),
                    "section": row.get("section", ""),
                    "content": row.get("content", ""),
                    "tags": [],
                    "created_at": doc_meta.get("created_at"),
                    "modified_at": doc_meta.get(
                        "modified_at", datetime.now().isoformat()
                    ),
                }
                enriched_results.append(self._dict_to_search_result(enriched_row, score))

            return enriched_results

        except VaultNotFoundError:
            raise
        except Exception as e:
            context = {
                "vault_name": vault_name,
                "query": query,
                "limit": limit,
                "where": where,
                "document_ids_count": len(document_ids) if document_ids else 0,
            }
            logger.error(
                f"Error in FTS search for vault '{vault_name}': {e}", extra=context
            )
            raise DatabaseError(
                f"Failed to perform FTS search: {e}", context=context
            ) from e

    async def hybrid_search(
        self,
        vault_name: str,
        query_vector: list[float],
        query_text: str,
        limit: int = 10,
        alpha: float | None = None,
        where: str | None = None,
        document_ids: set[str] | None = None,
    ) -> list[SearchResult]:
        """Гибридный поиск (векторный + FTS).

        Args:
            vault_name: Имя vault'а
            query_vector: Вектор запроса
            query_text: Текст запроса
            limit: Максимум результатов
            alpha: Вес векторного поиска (0-1, по умолчанию из settings)
            where: Дополнительное условие фильтрации (SQL WHERE)
            document_ids: Опциональный фильтр по document_id для двухэтапных запросов

        Returns:
            Список результатов поиска, отсортированных по комбинированной релевантности

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        if alpha is None:
            alpha = settings.hybrid_alpha

        try:
            # Выполняем оба поиска параллельно
            vector_results, fts_results = await asyncio.gather(
                self.vector_search(
                    vault_name,
                    query_vector,
                    limit=limit * 2,
                    where=where,
                    document_ids=document_ids,
                ),
                self.fts_search(
                    vault_name,
                    query_text,
                    limit=limit * 2,
                    where=where,
                    document_ids=document_ids,
                ),
                return_exceptions=True,
            )

            # Обрабатываем ошибки
            if isinstance(vector_results, Exception):
                logger.warning(f"Vector search failed: {vector_results}, using FTS only")
                vector_results = []
            if isinstance(fts_results, Exception):
                logger.warning(f"FTS search failed: {fts_results}, using vector only")
                fts_results = []

            # Улучшенный алгоритм объединения результатов
            results_dict: dict[str, SearchResult] = {}

            def normalize_scores(
                results: list[SearchResult], max_results: int
            ) -> dict[str, float]:
                """Нормализация scores с учётом позиции в результатах."""
                normalized = {}
                for idx, result in enumerate(results):
                    position_bonus = (max_results - idx) / max_results
                    normalized[result.chunk_id] = 0.7 * result.score + 0.3 * position_bonus
                return normalized

            vector_scores = normalize_scores(vector_results, len(vector_results))
            fts_scores = normalize_scores(fts_results, len(fts_results))

            # Собираем все уникальные chunk_id
            all_chunk_ids = set(vector_scores.keys()) | set(fts_scores.keys())

            # Создаём объединённые результаты
            for chunk_id in all_chunk_ids:
                vector_score = vector_scores.get(chunk_id, 0.0)
                fts_score = fts_scores.get(chunk_id, 0.0)

                combined_score = alpha * vector_score + (1 - alpha) * fts_score

                source_result = None
                for result in vector_results:
                    if result.chunk_id == chunk_id:
                        source_result = result
                        break
                if source_result is None:
                    for result in fts_results:
                        if result.chunk_id == chunk_id:
                            source_result = result
                            break

                if source_result:
                    updated_result = SearchResult(
                        chunk_id=source_result.chunk_id,
                        vault_name=source_result.vault_name,
                        file_path=source_result.file_path,
                        title=source_result.title,
                        section=source_result.section,
                        content=source_result.content,
                        tags=source_result.tags,
                        score=combined_score,
                        created_at=source_result.created_at,
                        modified_at=source_result.modified_at,
                    )
                    results_dict[chunk_id] = updated_result

            # Сортируем по score и берём топ limit
            sorted_results = sorted(
                results_dict.values(), key=lambda x: x.score, reverse=True
            )
            return sorted_results[:limit]

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in hybrid search for vault '{vault_name}': {e}")
            raise DatabaseError(f"Failed to perform hybrid search: {e}") from e
