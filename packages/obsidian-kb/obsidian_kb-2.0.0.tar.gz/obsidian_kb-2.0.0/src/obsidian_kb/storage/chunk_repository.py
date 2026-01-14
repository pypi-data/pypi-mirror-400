"""Репозиторий для работы с чанками."""

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from obsidian_kb.types import Chunk, ChunkSearchResult, MatchType, RelevanceScore, SearchResult

if TYPE_CHECKING:
    from obsidian_kb.lance_db import LanceDBManager

logger = logging.getLogger(__name__)


class ChunkRepository:
    """Реализация IChunkRepository для работы с чанками."""

    def __init__(self, db_manager: "LanceDBManager") -> None:
        """Инициализация репозитория.
        
        Args:
            db_manager: Экземпляр LanceDBManager
        """
        self._db_manager = db_manager

    async def upsert(
        self,
        vault_name: str,
        chunks: list[Chunk],
    ) -> None:
        """Сохранение/обновление чанков.
        
        Примечание: Этот метод не используется напрямую, так как индексация
        происходит через DocumentChunk. Оставлен для совместимости с интерфейсом.
        """
        # Конвертация Chunk в DocumentChunk не требуется для текущей архитектуры
        # Индексация происходит через VaultIndexer -> LanceDBManager.upsert_chunks()
        logger.warning("ChunkRepository.upsert() called but indexing should use LanceDBManager.upsert_chunks()")

    async def delete_by_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> int:
        """Удаление всех чанков документа.
        
        Returns:
            Количество удалённых чанков
        """
        # Получаем количество чанков ДО удаления
        chunks = await self.get_by_document(vault_name, document_id)
        count = len(chunks)
        
        # Используем метод LanceDBManager для удаления файла
        # Это удалит все чанки документа из всех таблиц
        file_path = document_id.split("::", 1)[1] if "::" in document_id else document_id
        await self._db_manager.delete_file(vault_name, file_path)
        
        return count

    async def get_by_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> list[Chunk]:
        """Получение всех чанков документа, отсортированных по chunk_index."""
        try:
            chunks_table = await self._db_manager._ensure_table(vault_name, "chunks")
            db = self._db_manager._get_db()
            
            def _get_chunks() -> list[dict[str, Any]]:
                try:
                    arrow_table = (
                        chunks_table.search()
                        .where(f"document_id = '{document_id}'")
                        .to_arrow()
                    )
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    return arrow_table.to_pylist()
                except Exception as e:
                    logger.error(f"Error getting chunks for document {document_id}: {e}")
                    return []
            
            rows = await asyncio.to_thread(_get_chunks)
            
            # Конвертируем в Chunk и сортируем по chunk_index
            chunks = []
            for row in rows:
                chunk = self._row_to_chunk(row)
                chunks.append(chunk)
            
            chunks.sort(key=lambda c: c.chunk_index)
            return chunks
            
        except Exception as e:
            logger.error(f"Error in get_by_document for vault '{vault_name}', document '{document_id}': {e}")
            return []

    async def vector_search(
        self,
        vault_name: str,
        query_vector: list[float],
        limit: int = 10,
        filter_document_ids: set[str] | None = None,
        where: str | None = None,
    ) -> list[ChunkSearchResult]:
        """Векторный поиск по чанкам."""
        # Используем метод LanceDBManager
        search_results = await self._db_manager.vector_search(
            vault_name=vault_name,
            query_vector=query_vector,
            limit=limit,
            where=where,
            document_ids=filter_document_ids,
        )
        
        # Конвертируем SearchResult в ChunkSearchResult
        return [self._search_result_to_chunk_result(sr) for sr in search_results]

    async def fts_search(
        self,
        vault_name: str,
        query: str,
        limit: int = 10,
        filter_document_ids: set[str] | None = None,
        where: str | None = None,
    ) -> list[ChunkSearchResult]:
        """Полнотекстовый поиск по чанкам."""
        # Используем метод LanceDBManager
        search_results = await self._db_manager.fts_search(
            vault_name=vault_name,
            query=query,
            limit=limit,
            where=where,
            document_ids=filter_document_ids,
        )
        
        # Конвертируем SearchResult в ChunkSearchResult
        return [self._search_result_to_chunk_result(sr, match_type=MatchType.KEYWORD) for sr in search_results]

    def _row_to_chunk(self, row: dict[str, Any]) -> Chunk:
        """Конвертация строки из БД в Chunk."""
        return Chunk(
            chunk_id=row.get("chunk_id", ""),
            document_id=row.get("document_id", ""),
            vault_name=row.get("vault_name", ""),
            chunk_index=row.get("chunk_index", 0),
            section=row.get("section", ""),
            content=row.get("content", ""),
            vector=row.get("vector"),
            inline_tags=row.get("inline_tags", []),
            links=row.get("links", []),
        )

    def _search_result_to_chunk_result(
        self,
        search_result: SearchResult,
        match_type: MatchType = MatchType.SEMANTIC,
    ) -> ChunkSearchResult:
        """Конвертация SearchResult в ChunkSearchResult."""
        # Извлекаем chunk_index из chunk_id (формат: vault::file::index)
        chunk_index = 0
        try:
            parts = search_result.chunk_id.split("::")
            if len(parts) >= 3:
                chunk_index = int(parts[-1])
        except (ValueError, IndexError) as e:
            logger.debug(f"Could not extract chunk_index from chunk_id '{search_result.chunk_id}': {e}")
        
        # Извлекаем document_id из chunk_id (первые две части)
        document_id = "::".join(search_result.chunk_id.split("::")[:-1]) if "::" in search_result.chunk_id else search_result.chunk_id
        
        chunk = Chunk(
            chunk_id=search_result.chunk_id,
            document_id=document_id,
            vault_name=search_result.vault_name,
            chunk_index=chunk_index,
            section=search_result.section,
            content=search_result.content,
            vector=None,  # Вектор не возвращается в SearchResult
            inline_tags=search_result.tags,  # В SearchResult tags это inline_tags
            links=[],  # Links не сохраняются в SearchResult
        )
        
        score = RelevanceScore(
            value=search_result.score,
            match_type=match_type,
            confidence=1.0,
        )
        
        return ChunkSearchResult(chunk=chunk, score=score)

