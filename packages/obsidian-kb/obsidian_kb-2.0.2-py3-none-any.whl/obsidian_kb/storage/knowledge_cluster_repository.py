"""Репозиторий для работы с кластерами знаний."""

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from obsidian_kb.types import KnowledgeCluster

if TYPE_CHECKING:
    from obsidian_kb.lance_db import LanceDBManager

logger = logging.getLogger(__name__)


class KnowledgeClusterRepository:
    """Реализация IKnowledgeClusterRepository для работы с кластерами знаний."""

    def __init__(self, db_manager: "LanceDBManager") -> None:
        """Инициализация репозитория.
        
        Args:
            db_manager: Экземпляр LanceDBManager
        """
        self._db_manager = db_manager

    async def upsert(
        self,
        vault_name: str,
        clusters: list[KnowledgeCluster],
    ) -> None:
        """Сохранение кластеров.
        
        Args:
            vault_name: Имя vault'а
            clusters: Список кластеров
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        if not clusters:
            return
        
        try:
            table = await self._db_manager._ensure_table(vault_name, "knowledge_clusters")
            
            def _upsert_operation() -> None:
                try:
                    # Конвертируем KnowledgeCluster в словари для PyArrow
                    records = []
                    for cluster in clusters:
                        record = {
                            "cluster_id": cluster.cluster_id,
                            "vault_name": cluster.vault_name,
                            "cluster_name": cluster.cluster_name,
                            "description": cluster.description,
                            "document_ids": cluster.document_ids,
                            "keywords": cluster.keywords,
                            "centroid_vector": cluster.centroid_vector if cluster.centroid_vector else None,
                            "created_at": cluster.created_at.isoformat(),
                            "updated_at": cluster.updated_at.isoformat(),
                        }
                        records.append(record)
                    
                    # Создаем PyArrow таблицу
                    import pyarrow as pa
                    from obsidian_kb.config import settings
                    from obsidian_kb.schema_migrations import get_knowledge_clusters_schema
                    
                    schema = get_knowledge_clusters_schema(settings.embedding_dimensions)
                    arrow_table = pa.Table.from_pylist(records, schema=schema)
                    
                    # Upsert в таблицу
                    table.merge_insert(
                        ["cluster_id"],  # on - ключ для merge
                    ).when_matched_update_all().when_not_matched_insert_all().execute(arrow_table)
                    
                except Exception as e:
                    logger.error(f"Error upserting clusters: {e}")
                    raise
            
            await asyncio.to_thread(_upsert_operation)
            logger.debug(f"Upserted {len(clusters)} clusters for vault '{vault_name}'")
            
        except Exception as e:
            logger.error(f"Error in upsert for vault '{vault_name}': {e}")
            from obsidian_kb.types import DatabaseError
            raise DatabaseError(f"Failed to upsert clusters: {e}", vault_name=vault_name)

    async def get_all(
        self,
        vault_name: str,
    ) -> list[KnowledgeCluster]:
        """Получение всех кластеров vault'а.
        
        Args:
            vault_name: Имя vault'а
            
        Returns:
            Список всех кластеров
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        try:
            table = await self._db_manager._ensure_table(vault_name, "knowledge_clusters")
            
            def _get_all_operation() -> list[KnowledgeCluster]:
                try:
                    arrow_table = (
                        table.search()
                        .where(f"vault_name = '{vault_name}'")
                        .to_arrow()
                    )
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    rows = arrow_table.to_pylist()
                    return [self._row_to_cluster(row) for row in rows]

                except Exception as e:
                    logger.error(f"Error getting all clusters: {e}")
                    return []
            
            return await asyncio.to_thread(_get_all_operation)
            
        except Exception as e:
            logger.error(f"Error in get_all for vault '{vault_name}': {e}")
            return []

    async def get(
        self,
        vault_name: str,
        cluster_id: str,
    ) -> KnowledgeCluster | None:
        """Получение кластера по ID.
        
        Args:
            vault_name: Имя vault'а
            cluster_id: ID кластера
            
        Returns:
            Кластер или None если не найден
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        try:
            table = await self._db_manager._ensure_table(vault_name, "knowledge_clusters")
            
            def _get_operation() -> dict[str, Any] | None:
                try:
                    arrow_table = (
                        table.search()
                        .where(f"cluster_id = '{cluster_id}' AND vault_name = '{vault_name}'")
                        .to_arrow()
                    )
                    
                    if arrow_table.num_rows == 0:
                        return None
                    
                    # Берем первую строку
                    row = {col: arrow_table[col][0].as_py() for col in arrow_table.column_names}
                    return row
                    
                except Exception as e:
                    logger.error(f"Error getting cluster {cluster_id}: {e}")
                    return None
            
            row = await asyncio.to_thread(_get_operation)
            if not row:
                return None
            
            return self._row_to_cluster(row)
            
        except Exception as e:
            logger.error(f"Error in get for vault '{vault_name}', cluster '{cluster_id}': {e}")
            return None

    async def get_for_document(
        self,
        vault_name: str,
        document_id: str,
    ) -> KnowledgeCluster | None:
        """Получение кластера для документа.
        
        Args:
            vault_name: Имя vault'а
            document_id: ID документа
            
        Returns:
            Кластер документа или None если не найден
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        try:
            table = await self._db_manager._ensure_table(vault_name, "knowledge_clusters")
            
            def _get_for_document_operation() -> dict[str, Any] | None:
                try:
                    # Ищем кластер, где document_id содержится в document_ids массиве
                    # LanceDB поддерживает array_contains для поиска в массивах
                    arrow_table = (
                        table.search()
                        .where(f"vault_name = '{vault_name}' AND array_contains(document_ids, '{document_id}')")
                        .to_arrow()
                    )
                    
                    if arrow_table.num_rows == 0:
                        return None
                    
                    # Берем первую строку (документ должен быть только в одном кластере)
                    row = {col: arrow_table[col][0].as_py() for col in arrow_table.column_names}
                    return row
                    
                except Exception as e:
                    logger.error(f"Error getting cluster for document {document_id}: {e}")
                    return None
            
            row = await asyncio.to_thread(_get_for_document_operation)
            if not row:
                return None
            
            return self._row_to_cluster(row)
            
        except Exception as e:
            logger.error(f"Error in get_for_document for vault '{vault_name}', document '{document_id}': {e}")
            return None

    async def search_similar(
        self,
        vault_name: str,
        query_vector: list[float],
        limit: int = 5,
    ) -> list[KnowledgeCluster]:
        """Поиск похожих кластеров по вектору.
        
        Args:
            vault_name: Имя vault'а
            query_vector: Вектор запроса
            limit: Максимум результатов
            
        Returns:
            Список похожих кластеров
            
        Raises:
            DatabaseError: При ошибке работы с БД
        """
        try:
            table = await self._db_manager._ensure_table(vault_name, "knowledge_clusters")
            
            def _search_similar_operation() -> list[KnowledgeCluster]:
                try:
                    # Векторный поиск по centroid_vector
                    # Используем search() с вектором запроса
                    arrow_table = (
                        table.search(query_vector)
                        .where(f"vault_name = '{vault_name}'")
                        .limit(limit)
                        .to_arrow()
                    )
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    rows = arrow_table.to_pylist()
                    return [self._row_to_cluster(row) for row in rows]

                except Exception as e:
                    logger.error(f"Error searching similar clusters: {e}")
                    return []
            
            return await asyncio.to_thread(_search_similar_operation)
            
        except Exception as e:
            logger.error(f"Error in search_similar for vault '{vault_name}': {e}")
            return []

    def _row_to_cluster(self, row: dict[str, Any]) -> KnowledgeCluster:
        """Конвертация строки из БД в KnowledgeCluster."""
        # Парсим datetime из ISO строки
        created_at_str = row.get("created_at", "")
        updated_at_str = row.get("updated_at", "")
        
        try:
            created_at = datetime.fromisoformat(created_at_str)
        except (ValueError, TypeError):
            created_at = datetime.now()
        
        try:
            updated_at = datetime.fromisoformat(updated_at_str)
        except (ValueError, TypeError):
            updated_at = datetime.now()
        
        # centroid_vector может быть None
        centroid_vector = row.get("centroid_vector")
        if centroid_vector is None:
            centroid_vector = None
        elif isinstance(centroid_vector, list):
            centroid_vector = list(centroid_vector)
        else:
            centroid_vector = None
        
        return KnowledgeCluster(
            cluster_id=row.get("cluster_id", ""),
            vault_name=row.get("vault_name", ""),
            cluster_name=row.get("cluster_name", ""),
            description=row.get("description", ""),
            document_ids=row.get("document_ids", []),
            keywords=row.get("keywords", []),
            centroid_vector=centroid_vector,
            created_at=created_at,
            updated_at=updated_at,
        )

