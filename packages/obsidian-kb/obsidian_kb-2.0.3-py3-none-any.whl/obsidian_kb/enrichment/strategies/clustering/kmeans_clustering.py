"""K-means стратегия кластеризации документов."""

import logging
from typing import Any

import numpy as np

from obsidian_kb.enrichment.strategies.clustering.clustering_strategy import ClusteringStrategy

logger = logging.getLogger(__name__)


class KMeansClusteringStrategy:
    """K-means стратегия кластеризации документов.
    
    Использует алгоритм K-means для группировки документов по семантической близости.
    Поддерживает автоматическое определение количества кластеров через elbow method.
    """
    
    def __init__(
        self,
        max_iterations: int = 100,
        tolerance: float = 1e-4,
        random_state: int | None = None,
    ) -> None:
        """Инициализация стратегии.
        
        Args:
            max_iterations: Максимальное количество итераций K-means
            tolerance: Порог сходимости (изменение центроидов)
            random_state: Seed для генератора случайных чисел (для воспроизводимости)
        """
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.random_state = random_state
    
    async def cluster(
        self,
        document_vectors: list[tuple[str, list[float]]],
        n_clusters: int | None = None,
    ) -> list[dict[str, Any]]:
        """Кластеризация документов через K-means.
        
        Args:
            document_vectors: Список кортежей (document_id, embedding_vector)
            n_clusters: Количество кластеров (None для автоматического определения)
            
        Returns:
            Список словарей с кластерами
        """
        if not document_vectors:
            return []
        
        if len(document_vectors) < 2:
            # Недостаточно документов для кластеризации
            doc_id, vector = document_vectors[0]
            return [{
                "cluster_id": "cluster_0",
                "document_ids": [doc_id],
                "centroid_vector": vector,
            }]
        
        # Конвертируем в numpy массив
        doc_ids = [doc_id for doc_id, _ in document_vectors]
        vectors = np.array([vector for _, vector in document_vectors])
        
        # Определяем количество кластеров
        if n_clusters is None:
            n_clusters = self._determine_optimal_clusters(vectors)
        
        # Ограничиваем количество кластеров количеством документов
        n_clusters = min(n_clusters, len(document_vectors))
        
        if n_clusters < 1:
            n_clusters = 1
        
        logger.info(f"Clustering {len(document_vectors)} documents into {n_clusters} clusters")
        
        # Выполняем K-means кластеризацию
        centroids, labels = self._kmeans(vectors, n_clusters)
        
        # Группируем документы по кластерам
        clusters: dict[int, list[str]] = {}
        for idx, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(doc_ids[idx])
        
        # Формируем результат
        result = []
        for cluster_idx, doc_ids_in_cluster in clusters.items():
            result.append({
                "cluster_id": f"cluster_{cluster_idx}",
                "document_ids": doc_ids_in_cluster,
                "centroid_vector": centroids[cluster_idx].tolist(),
            })
        
        logger.info(f"Created {len(result)} clusters")
        return result
    
    def _determine_optimal_clusters(self, vectors: np.ndarray) -> int:
        """Определение оптимального количества кластеров через elbow method.
        
        Args:
            vectors: Массив векторов документов
            
        Returns:
            Оптимальное количество кластеров
        """
        n_samples = len(vectors)
        
        # Для небольших vault'ов (< 50 документов): фиксированное количество
        if n_samples < 50:
            return min(5, max(2, n_samples // 10))
        
        # Для средних vault'ов (50-200 документов): elbow method
        if n_samples < 200:
            max_k = min(15, n_samples // 3)
            return self._elbow_method(vectors, max_k=max_k)
        
        # Для больших vault'ов (> 200 документов): автоматическое определение
        max_k = min(20, n_samples // 10)
        return self._elbow_method(vectors, max_k=max_k)
    
    def _elbow_method(self, vectors: np.ndarray, max_k: int = 15) -> int:
        """Elbow method для определения оптимального количества кластеров.
        
        Args:
            vectors: Массив векторов
            max_k: Максимальное количество кластеров для проверки
            
        Returns:
            Оптимальное количество кластеров
        """
        if len(vectors) < 3:
            return 1
        
        max_k = min(max_k, len(vectors) - 1)
        if max_k < 2:
            return 2
        
        # Вычисляем within-cluster sum of squares (WCSS) для разных k
        wcss = []
        k_values = range(2, max_k + 1)
        
        for k in k_values:
            _, labels = self._kmeans(vectors, k)
            wcss_value = self._compute_wcss(vectors, labels, k)
            wcss.append(wcss_value)
        
        # Находим "локоть" - точку максимального изгиба
        if len(wcss) < 2:
            return 2
        
        # Вычисляем разности (производную)
        diffs = [wcss[i] - wcss[i + 1] for i in range(len(wcss) - 1)]
        if not diffs:
            return 2
        
        # Находим максимальное уменьшение (локоть)
        max_diff_idx = max(range(len(diffs)), key=lambda i: diffs[i])
        optimal_k = k_values[max_diff_idx]
        
        return optimal_k
    
    def _compute_wcss(self, vectors: np.ndarray, labels: np.ndarray, k: int) -> float:
        """Вычисление within-cluster sum of squares.
        
        Args:
            vectors: Массив векторов
            labels: Метки кластеров
            k: Количество кластеров
            
        Returns:
            WCSS значение
        """
        wcss = 0.0
        for cluster_idx in range(k):
            cluster_vectors = vectors[labels == cluster_idx]
            if len(cluster_vectors) == 0:
                continue
            centroid = cluster_vectors.mean(axis=0)
            wcss += np.sum((cluster_vectors - centroid) ** 2)
        return float(wcss)
    
    def _kmeans(
        self,
        vectors: np.ndarray,
        n_clusters: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Реализация K-means алгоритма.
        
        Args:
            vectors: Массив векторов для кластеризации
            n_clusters: Количество кластеров
            
        Returns:
            Кортеж (centroids, labels) где:
            - centroids: массив центроидов кластеров
            - labels: массив меток кластеров для каждого вектора
        """
        n_samples, n_features = vectors.shape
        
        # Инициализация центроидов случайным образом
        rng = np.random.default_rng(self.random_state)
        centroids = vectors[rng.choice(n_samples, n_clusters, replace=False)]
        
        labels = np.zeros(n_samples, dtype=int)
        
        for iteration in range(self.max_iterations):
            # Назначение точек ближайшим центроидам
            distances = np.sqrt(((vectors - centroids[:, np.newaxis]) ** 2).sum(axis=2))
            new_labels = np.argmin(distances, axis=0)
            
            # Проверка сходимости
            if np.array_equal(labels, new_labels):
                break
            
            labels = new_labels
            
            # Обновление центроидов
            for cluster_idx in range(n_clusters):
                cluster_vectors = vectors[labels == cluster_idx]
                if len(cluster_vectors) > 0:
                    centroids[cluster_idx] = cluster_vectors.mean(axis=0)
            
            # Проверка изменения центроидов
            if iteration > 0:
                centroid_change = np.max(np.abs(centroids - centroids_prev))
                if centroid_change < self.tolerance:
                    break
            
            centroids_prev = centroids.copy()
        
        return centroids, labels

