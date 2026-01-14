"""Модуль работы с LanceDB для хранения и поиска чанков."""

import asyncio
import json
import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import lancedb
import pyarrow as pa

from obsidian_kb.config import settings
from obsidian_kb.core.data_normalizer import DataNormalizer
from obsidian_kb.core.ttl_cache import TTLCache

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IChunkRepository, IDocumentRepository
from obsidian_kb.db_connection_manager import DBConnectionManager
from obsidian_kb.performance_monitor import PerformanceMonitor
from obsidian_kb.schema_migrations import get_schema_for_table_type
from obsidian_kb.search.vector_search_service import VectorSearchService
from obsidian_kb.storage.indexing import IndexingService
from obsidian_kb.storage.metadata_service import MetadataService
from obsidian_kb.types import (
    DatabaseError,
    DocumentChunk,
    DocumentInfo,
    SearchResult,
    VaultNotFoundError,
    VaultStats,
)

logger = logging.getLogger(__name__)

# Глобальный экземпляр PerformanceMonitor
_performance_monitor = PerformanceMonitor()

# Порог для создания IVF-PQ индекса
# Снижен до 500 для поддержки небольших vault'ов и улучшения точности поиска
IVF_PQ_THRESHOLD = 500


class LanceDBManager:
    """Менеджер для работы с LanceDB."""

    # TTL для кэша метаданных документов (5 минут по умолчанию)
    DOCUMENT_CACHE_TTL_SECONDS: float = 300.0

    def __init__(self, db_path: Path | None = None) -> None:
        """Инициализация менеджера LanceDB.

        Args:
            db_path: Путь к базе данных (по умолчанию из settings)
        """
        self.db_path = Path(db_path or settings.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection_manager = DBConnectionManager.get_instance(self.db_path)
        # Кэш метаданных документов с TTL (v0.6.0)
        # Используем TTLCache вместо простого dict для автоматической инвалидации
        self._document_info_cache = TTLCache(
            ttl_seconds=self.DOCUMENT_CACHE_TTL_SECONDS,
            max_size=10000,
        )
        # Lazy initialization для репозиториев (v5)
        self._chunk_repository: "IChunkRepository | None" = None
        self._document_repository: "IDocumentRepository | None" = None

        # Инициализация VectorSearchService (v0.7.0 - Phase 3)
        self._normalizer = DataNormalizer()
        self._vector_search_service = VectorSearchService(
            connection_manager=self.connection_manager,
            normalizer=self._normalizer,
            cache=self._document_info_cache,
        )

        # Инициализация IndexingService (v0.7.0 - Phase 3)
        self._indexing_service = IndexingService(
            connection_manager=self.connection_manager,
        )

        # Инициализация MetadataService (v0.7.0 - Phase 3)
        self._metadata_service = MetadataService(
            connection_manager=self.connection_manager,
            document_info_cache=self._document_info_cache,
        )

    def _get_db(self) -> lancedb.DBConnection:
        """Получение подключения к БД из пула.

        Returns:
            Подключение к LanceDB из пула
        """
        return self.connection_manager.get_or_create_connection(self.db_path)
    
    @contextmanager
    def _get_db_context(self) -> Generator[lancedb.DBConnection, None, None]:
        """Получение подключения к БД через context manager (рекомендуемый способ).
        
        Yields:
            Подключение к LanceDB
            
        Note:
            Используйте этот метод для операций, которые требуют явного управления жизненным циклом соединения.
        """
        with self.connection_manager.get_connection(self.db_path) as db:
            yield db

    def _normalize_vault_name(self, vault_name: str) -> str:
        """Нормализация имени vault'а для LanceDB (alphanumeric, underscores, hyphens, periods)."""
        import re
        safe_name = re.sub(r'[^a-zA-Z0-9_\-.]', '_', vault_name)
        safe_name = re.sub(r'_+', '_', safe_name)
        return safe_name.strip('_')

    def _get_table_name(self, vault_name: str, table_type: str = "chunks") -> str:
        """Получение имени таблицы vault_{vault_name}_{table_type} с защитой от ошибок."""
        valid_types = ["chunks", "documents", "document_properties", "metadata",
                       "chunk_enrichments", "knowledge_clusters"]
        if vault_name.startswith("vault_"):
            parts = vault_name.replace("vault_", "", 1).split("_")
            vault_parts, found = [], False
            for part in parts:
                if part in valid_types:
                    found = True
                    break
                vault_parts.append(part)
            if found and vault_parts:
                vault_name = "_".join(vault_parts)
                logger.error(f"BUG: table name passed as vault_name, extracted: '{vault_name}'")
            else:
                raise ValueError(f"Invalid vault_name '{vault_name}' starts with 'vault_'")
        for t in ["chunks", "documents", "document_properties", "metadata"]:
            if vault_name.endswith(f"_{t}"):
                vault_name = vault_name[:-(len(t) + 1)]
                logger.warning(f"Extracted vault_name: '{vault_name}'")
                break
        return f"vault_{self._normalize_vault_name(vault_name)}_{table_type}"

    def _serialize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Сериализация metadata. Делегирует IndexingService."""
        return self._indexing_service._serialize_metadata(metadata)

    def _get_full_path(self, file_path: str) -> Path:
        """Получение полного пути к файлу. Делегирует IndexingService."""
        return self._indexing_service._get_full_path(file_path)

    def _detect_content_type(self, file_path: str) -> str:
        """Определение типа контента файла. Делегирует IndexingService."""
        return self._indexing_service._detect_content_type(file_path)

    def _get_file_size(self, file_path: str) -> int:
        """Получение размера файла в байтах. Делегирует IndexingService."""
        return self._indexing_service._get_file_size(file_path)

    def _normalize_property_value(self, value: Any) -> str:
        """Нормализация значения свойства. Делегирует IndexingService."""
        return self._indexing_service._normalize_property_value(value)

    def _get_property_type(self, value: Any) -> str:
        """Определение типа значения свойства. Делегирует IndexingService."""
        return self._indexing_service._get_property_type(value)

    def _compute_metadata_hash(self, metadata: dict[str, Any]) -> str:
        """Вычисление хеша метаданных. Делегирует IndexingService."""
        return self._indexing_service._compute_metadata_hash(metadata)

    def _prepare_document_record(
        self,
        chunk: DocumentChunk,
        vault_name: str,
        content_hash: str | None = None,
    ) -> dict[str, Any]:
        """Подготовка записи для таблицы documents (v4).

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return self._indexing_service._prepare_document_record(
            chunk=chunk, vault_name=vault_name, content_hash=content_hash
        )

    def _prepare_chunk_record(
        self, chunk: DocumentChunk, embedding: list[float], document_id: str
    ) -> dict[str, Any]:
        """Подготовка записи для таблицы chunks (v4).

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return self._indexing_service._prepare_chunk_record(
            chunk=chunk, embedding=embedding, document_id=document_id
        )

    def _extract_properties(
        self, chunk: DocumentChunk, document_id: str, vault_name: str
    ) -> list[dict[str, Any]]:
        """Извлечение свойств из frontmatter для таблицы properties (v4).

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return self._indexing_service._extract_properties(
            chunk=chunk, document_id=document_id, vault_name=vault_name
        )

    def _prepare_metadata_record(
        self, chunk: DocumentChunk, vault_name: str
    ) -> dict[str, Any]:
        """Подготовка записи для таблицы metadata (v4).

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return self._indexing_service._prepare_metadata_record(
            chunk=chunk, vault_name=vault_name
        )

    def _dict_to_search_result(self, row: dict[str, Any], score: float) -> SearchResult:
        """Конвертация строки из БД в SearchResult.

        Делегирует VectorSearchService (v0.7.0 - Phase 3).
        """
        return self._vector_search_service._dict_to_search_result(row=row, score=score)

    async def _ensure_table(
        self, vault_name: str, table_type: str = "chunks"
    ) -> lancedb.table.Table:
        """Создание или получение таблицы для vault'а (v4).

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return await self._indexing_service._ensure_table(
            vault_name=vault_name, table_type=table_type
        )

    async def upsert_chunks(
        self,
        vault_name: str,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Добавление или обновление чанков в БД. Делегирует IndexingService."""
        return await self._indexing_service.upsert_chunks(
            vault_name=vault_name, chunks=chunks, embeddings=embeddings
        )

    async def _get_row_count(self, table: lancedb.table.Table) -> int:
        """Получение количества строк в таблице.

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return await self._indexing_service._get_row_count(table)

    def _get_index_params(self, row_count: int) -> tuple[int, int]:
        """Вычисление оптимальных параметров индекса.

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return self._indexing_service._get_index_params(row_count)

    async def _create_vector_index(
        self, table: lancedb.table.Table, row_count: int | None = None
    ) -> None:
        """Создание IVF-PQ индекса для векторного поиска.

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return await self._indexing_service._create_vector_index(
            table=table, row_count=row_count
        )

    async def _create_fts_index(
        self, table: lancedb.table.Table, table_type: str = "chunks"
    ) -> None:
        """Создание FTS индекса для полнотекстового поиска.

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return await self._indexing_service._create_fts_index(
            table=table, table_type=table_type
        )

    async def _create_metadata_indexes(self, table: lancedb.table.Table) -> None:
        """Создание индексов для таблицы metadata.

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return await self._indexing_service._create_metadata_indexes(table=table)

    async def _create_documents_indexes(self, table: lancedb.table.Table) -> None:
        """Создание индексов для таблицы documents.

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return await self._indexing_service._create_documents_indexes(table=table)

    async def _create_properties_indexes(self, table: lancedb.table.Table) -> None:
        """Создание индексов для таблицы document_properties.

        Делегирует IndexingService (v0.7.0 - Phase 3).
        """
        return await self._indexing_service._create_properties_indexes(table=table)

    async def delete_file(self, vault_name: str, file_path: str) -> None:
        """Удаление файла из индекса. Делегирует IndexingService."""
        return await self._indexing_service.delete_file(
            vault_name=vault_name, file_path=file_path
        )

    async def get_indexed_files(self, vault_name: str) -> dict[str, datetime]:
        """Получение списка проиндексированных файлов. Делегирует IndexingService."""
        return await self._indexing_service.get_indexed_files(vault_name=vault_name)

    async def delete_vault(self, vault_name: str) -> None:
        """Удаление всех таблиц vault'а. Делегирует IndexingService."""
        return await self._indexing_service.delete_vault(vault_name=vault_name)

    async def _get_document_info_cached(
        self, vault_name: str, document_id: str
    ) -> dict[str, Any] | None:
        """Получение метаданных документа с кэшированием и TTL."""
        cache_key = f"{vault_name}::{document_id}"
        cached = self._document_info_cache.get(cache_key)
        if cached is not None:
            return None if isinstance(cached, dict) and cached.get("__not_found__") else cached
        try:
            documents_table = await self._ensure_table(vault_name, "documents")
            def _get_info() -> dict[str, Any] | None:
                try:
                    t = documents_table.search().where(f"document_id = '{document_id}'").to_arrow()
                    return {c: t[c][0].as_py() for c in t.column_names} if t.num_rows > 0 else None
                except Exception as e:
                    logger.debug(f"Error searching document info for {document_id}: {e}")
                    return None
            doc_info = await asyncio.to_thread(_get_info)
            self._document_info_cache.set(cache_key, doc_info or {"__not_found__": True})
            return doc_info
        except Exception as e:
            logger.debug(f"Error getting document info cached for {vault_name}::{document_id}: {e}")
            return None

    def invalidate_document_cache(self, vault_name: str, document_id: str | None = None) -> int:
        """Инвалидация кэша документов. Возвращает количество инвалидированных записей."""
        if document_id:
            self._document_info_cache.invalidate(f"{vault_name}::{document_id}")
            return 1
        return self._document_info_cache.invalidate_prefix(f"{vault_name}::")

    async def vector_search(
        self,
        vault_name: str,
        query_vector: list[float],
        limit: int = 10,
        where: str | None = None,
        document_ids: set[str] | None = None,
    ) -> list[SearchResult]:
        """Векторный поиск по embeddings. Делегирует VectorSearchService."""
        return await self._vector_search_service.vector_search(
            vault_name=vault_name, query_vector=query_vector, limit=limit,
            where=where, document_ids=document_ids,
        )

    async def fts_search(
        self,
        vault_name: str,
        query: str,
        limit: int = 10,
        where: str | None = None,
        document_ids: set[str] | None = None,
    ) -> list[SearchResult]:
        """Полнотекстовый поиск (BM25). Делегирует VectorSearchService."""
        async with _performance_monitor.measure("fts_search"):
            return await self._vector_search_service.fts_search(
                vault_name=vault_name, query=query, limit=limit,
                where=where, document_ids=document_ids,
            )

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
        """Гибридный поиск (векторный + FTS). Делегирует VectorSearchService."""
        async with _performance_monitor.measure("hybrid_search"):
            return await self._vector_search_service.hybrid_search(
                vault_name=vault_name, query_vector=query_vector,
                query_text=query_text, limit=limit, alpha=alpha,
                where=where, document_ids=document_ids,
            )

    async def get_all_links(self, vault_name: str) -> list[str]:
        """Получение всех уникальных ссылок. Делегирует MetadataService."""
        return await self._metadata_service.get_all_links(vault_name=vault_name)

    async def get_all_tags(
        self, vault_name: str, tag_type: str = "frontmatter"
    ) -> list[str]:
        """Получение всех уникальных тегов. Делегирует MetadataService."""
        return await self._metadata_service.get_all_tags(
            vault_name=vault_name, tag_type=tag_type
        )

    async def get_vault_stats(self, vault_name: str) -> VaultStats:
        """Получение статистики vault'а. Делегирует MetadataService."""
        return await self._metadata_service.get_vault_stats(vault_name=vault_name)

    async def list_vaults(self) -> list[str]:
        """Получение списка всех vault'ов. Делегирует MetadataService."""
        return await self._metadata_service.list_vaults()

    async def search_by_links(
        self, vault_name: str, link_name: str, limit: int = 10
    ) -> list[SearchResult]:
        """Поиск заметок по wikilinks. Делегирует MetadataService."""
        return await self._metadata_service.search_by_links(
            vault_name=vault_name, link_name=link_name, limit=limit
        )

    async def get_documents_by_property(
        self,
        vault_name: str,
        property_key: str,
        property_value: str | None = None,
        property_value_pattern: str | None = None,
    ) -> set[str]:
        """Получение документов по свойству. Делегирует MetadataService."""
        return await self._metadata_service.get_documents_by_property(
            vault_name=vault_name, property_key=property_key,
            property_value=property_value, property_value_pattern=property_value_pattern,
        )

    async def get_document_properties(
        self, vault_name: str, document_id: str
    ) -> dict[str, str]:
        """Получение всех свойств документа. Делегирует MetadataService."""
        return await self._metadata_service.get_document_properties(
            vault_name=vault_name, document_id=document_id
        )

    async def get_document_info(
        self, vault_name: str, document_id: str
    ) -> DocumentInfo | None:
        """Получение метаданных документа. Делегирует MetadataService."""
        return await self._metadata_service.get_document_info(
            vault_name=vault_name, document_id=document_id
        )

    async def get_documents_by_tags(
        self, vault_name: str, tags: list[str], match_all: bool = True
    ) -> set[str]:
        """Получение документов по тегам. Делегирует MetadataService."""
        return await self._metadata_service.get_documents_by_tags(
            vault_name=vault_name, tags=tags, match_all=match_all
        )

    # ============================================================================
    # Репозитории (v5) - lazy initialization
    # ============================================================================

    @property
    def chunks(self) -> "IChunkRepository":
        """Репозиторий чанков (lazy initialization)."""
        if self._chunk_repository is None:
            from obsidian_kb.storage.chunk_repository import ChunkRepository
            self._chunk_repository = ChunkRepository(self)
        return self._chunk_repository

    @property
    def documents(self) -> "IDocumentRepository":
        """Репозиторий документов (lazy initialization)."""
        if self._document_repository is None:
            from obsidian_kb.storage.document_repository import DocumentRepository
            self._document_repository = DocumentRepository(self)
        return self._document_repository

