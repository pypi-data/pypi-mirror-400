"""Сервис работы с метаданными документов.

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
from obsidian_kb.schema_migrations import get_schema_for_table_type
from obsidian_kb.types import (
    DatabaseError,
    DocumentInfo,
    SearchResult,
    VaultNotFoundError,
    VaultStats,
)

if TYPE_CHECKING:
    from obsidian_kb.core.connection_manager import DBConnectionManager
    from obsidian_kb.core.ttl_cache import TTLCache

logger = logging.getLogger(__name__)


class MetadataService:
    """Сервис работы с метаданными документов и vault'ов.

    Отвечает за:
    - Получение всех ссылок и тегов
    - Получение статистики vault'а
    - Работа со свойствами документов
    - Поиск по ссылкам и тегам
    - Получение информации о документах
    """

    def __init__(
        self,
        connection_manager: "DBConnectionManager",
        document_info_cache: "TTLCache | None" = None,
    ) -> None:
        """Инициализация сервиса метаданных.

        Args:
            connection_manager: Менеджер подключений к БД
            document_info_cache: Кэш метаданных документов (опционально)
        """
        self._connection_manager = connection_manager
        self._document_info_cache = document_info_cache

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
        """Создание или получение таблицы для vault'а."""
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

    async def _get_document_info_cached(
        self,
        vault_name: str,
        document_id: str,
    ) -> dict[str, Any] | None:
        """Получение метаданных документа с кэшированием."""
        if self._document_info_cache is None:
            return await self._get_document_info_uncached(vault_name, document_id)

        cache_key = f"{vault_name}::{document_id}"

        cached_value = self._document_info_cache.get(cache_key)
        if cached_value is not None:
            if isinstance(cached_value, dict) and cached_value.get("__not_found__"):
                return None
            return cached_value

        doc_info = await self._get_document_info_uncached(vault_name, document_id)
        self._document_info_cache.set(
            cache_key, doc_info if doc_info else {"__not_found__": True}
        )
        return doc_info

    async def _get_document_info_uncached(
        self,
        vault_name: str,
        document_id: str,
    ) -> dict[str, Any] | None:
        """Получение метаданных документа без кэширования."""
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

            return await asyncio.to_thread(_get_info)
        except Exception:
            return None

    def _dict_to_search_result(self, row: dict[str, Any], score: float) -> SearchResult:
        """Конвертация строки из БД в SearchResult."""
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

    # ============================================================
    # Методы получения метаданных
    # ============================================================

    async def get_all_links(self, vault_name: str) -> list[str]:
        """Получение всех уникальных ссылок из vault'а.

        Args:
            vault_name: Имя vault'а

        Returns:
            Список всех уникальных ссылок

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            chunks_table = await self._ensure_table(vault_name, "chunks")

            def _get_links() -> list[str]:
                try:
                    arrow_table = chunks_table.to_arrow()

                    if arrow_table.num_rows == 0:
                        return []

                    links_list = arrow_table["links"].to_pylist()
                    all_links = set()
                    for links in links_list:
                        if isinstance(links, list):
                            all_links.update(links)

                    return sorted(list(all_links))
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            return await asyncio.to_thread(_get_links)

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting all links for vault '{vault_name}': {e}")
            raise DatabaseError(f"Failed to get all links: {e}") from e

    async def get_all_tags(
        self, vault_name: str, tag_type: str = "frontmatter"
    ) -> list[str]:
        """Получение всех уникальных тегов из vault'а.

        Args:
            vault_name: Имя vault'а
            tag_type: Тип тегов - "frontmatter" или "inline"

        Returns:
            Список всех уникальных тегов

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            if tag_type == "inline":
                table = await self._ensure_table(vault_name, "chunks")
                field_name = "inline_tags"
            else:
                table = await self._ensure_table(vault_name, "metadata")
                field_name = "frontmatter_tags"

            def _get_tags() -> list[str]:
                try:
                    arrow_table = table.to_arrow()

                    if arrow_table.num_rows == 0:
                        return []

                    if field_name not in arrow_table.column_names:
                        return []

                    tags_list = arrow_table[field_name].to_pylist()
                    all_tags = set()
                    for tags in tags_list:
                        if isinstance(tags, list):
                            all_tags.update(tags)

                    return sorted(list(all_tags))
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            return await asyncio.to_thread(_get_tags)

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting all tags for vault '{vault_name}': {e}")
            raise DatabaseError(f"Failed to get all tags: {e}") from e

    async def get_vault_stats(self, vault_name: str) -> VaultStats:
        """Получение статистики vault'а.

        Args:
            vault_name: Имя vault'а

        Returns:
            Статистика vault'а

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            documents_table = await self._ensure_table(vault_name, "documents")
            chunks_table = await self._ensure_table(vault_name, "chunks")

            metadata_table = None
            try:
                metadata_table = await self._ensure_table(vault_name, "metadata")
            except Exception as e:
                logger.debug(
                    f"Metadata table not found for vault '{vault_name}': {e}"
                )

            def _get_stats() -> dict[str, Any]:
                try:
                    # Диагностика: логируем какие таблицы используются
                    logger.debug(
                        f"[STATS] vault='{vault_name}', "
                        f"documents_table='{documents_table.name}', "
                        f"chunks_table='{chunks_table.name}'"
                    )
                    documents_arrow = documents_table.to_arrow()
                    chunks_arrow = chunks_table.to_arrow()
                    logger.debug(
                        f"[STATS] Read from tables: docs={documents_arrow.num_rows}, "
                        f"chunks={chunks_arrow.num_rows}"
                    )

                    if documents_arrow.num_rows == 0:
                        return {
                            "file_count": 0,
                            "chunk_count": 0,
                            "total_size_bytes": 0,
                            "tags": [],
                            "oldest_file": None,
                            "newest_file": None,
                        }

                    file_count = documents_arrow.num_rows
                    chunk_count = chunks_arrow.num_rows

                    file_sizes = documents_arrow["file_size"].to_pylist()
                    total_size = sum(file_sizes) if file_sizes else 0

                    all_tags = set()
                    if metadata_table is not None:
                        try:
                            metadata_arrow = metadata_table.to_arrow()
                            if (
                                metadata_arrow.num_rows > 0
                                and "frontmatter_tags" in metadata_arrow.column_names
                            ):
                                tags_list = metadata_arrow[
                                    "frontmatter_tags"
                                ].to_pylist()
                                for tags in tags_list:
                                    if isinstance(tags, list):
                                        all_tags.update(tags)
                        except Exception as e:
                            logger.debug(
                                f"Could not get tags from metadata table: {e}"
                            )

                    modified_ats = documents_arrow["modified_at"].to_pylist()
                    dates = []
                    for date_str in modified_ats:
                        if date_str:
                            try:
                                dates.append(datetime.fromisoformat(date_str))
                            except (ValueError, TypeError):
                                pass

                    oldest = min(dates) if dates else None
                    newest = max(dates) if dates else None

                    return {
                        "file_count": file_count,
                        "chunk_count": chunk_count,
                        "total_size_bytes": total_size,
                        "tags": sorted(list(all_tags)),
                        "oldest_file": oldest,
                        "newest_file": newest,
                    }

                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            stats = await asyncio.to_thread(_get_stats)

            return VaultStats(
                vault_name=vault_name,
                file_count=stats["file_count"],
                chunk_count=stats["chunk_count"],
                total_size_bytes=stats["total_size_bytes"],
                tags=stats["tags"],
                oldest_file=stats["oldest_file"],
                newest_file=stats["newest_file"],
            )

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting stats for vault '{vault_name}': {e}")
            raise DatabaseError(f"Failed to get vault stats: {e}") from e

    async def list_vaults(self) -> list[str]:
        """Получение списка всех проиндексированных vault'ов.

        Returns:
            Список имён vault'ов (уникальные, без дубликатов)
        """
        try:
            db = self._get_db()

            def _list() -> list[str]:
                try:
                    result = db.list_tables()
                    if hasattr(result, "tables"):
                        table_names = result.tables
                    else:
                        table_names = result
                except AttributeError:
                    table_names = db.table_names()

                vaults_set = set()
                valid_table_types = [
                    "chunks",
                    "documents",
                    "document_properties",
                    "metadata",
                ]

                for name in table_names:
                    if not isinstance(name, str) or not name.startswith("vault_"):
                        continue

                    name_without_prefix = name[6:]

                    vault_name = None
                    for table_type in valid_table_types:
                        if name_without_prefix.endswith(f"_{table_type}"):
                            vault_name = name_without_prefix[: -(len(table_type) + 1)]
                            break

                    if vault_name is None:
                        logger.warning(f"Skipping invalid table name: {name}")
                        continue

                    vaults_set.add(vault_name)

                return sorted(list(vaults_set))

            return await asyncio.to_thread(_list)

        except Exception as e:
            logger.error(f"Error listing vaults: {e}")
            raise DatabaseError(f"Failed to list vaults: {e}") from e

    async def search_by_links(
        self,
        vault_name: str,
        link_name: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Поиск заметок, связанных с указанной заметкой через wikilinks.

        Args:
            vault_name: Имя vault'а
            link_name: Имя связанной заметки (wikilink без [[ ]])
            limit: Максимум результатов

        Returns:
            Список результатов поиска (заметки, которые ссылаются на link_name)

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            chunks_table = await self._ensure_table(vault_name, "chunks")

            def _search() -> list[dict[str, Any]]:
                try:
                    safe_link_name = link_name.replace("'", "''")
                    where_clause = f"array_contains(links, '{safe_link_name}')"
                    arrow_table = (
                        chunks_table.search(query=None)
                        .where(where_clause)
                        .limit(limit)
                        .to_arrow()
                    )
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
                enriched_results.append(self._dict_to_search_result(enriched_row, 1.0))

            return enriched_results

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in link search for vault '{vault_name}': {e}")
            raise DatabaseError(f"Failed to perform link search: {e}") from e

    async def get_documents_by_property(
        self,
        vault_name: str,
        property_key: str,
        property_value: str | None = None,
        property_value_pattern: str | None = None,
    ) -> set[str]:
        """Получение document_id документов с указанным свойством.

        Args:
            vault_name: Имя vault'а
            property_key: Ключ свойства
            property_value: Точное значение свойства
            property_value_pattern: Паттерн для поиска (LIKE)

        Returns:
            Множество document_id документов с указанным свойством

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            properties_table = await self._ensure_table(
                vault_name, "document_properties"
            )

            def _get_documents() -> set[str]:
                try:
                    where_conditions = [f"property_key = '{property_key}'"]

                    if property_value:
                        where_conditions.append(f"property_value = '{property_value}'")
                    elif property_value_pattern:
                        where_conditions.append(
                            f"property_value_raw LIKE '%{property_value_pattern}%'"
                        )

                    where_clause = " AND ".join(where_conditions)
                    arrow_table = (
                        properties_table.search().where(where_clause).to_arrow()
                    )

                    document_ids = set()
                    if arrow_table.num_rows > 0:
                        doc_ids = arrow_table["document_id"].to_pylist()
                        document_ids = set(doc_ids)

                    return document_ids
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            return await asyncio.to_thread(_get_documents)

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Error getting documents by property for vault '{vault_name}': {e}"
            )
            raise DatabaseError(f"Failed to get documents by property: {e}") from e

    async def get_document_properties(
        self,
        vault_name: str,
        document_id: str,
    ) -> dict[str, str]:
        """Получение всех свойств документа.

        Args:
            vault_name: Имя vault'а
            document_id: ID документа

        Returns:
            Словарь {property_key: property_value} всех свойств документа

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            properties_table = await self._ensure_table(
                vault_name, "document_properties"
            )

            def _get_properties() -> dict[str, str]:
                try:
                    arrow_table = (
                        properties_table.search()
                        .where(f"document_id = '{document_id}'")
                        .to_arrow()
                    )

                    properties = {}
                    if arrow_table.num_rows > 0:
                        keys = arrow_table["property_key"].to_pylist()
                        values = arrow_table["property_value"].to_pylist()
                        properties = dict(zip(keys, values))

                    return properties
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            return await asyncio.to_thread(_get_properties)

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Error getting document properties for vault '{vault_name}': {e}"
            )
            raise DatabaseError(f"Failed to get document properties: {e}") from e

    async def get_document_info(
        self,
        vault_name: str,
        document_id: str,
    ) -> DocumentInfo | None:
        """Получение метаданных документа.

        Args:
            vault_name: Имя vault'а
            document_id: ID документа

        Returns:
            DocumentInfo или None если документ не найден

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            documents_table = await self._ensure_table(vault_name, "documents")

            def _get_info() -> DocumentInfo | None:
                try:
                    arrow_table = (
                        documents_table.search()
                        .where(f"document_id = '{document_id}'")
                        .to_arrow()
                    )

                    if arrow_table.num_rows == 0:
                        return None

                    row = {
                        col: arrow_table[col][0].as_py()
                        for col in arrow_table.column_names
                    }

                    return DocumentInfo(
                        document_id=row["document_id"],
                        vault_name=row["vault_name"],
                        file_path=row["file_path"],
                        file_path_full=row["file_path_full"],
                        file_name=row["file_name"],
                        file_extension=row["file_extension"],
                        content_type=row["content_type"],
                        title=row["title"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row.get("created_at")
                        else datetime.now(),
                        modified_at=datetime.fromisoformat(row["modified_at"]),
                        file_size=row["file_size"],
                        chunk_count=row["chunk_count"],
                    )
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            return await asyncio.to_thread(_get_info)

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting document info for vault '{vault_name}': {e}")
            raise DatabaseError(f"Failed to get document info: {e}") from e

    async def get_documents_by_tags(
        self,
        vault_name: str,
        tags: list[str],
        match_all: bool = True,
    ) -> set[str]:
        """Получение document_id документов с указанными frontmatter тегами.

        Args:
            vault_name: Имя vault'а
            tags: Список тегов для поиска
            match_all: Если True, документ должен содержать все теги (AND).
                      Если False, документ должен содержать хотя бы один тег (OR).

        Returns:
            Множество document_id документов с указанными тегами

        Raises:
            VaultNotFoundError: Если vault не найден
            DatabaseError: При ошибке работы с БД
        """
        try:
            metadata_table = await self._ensure_table(vault_name, "metadata")

            from obsidian_kb.normalization import DataNormalizer

            normalized_tags = DataNormalizer.normalize_tags(tags)
            if not normalized_tags:
                return set()

            def _get_documents() -> set[str]:
                try:
                    conditions = []
                    for tag in normalized_tags:
                        safe_tag = DataNormalizer.escape_sql_string(tag)
                        conditions.append(
                            f"array_contains(frontmatter_tags, '{safe_tag}')"
                        )

                    if match_all:
                        where_clause = " AND ".join(conditions)
                    else:
                        where_clause = " OR ".join(conditions)

                    arrow_table = (
                        metadata_table.search().where(where_clause).to_arrow()
                    )

                    document_ids = set()
                    if arrow_table.num_rows > 0:
                        doc_ids = arrow_table["document_id"].to_pylist()
                        document_ids = set(doc_ids)

                    return document_ids
                except ValueError as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise
                except Exception as e:
                    if "was not found" in str(e) or "does not exist" in str(e).lower():
                        raise VaultNotFoundError(vault_name) from e
                    raise

            return await asyncio.to_thread(_get_documents)

        except VaultNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Error getting documents by tags for vault '{vault_name}': {e}"
            )
            raise DatabaseError(f"Failed to get documents by tags: {e}") from e
