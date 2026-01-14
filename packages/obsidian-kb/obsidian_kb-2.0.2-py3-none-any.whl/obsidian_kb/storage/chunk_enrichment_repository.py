"""Репозиторий для работы с обогащенными данными чанков."""

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from obsidian_kb.types import ChunkEnrichment

if TYPE_CHECKING:
    from obsidian_kb.lance_db import LanceDBManager

logger = logging.getLogger(__name__)


class ChunkEnrichmentRepository:
    """Реализация IChunkEnrichmentRepository для работы с обогащенными данными чанков."""

    def __init__(self, db_manager: "LanceDBManager") -> None:
        """Инициализация репозитория.
        
        Args:
            db_manager: Экземпляр LanceDBManager
        """
        self._db_manager = db_manager

    async def upsert(
        self,
        vault_name: str,
        enrichments: list[ChunkEnrichment],
    ) -> None:
        """Сохранение обогащенных данных.
        
        Args:
            vault_name: Имя vault'а
            enrichments: Список обогащенных данных
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        if not enrichments:
            return
        
        try:
            table = await self._db_manager._ensure_table(vault_name, "chunk_enrichments")
            
            def _upsert_operation() -> None:
                try:
                    # Конвертируем ChunkEnrichment в словари для PyArrow
                    records = []
                    for enrichment in enrichments:
                        record = {
                            "chunk_id": enrichment.chunk_id,
                            "vault_name": enrichment.vault_name,
                            "summary": enrichment.summary,
                            "key_concepts": enrichment.key_concepts,
                            "semantic_tags": enrichment.semantic_tags,
                            "enriched_at": enrichment.enriched_at.isoformat(),
                            "content_hash": enrichment.content_hash,
                        }
                        records.append(record)
                    
                    # Создаем PyArrow таблицу
                    import pyarrow as pa
                    from obsidian_kb.schema_migrations import get_chunk_enrichments_schema
                    
                    schema = get_chunk_enrichments_schema()
                    arrow_table = pa.Table.from_pylist(records, schema=schema)
                    
                    # Upsert в таблицу
                    table.merge_insert(
                        ["chunk_id"],  # on - ключ для merge
                    ).when_matched_update_all().when_not_matched_insert_all().execute(arrow_table)
                    
                except Exception as e:
                    logger.error(f"Error upserting enrichments: {e}")
                    raise
            
            await asyncio.to_thread(_upsert_operation)
            logger.debug(f"Upserted {len(enrichments)} enrichments for vault '{vault_name}'")
            
        except Exception as e:
            logger.error(f"Error in upsert for vault '{vault_name}': {e}")
            from obsidian_kb.types import DatabaseError
            raise DatabaseError(f"Failed to upsert enrichments: {e}", vault_name=vault_name)

    async def get(
        self,
        vault_name: str,
        chunk_id: str,
    ) -> ChunkEnrichment | None:
        """Получение обогащения для чанка.
        
        Args:
            vault_name: Имя vault'а
            chunk_id: ID чанка
            
        Returns:
            Обогащение чанка или None если не найдено
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        try:
            table = await self._db_manager._ensure_table(vault_name, "chunk_enrichments")
            
            def _get_operation() -> dict[str, Any] | None:
                try:
                    arrow_table = (
                        table.search()
                        .where(f"chunk_id = '{chunk_id}' AND vault_name = '{vault_name}'")
                        .to_arrow()
                    )
                    
                    if arrow_table.num_rows == 0:
                        return None
                    
                    # Берем первую строку
                    row = {col: arrow_table[col][0].as_py() for col in arrow_table.column_names}
                    return row
                    
                except Exception as e:
                    logger.error(f"Error getting enrichment for chunk {chunk_id}: {e}")
                    return None
            
            row = await asyncio.to_thread(_get_operation)
            if not row:
                return None
            
            return self._row_to_enrichment(row)
            
        except Exception as e:
            logger.error(f"Error in get for vault '{vault_name}', chunk '{chunk_id}': {e}")
            return None

    async def get_many(
        self,
        vault_name: str,
        chunk_ids: list[str],
    ) -> dict[str, ChunkEnrichment]:
        """Получение обогащений для нескольких чанков.
        
        Args:
            vault_name: Имя vault'а
            chunk_ids: Список ID чанков
            
        Returns:
            Словарь {chunk_id: ChunkEnrichment}
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        if not chunk_ids:
            return {}
        
        try:
            table = await self._db_manager._ensure_table(vault_name, "chunk_enrichments")
            
            def _get_many_operation() -> dict[str, ChunkEnrichment]:
                try:
                    # Создаем условие для поиска нескольких chunk_id
                    chunk_ids_str = "', '".join(chunk_id.replace("'", "''") for chunk_id in chunk_ids)
                    where_clause = f"vault_name = '{vault_name}' AND chunk_id IN ('{chunk_ids_str}')"

                    arrow_table = (
                        table.search()
                        .where(where_clause)
                        .to_arrow()
                    )
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    rows = arrow_table.to_pylist()
                    enrichments = {}
                    for row in rows:
                        enrichment = self._row_to_enrichment(row)
                        enrichments[enrichment.chunk_id] = enrichment
                    return enrichments

                except Exception as e:
                    logger.error(f"Error getting many enrichments: {e}")
                    return {}
            
            return await asyncio.to_thread(_get_many_operation)
            
        except Exception as e:
            logger.error(f"Error in get_many for vault '{vault_name}': {e}")
            return {}

    async def delete_by_chunk(
        self,
        vault_name: str,
        chunk_id: str,
    ) -> None:
        """Удаление обогащения для чанка.
        
        Args:
            vault_name: Имя vault'а
            chunk_id: ID чанка
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        try:
            table = await self._db_manager._ensure_table(vault_name, "chunk_enrichments")
            
            def _delete_operation() -> None:
                try:
                    table.delete(f"chunk_id = '{chunk_id}' AND vault_name = '{vault_name}'")
                except Exception as e:
                    logger.error(f"Error deleting enrichment for chunk {chunk_id}: {e}")
                    raise
            
            await asyncio.to_thread(_delete_operation)
            logger.debug(f"Deleted enrichment for chunk '{chunk_id}' in vault '{vault_name}'")
            
        except Exception as e:
            logger.error(f"Error in delete_by_chunk for vault '{vault_name}', chunk '{chunk_id}': {e}")
            from obsidian_kb.types import DatabaseError
            raise DatabaseError(f"Failed to delete enrichment: {e}", vault_name=vault_name)

    async def delete_by_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> None:
        """Удаление всех обогащений документа.
        
        Args:
            vault_name: Имя vault'а
            document_id: ID документа
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        try:
            table = await self._db_manager._ensure_table(vault_name, "chunk_enrichments")
            
            def _delete_operation() -> None:
                try:
                    # Удаляем все обогащения, где chunk_id начинается с document_id::
                    # chunk_id имеет формат: vault_name::file_path::chunk_index
                    # document_id имеет формат: vault_name::file_path
                    where_clause = f"vault_name = '{vault_name}' AND chunk_id LIKE '{document_id}::%'"
                    table.delete(where_clause)
                except Exception as e:
                    logger.error(f"Error deleting enrichments for document {document_id}: {e}")
                    raise
            
            await asyncio.to_thread(_delete_operation)
            logger.debug(f"Deleted enrichments for document '{document_id}' in vault '{vault_name}'")
            
        except Exception as e:
            logger.error(f"Error in delete_by_document for vault '{vault_name}', document '{document_id}': {e}")
            from obsidian_kb.types import DatabaseError
            raise DatabaseError(f"Failed to delete enrichments: {e}", vault_name=vault_name)

    async def search(
        self,
        vault_name: str,
        query: str,
        limit: int = 10,
    ) -> list[ChunkEnrichment]:
        """Поиск по обогащенным данным (summary, key_concepts).
        
        Args:
            vault_name: Имя vault'а
            query: Поисковый запрос
            limit: Максимум результатов
            
        Returns:
            Список найденных обогащений
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        try:
            table = await self._db_manager._ensure_table(vault_name, "chunk_enrichments")
            
            def _search_operation() -> list[ChunkEnrichment]:
                try:
                    # Используем FTS поиск по summary и key_concepts
                    # LanceDB поддерживает FTS через search() с текстовым запросом
                    arrow_table = (
                        table.search(query=query)
                        .where(f"vault_name = '{vault_name}'")
                        .limit(limit)
                        .to_arrow()
                    )
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    rows = arrow_table.to_pylist()
                    return [self._row_to_enrichment(row) for row in rows]

                except Exception as e:
                    logger.error(f"Error searching enrichments: {e}")
                    return []
            
            return await asyncio.to_thread(_search_operation)
            
        except Exception as e:
            logger.error(f"Error in search for vault '{vault_name}': {e}")
            return []

    def _row_to_enrichment(self, row: dict[str, Any]) -> ChunkEnrichment:
        """Конвертация строки из БД в ChunkEnrichment."""
        # Парсим datetime из ISO строки
        enriched_at_str = row.get("enriched_at", "")
        try:
            enriched_at = datetime.fromisoformat(enriched_at_str)
        except (ValueError, TypeError):
            enriched_at = datetime.now()
        
        return ChunkEnrichment(
            chunk_id=row.get("chunk_id", ""),
            vault_name=row.get("vault_name", ""),
            summary=row.get("summary", ""),
            key_concepts=row.get("key_concepts", []),
            semantic_tags=row.get("semantic_tags", []),
            enriched_at=enriched_at,
            content_hash=row.get("content_hash", ""),
        )

