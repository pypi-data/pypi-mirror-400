"""Сервис индексирования документов.

Вынесен из lance_db.py в рамках Phase 3 рефакторинга (v0.7.0).
"""

import asyncio
import hashlib
import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import lancedb
import lancedb.table
import pyarrow as pa

from obsidian_kb.config import settings
from obsidian_kb.core.data_normalizer import DataNormalizer
from obsidian_kb.schema_migrations import get_schema_for_table_type
from obsidian_kb.types import (
    DatabaseError,
    DocumentChunk,
    VaultNotFoundError,
)

if TYPE_CHECKING:
    from obsidian_kb.core.connection_manager import DBConnectionManager

logger = logging.getLogger(__name__)

# Порог для создания IVF-PQ индекса
IVF_PQ_THRESHOLD = 500


class IndexingService:
    """Сервис индексирования документов и управления таблицами.

    Отвечает за:
    - Добавление/обновление чанков в БД (upsert_chunks)
    - Удаление файлов из индекса
    - Получение списка проиндексированных файлов
    - Удаление vault'а
    - Создание и управление индексами (vector, FTS)
    """

    def __init__(
        self,
        connection_manager: "DBConnectionManager",
    ) -> None:
        """Инициализация сервиса индексирования.

        Args:
            connection_manager: Менеджер подключений к БД
        """
        self._connection_manager = connection_manager

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
        # Защита от передачи имени таблицы вместо vault_name
        if vault_name.startswith("vault_"):
            parts = vault_name.replace("vault_", "", 1).split("_")
            valid_table_types = [
                "chunks",
                "documents",
                "document_properties",
                "metadata",
                "chunk_enrichments",
                "knowledge_clusters",
            ]

            vault_parts = []
            found_table_type = False
            for part in parts:
                if part in valid_table_types:
                    found_table_type = True
                    break
                vault_parts.append(part)

            if found_table_type and vault_parts:
                extracted_vault_name = "_".join(vault_parts)
                logger.error(
                    f"CRITICAL BUG: vault_name '{vault_name}' is actually a table name! "
                    f"Extracted vault_name: '{extracted_vault_name}'."
                )
                vault_name = extracted_vault_name
            else:
                raise ValueError(
                    f"CRITICAL: vault_name '{vault_name}' starts with 'vault_' and cannot be "
                    f"extracted. This will cause recursive table creation."
                )

        valid_table_types = ["chunks", "documents", "document_properties", "metadata"]
        for table_type_check in valid_table_types:
            if vault_name.endswith(f"_{table_type_check}"):
                logger.error(
                    f"CRITICAL BUG: vault_name '{vault_name}' ends with table type '{table_type_check}'."
                )
                vault_name = vault_name[: -(len(table_type_check) + 1)]
                logger.warning(f"Extracted vault_name: '{vault_name}'")
                break

        safe_name = self._normalize_vault_name(vault_name)
        return f"vault_{safe_name}_{table_type}"

    async def _ensure_table(
        self, vault_name: str, table_type: str = "chunks"
    ) -> lancedb.table.Table:
        """Создание или получение таблицы для vault'а.

        Args:
            vault_name: Имя vault'а
            table_type: Тип таблицы

        Returns:
            Таблица LanceDB
        """
        table_name = self._get_table_name(vault_name, table_type)
        db = self._get_db()

        def _ensure_table_sync() -> lancedb.table.Table:
            try:
                table = db.open_table(table_name)
                schema = table.schema
                expected_schema = get_schema_for_table_type(
                    table_type, settings.embedding_dimensions
                )

                schema_match = True
                if len(schema) != len(expected_schema):
                    schema_match = False
                else:
                    expected_field_names = {field.name for field in expected_schema}
                    actual_field_names = {field.name for field in schema}
                    if expected_field_names != actual_field_names:
                        schema_match = False

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
                expected_schema = get_schema_for_table_type(
                    table_type, settings.embedding_dimensions
                )
                empty_table = pa.Table.from_pylist([], schema=expected_schema)
                return db.create_table(table_name, empty_table, mode="overwrite")

        return await asyncio.to_thread(_ensure_table_sync)

    # ============================================================
    # Методы подготовки данных
    # ============================================================

    def _serialize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Сериализация metadata с обработкой специальных типов."""
        result = {}
        for key, value in metadata.items():
            if isinstance(value, (date, datetime)):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = self._serialize_metadata(value)
            elif isinstance(value, list):
                result[key] = [
                    item.isoformat() if isinstance(item, (date, datetime)) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def _get_full_path(self, file_path: str) -> Path:
        """Получение полного пути к файлу."""
        return Path(file_path)

    def _detect_content_type(self, file_path: str) -> str:
        """Определение типа контента файла."""
        ext = Path(file_path).suffix.lower()
        if ext == ".md":
            return "markdown"
        elif ext == ".pdf":
            return "pdf"
        elif ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]:
            return "image"
        else:
            return "unknown"

    def _get_file_size(self, file_path: str) -> int:
        """Получение размера файла в байтах."""
        return 0

    def _normalize_property_value(self, value: Any) -> str:
        """Нормализация значения свойства для индексации."""
        from obsidian_kb.normalization import DataNormalizer

        if isinstance(value, str):
            return DataNormalizer.normalize_string(value)
        elif isinstance(value, (int, float)):
            return str(value).lower()
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, list):
            normalized_items = [self._normalize_property_value(item) for item in value]
            return ",".join(normalized_items)
        else:
            return str(value).lower()

    def _get_property_type(self, value: Any) -> str:
        """Определение типа значения свойства."""
        if isinstance(value, str):
            return "string"
        elif isinstance(value, bool):
            # Важно: проверка bool должна быть перед int/float,
            # т.к. bool является подклассом int в Python
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, (date, datetime)):
            return "date"
        elif isinstance(value, list):
            return "array"
        else:
            return "string"

    def _compute_metadata_hash(self, metadata: dict[str, Any]) -> str:
        """Вычисление хеша метаданных для отслеживания изменений."""
        metadata_str = json.dumps(self._serialize_metadata(metadata), sort_keys=True)
        return hashlib.sha256(metadata_str.encode()).hexdigest()

    def _compute_file_content_hash(self, file_path: str) -> str:
        """Вычисление SHA256 хеша содержимого файла."""
        try:
            full_path = self._get_full_path(file_path)
            if not full_path.exists():
                return ""

            sha256 = hashlib.sha256()
            with open(full_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)

            return sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute content hash for {file_path}: {e}")
            return ""

    def _prepare_document_record(
        self,
        chunk: DocumentChunk,
        vault_name: str,
        content_hash: str | None = None,
    ) -> dict[str, Any]:
        """Подготовка записи для таблицы documents."""
        document_id = f"{vault_name}::{chunk.file_path}"

        if content_hash is None:
            content_hash = self._compute_file_content_hash(chunk.file_path)

        return {
            "document_id": document_id,
            "vault_name": vault_name,
            "file_path": chunk.file_path,
            "file_path_full": str(self._get_full_path(chunk.file_path)),
            "file_name": Path(chunk.file_path).name,
            "file_extension": Path(chunk.file_path).suffix,
            "content_type": self._detect_content_type(chunk.file_path),
            "title": chunk.title,
            "created_at": chunk.created_at.isoformat() if chunk.created_at else "",
            "modified_at": chunk.modified_at.isoformat(),
            "file_size": self._get_file_size(chunk.file_path),
            "chunk_count": 0,
            "content_hash": content_hash,
        }

    def _prepare_chunk_record(
        self, chunk: DocumentChunk, embedding: list[float], document_id: str
    ) -> dict[str, Any]:
        """Подготовка записи для таблицы chunks."""
        chunk_index = 0
        try:
            chunk_index = int(chunk.id.split("::")[-1])
        except (ValueError, IndexError):
            pass

        return {
            "chunk_id": chunk.id,
            "document_id": document_id,
            "vault_name": chunk.vault_name,
            "chunk_index": chunk_index,
            "section": chunk.section,
            "content": chunk.content,
            "vector": embedding,
            "links": chunk.links,
            "inline_tags": chunk.inline_tags,
        }

    def _extract_properties(
        self, chunk: DocumentChunk, document_id: str, vault_name: str
    ) -> list[dict[str, Any]]:
        """Извлечение свойств из frontmatter для таблицы properties."""
        properties = []
        if isinstance(chunk.metadata, dict):
            for key, value in chunk.metadata.items():
                if key == "tags":
                    continue

                normalized_value = self._normalize_property_value(value)
                property_id = f"{document_id}::{key}"

                properties.append(
                    {
                        "property_id": property_id,
                        "document_id": document_id,
                        "vault_name": vault_name,
                        "property_key": key,
                        "property_value": normalized_value,
                        "property_value_raw": str(value),
                        "property_type": self._get_property_type(value),
                    }
                )
        return properties

    def _prepare_metadata_record(
        self, chunk: DocumentChunk, vault_name: str
    ) -> dict[str, Any]:
        """Подготовка записи для таблицы metadata."""
        document_id = f"{vault_name}::{chunk.file_path}"
        metadata_serializable = self._serialize_metadata(chunk.metadata)
        return {
            "document_id": document_id,
            "vault_name": vault_name,
            "metadata_json": json.dumps(metadata_serializable, default=str),
            "frontmatter_tags": chunk.frontmatter_tags,
            "metadata_hash": self._compute_metadata_hash(chunk.metadata),
        }

    # ============================================================
    # Методы создания индексов
    # ============================================================

    async def _get_row_count(self, table: lancedb.table.Table) -> int:
        """Получение количества строк в таблице (оптимизировано).

        Использует count_rows() вместо загрузки всей таблицы в память.
        """

        def _count() -> int:
            return table.count_rows()

        return await asyncio.to_thread(_count)

    def _get_index_params(self, row_count: int) -> tuple[int, int]:
        """Вычисление оптимальных параметров индекса."""
        if row_count < 2000:
            return (64, 8)
        elif row_count < 10000:
            return (128, 12)
        else:
            return (256, 16)

    async def _create_vector_index(
        self, table: lancedb.table.Table, row_count: int | None = None
    ) -> None:
        """Создание IVF-PQ индекса для векторного поиска."""
        try:
            if row_count is None:
                row_count = await self._get_row_count(table)

            num_partitions, num_sub_vectors = self._get_index_params(row_count)

            def _create_index() -> None:
                try:
                    table.create_index(
                        metric="cosine",
                        num_partitions=num_partitions,
                        num_sub_vectors=num_sub_vectors,
                    )
                    logger.info(
                        f"Vector index created with adaptive params: "
                        f"partitions={num_partitions}, sub_vectors={num_sub_vectors} "
                        f"(row_count={row_count})"
                    )
                except Exception as e:
                    if (
                        "already exists" not in str(e).lower()
                        and "already has" not in str(e).lower()
                    ):
                        logger.debug(f"Index creation note: {e}")

            await asyncio.to_thread(_create_index)
            logger.debug("Vector index created/updated")

        except Exception as e:
            logger.warning(f"Failed to create vector index: {e}")

    async def _create_fts_index(
        self, table: lancedb.table.Table, table_type: str = "chunks"
    ) -> None:
        """Создание FTS индекса для полнотекстового поиска."""
        try:

            def _create_index() -> None:
                try:
                    if table_type == "documents":
                        try:
                            table.create_fts_index("title", replace=True)
                            logger.debug(
                                "FTS index created on 'title' for documents table"
                            )
                        except Exception as e:
                            logger.debug(f"Could not create FTS index on 'title': {e}")
                        try:
                            table.create_fts_index("file_path", replace=True)
                            logger.debug(
                                "FTS index created on 'file_path' for documents table"
                            )
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

    async def _create_metadata_indexes(self, table: lancedb.table.Table) -> None:
        """Создание индексов для таблицы metadata."""
        try:

            def _create_indexes() -> None:
                try:
                    arrow_table = table.to_arrow()
                    if "frontmatter_tags" not in arrow_table.column_names:
                        logger.debug(
                            "frontmatter_tags column not found in metadata table"
                        )
                        return
                    logger.debug(
                        "Metadata table indexes checked (array indexes are automatic in LanceDB)"
                    )
                except Exception as e:
                    logger.debug(f"Could not check/create metadata indexes: {e}")

            await asyncio.to_thread(_create_indexes)
            logger.debug("Metadata indexes checked")

        except Exception as e:
            logger.warning(f"Failed to create metadata indexes: {e}")

    async def _create_documents_indexes(self, table: lancedb.table.Table) -> None:
        """Создание индексов для таблицы documents."""
        try:

            def _create_indexes() -> None:
                try:
                    arrow_table = table.to_arrow()
                    if (
                        "created_at" not in arrow_table.column_names
                        or "modified_at" not in arrow_table.column_names
                    ):
                        logger.debug("Date columns not found in documents table")
                        return
                    logger.debug(
                        "Documents table indexes checked (scalar indexes are automatic in LanceDB)"
                    )
                except Exception as e:
                    logger.debug(f"Could not check/create documents indexes: {e}")

            await asyncio.to_thread(_create_indexes)
            logger.debug("Documents indexes checked")

        except Exception as e:
            logger.warning(f"Failed to create documents indexes: {e}")

    async def _create_properties_indexes(self, table: lancedb.table.Table) -> None:
        """Создание индексов для таблицы document_properties."""
        try:

            def _create_indexes() -> None:
                try:
                    arrow_table = table.to_arrow()
                    if (
                        "property_key" not in arrow_table.column_names
                        or "property_value" not in arrow_table.column_names
                    ):
                        logger.debug(
                            "Property columns not found in document_properties table"
                        )
                        return
                    logger.debug(
                        "Properties table indexes checked (scalar indexes are automatic in LanceDB)"
                    )
                except Exception as e:
                    logger.debug(f"Could not check/create properties indexes: {e}")

            await asyncio.to_thread(_create_indexes)
            logger.debug("Properties indexes checked")

        except Exception as e:
            logger.warning(f"Failed to create properties indexes: {e}")

    # ============================================================
    # Основные методы индексирования
    # ============================================================

    async def upsert_chunks(
        self,
        vault_name: str,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Добавление или обновление чанков в БД.

        Записывает данные в 4 таблицы:
        - documents: метаданные файлов
        - chunks: векторизованное содержимое
        - document_properties: свойства из frontmatter
        - metadata: полный frontmatter в JSON

        Args:
            vault_name: Имя vault'а
            chunks: Список чанков
            embeddings: Список векторов (должен соответствовать chunks)

        Raises:
            DatabaseError: При ошибке работы с БД
            ValueError: Если количество chunks не равно количеству embeddings
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks count ({len(chunks)}) != embeddings count ({len(embeddings)})"
            )

        if not chunks:
            return

        # Ленивый импорт для избежания циклического импорта
        from obsidian_kb.service_container import get_service_container

        services = get_service_container()
        recovery_service = services.recovery_service

        async def _upsert_operation() -> None:
            documents_table = await self._ensure_table(vault_name, "documents")
            chunks_table = await self._ensure_table(vault_name, "chunks")
            properties_table = await self._ensure_table(
                vault_name, "document_properties"
            )
            metadata_table = await self._ensure_table(vault_name, "metadata")

            documents_data: dict[str, dict[str, Any]] = {}
            chunks_data: list[dict[str, Any]] = []
            properties_data: list[dict[str, Any]] = []
            metadata_data: dict[str, dict[str, Any]] = {}

            document_chunk_counts: dict[str, int] = {}

            for chunk, embedding in zip(chunks, embeddings):
                document_id = f"{vault_name}::{chunk.file_path}"

                if document_id not in documents_data:
                    content_hash = self._compute_file_content_hash(chunk.file_path)
                    documents_data[document_id] = self._prepare_document_record(
                        chunk, vault_name, content_hash=content_hash
                    )
                    metadata_data[document_id] = self._prepare_metadata_record(
                        chunk, vault_name
                    )
                    document_chunk_counts[document_id] = 0

                document_chunk_counts[document_id] += 1

                chunk_record = self._prepare_chunk_record(chunk, embedding, document_id)
                chunks_data.append(chunk_record)

                if document_id not in [p.get("document_id") for p in properties_data]:
                    doc_properties = self._extract_properties(
                        chunk, document_id, vault_name
                    )
                    properties_data.extend(doc_properties)

            for document_id, count in document_chunk_counts.items():
                if document_id in documents_data:
                    documents_data[document_id]["chunk_count"] = count

            def _upsert() -> None:
                for document_id in documents_data.keys():
                    # Экранируем document_id для безопасного использования в SQL-запросах
                    # Это критически важно для путей с апострофами (например "John's Notes.md")
                    escaped_doc_id = DataNormalizer.escape_sql_string(document_id)
                    chunks_table.delete(f"document_id = '{escaped_doc_id}'")
                    properties_table.delete(f"document_id = '{escaped_doc_id}'")
                    documents_table.delete(f"document_id = '{escaped_doc_id}'")
                    metadata_table.delete(f"document_id = '{escaped_doc_id}'")

                if documents_data:
                    documents_arrow = pa.Table.from_pylist(
                        list(documents_data.values())
                    )
                    documents_table.add(documents_arrow, mode="append")

                if chunks_data:
                    chunks_arrow = pa.Table.from_pylist(chunks_data)
                    chunks_table.add(chunks_arrow, mode="append")

                if properties_data:
                    properties_arrow = pa.Table.from_pylist(properties_data)
                    properties_table.add(properties_arrow, mode="append")

                if metadata_data:
                    metadata_arrow = pa.Table.from_pylist(list(metadata_data.values()))
                    metadata_table.add(metadata_arrow, mode="append")

            await asyncio.to_thread(_upsert)

            # Верификация записи - проверяем что данные действительно сохранились
            row_count = await self._get_row_count(chunks_table)
            logger.info(
                f"[VERIFY] After upsert: vault='{vault_name}', "
                f"expected={len(chunks_data)}, actual_in_table={row_count}"
            )
            if row_count == 0 and len(chunks_data) > 0:
                logger.error(
                    f"CRITICAL: Table empty after upsert! vault='{vault_name}', "
                    f"table='{chunks_table.name}', expected_chunks={len(chunks_data)}"
                )

            if row_count >= IVF_PQ_THRESHOLD:
                await self._create_vector_index(chunks_table, row_count)
            else:
                logger.debug(
                    f"Skipping vector index creation: {row_count} < {IVF_PQ_THRESHOLD}"
                )

            await self._create_fts_index(chunks_table, "chunks")

            files_changed = len(documents_data)
            if files_changed >= 50:
                logger.info(
                    f"Significant changes detected ({files_changed} files), optimizing indexes..."
                )
                try:

                    def _optimize() -> None:
                        chunks_table.optimize()

                    await asyncio.to_thread(_optimize)
                    logger.info("Indexes optimized successfully")
                except Exception as e:
                    logger.warning(f"Failed to optimize indexes: {e}")
            else:
                logger.debug(
                    f"Skipping optimize: {files_changed} files changed (< 50 threshold)"
                )

            await self._create_metadata_indexes(metadata_table)
            await self._create_documents_indexes(documents_table)
            await self._create_fts_index(documents_table, "documents")
            await self._create_properties_indexes(properties_table)

            logger.info(f"Upserted {len(chunks)} chunks for vault '{vault_name}' (v4)")

        try:
            await recovery_service.retry_with_backoff(
                _upsert_operation,
                max_retries=3,
                initial_delay=1.0,
                operation_name=f"upsert_chunks_{vault_name}",
            )
        except Exception as e:
            context = {
                "vault_name": vault_name,
                "chunks_count": len(chunks),
                "embeddings_count": len(embeddings),
            }
            logger.error(
                f"Error upserting chunks for vault '{vault_name}': {e}", extra=context
            )
            raise DatabaseError(
                f"Failed to upsert chunks: {e}", context=context
            ) from e

    async def delete_file(self, vault_name: str, file_path: str) -> None:
        """Удаление файла из индекса.

        Удаляет данные из всех 4 таблиц: documents, chunks, document_properties, metadata.

        Args:
            vault_name: Имя vault'а
            file_path: Путь к файлу (относительно vault'а)

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            document_id = f"{vault_name}::{file_path}"

            documents_table = await self._ensure_table(vault_name, "documents")
            chunks_table = await self._ensure_table(vault_name, "chunks")
            properties_table = await self._ensure_table(
                vault_name, "document_properties"
            )
            metadata_table = await self._ensure_table(vault_name, "metadata")

            def _delete() -> None:
                try:
                    # Экранируем document_id для безопасного использования в SQL-запросах
                    escaped_doc_id = DataNormalizer.escape_sql_string(document_id)
                    documents_table.delete(f"document_id = '{escaped_doc_id}'")
                    chunks_table.delete(f"document_id = '{escaped_doc_id}'")
                    properties_table.delete(f"document_id = '{escaped_doc_id}'")
                    metadata_table.delete(f"document_id = '{escaped_doc_id}'")
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            await asyncio.to_thread(_delete)
            logger.info(f"Deleted file '{file_path}' from vault '{vault_name}' (v4)")

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Error deleting file '{file_path}' from vault '{vault_name}': {e}"
            )
            raise DatabaseError(f"Failed to delete file: {e}") from e

    async def get_indexed_files(self, vault_name: str) -> dict[str, datetime]:
        """Получение списка проиндексированных файлов с временем модификации.

        Args:
            vault_name: Имя vault'а

        Returns:
            Словарь {file_path: modified_at} для всех проиндексированных файлов

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            documents_table = await self._ensure_table(vault_name, "documents")

            def _get_files() -> dict[str, datetime]:
                try:
                    arrow_table = documents_table.to_arrow()

                    if arrow_table.num_rows == 0:
                        return {}

                    file_paths = arrow_table["file_path"].to_pylist()
                    modified_ats = arrow_table["modified_at"].to_pylist()

                    file_times: dict[str, datetime] = {}
                    for file_path_item, modified_at_str in zip(
                        file_paths, modified_ats
                    ):
                        if modified_at_str:
                            try:
                                modified_at = datetime.fromisoformat(modified_at_str)
                                file_times[file_path_item] = modified_at
                            except (ValueError, TypeError):
                                pass

                    return file_times
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            return await asyncio.to_thread(_get_files)

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting indexed files for vault '{vault_name}': {e}")
            raise DatabaseError(f"Failed to get indexed files: {e}") from e

    async def delete_vault(self, vault_name: str) -> None:
        """Удаление всех таблиц vault'а.

        Удаляет все 4 таблицы: documents, chunks, document_properties, metadata.

        Args:
            vault_name: Имя vault'а

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            db = self._get_db()
            table_types = ["documents", "chunks", "document_properties", "metadata"]

            def _delete() -> None:
                try:
                    for table_type in table_types:
                        table_name = self._get_table_name(vault_name, table_type)
                        try:
                            db.drop_table(table_name)
                        except ValueError:
                            pass
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            await asyncio.to_thread(_delete)
            logger.info(f"Deleted vault '{vault_name}' (all 4 tables)")

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting vault '{vault_name}': {e}")
            raise DatabaseError(f"Failed to delete vault: {e}") from e
