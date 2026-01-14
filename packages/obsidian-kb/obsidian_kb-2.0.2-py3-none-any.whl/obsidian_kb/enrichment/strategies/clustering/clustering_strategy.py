"""Базовый интерфейс стратегии кластеризации."""

from typing import Any, Protocol


class ClusteringStrategy(Protocol):
    """Базовый интерфейс стратегии кластеризации документов.
    
    Стратегии кластеризации используются для группировки документов
    по семантической близости на основе их векторных представлений.
    """
    
    async def cluster(
        self,
        document_vectors: list[tuple[str, list[float]]],  # (document_id, embedding)
        n_clusters: int | None = None,
    ) -> list[dict[str, Any]]:
        """Кластеризация документов по их векторным представлениям.
        
        Args:
            document_vectors: Список кортежей (document_id, embedding_vector)
            n_clusters: Количество кластеров (None для автоматического определения)
            
        Returns:
            Список словарей с ключами:
            - cluster_id: str - уникальный ID кластера
            - document_ids: list[str] - ID документов в кластере
            - centroid_vector: list[float] | None - центроид кластера (опционально)
        """
        ...

