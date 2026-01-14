"""Сервис кластеризации знаний."""

import asyncio
import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import ClientTimeout, TCPConnector

from obsidian_kb.config import settings
from obsidian_kb.enrichment.prompts import CLUSTER_NAMING_PROMPT, ENRICHMENT_SYSTEM_PROMPT
from obsidian_kb.enrichment.strategies.clustering.clustering_strategy import ClusteringStrategy
from obsidian_kb.providers.exceptions import ProviderConnectionError
from obsidian_kb.types import KnowledgeCluster, VaultNotFoundError

if TYPE_CHECKING:
    from obsidian_kb.interfaces import (
        IChunkRepository,
        IDocumentRepository,
        IEmbeddingService,
        IKnowledgeClusterRepository,
        ILLMEnrichmentService,
    )
    from obsidian_kb.lance_db import LanceDBManager

logger = logging.getLogger(__name__)


class KnowledgeClusterService:
    """Сервис для кластеризации документов vault'а.
    
    Реализует IKnowledgeClusterService и обеспечивает:
    - Кластеризацию документов по семантической близости
    - Генерацию названий кластеров через LLM
    - Автоматическое определение количества кластеров
    - Graceful degradation при ошибках
    """
    
    def __init__(
        self,
        db_manager: "LanceDBManager",
        embedding_service: "IEmbeddingService",
        llm_enrichment_service: "ILLMEnrichmentService",
        chunk_repository: "IChunkRepository",
        document_repository: "IDocumentRepository",
        cluster_repository: "IKnowledgeClusterRepository",
        strategy: ClusteringStrategy | None = None,
    ) -> None:
        """Инициализация сервиса кластеризации.
        
        Args:
            db_manager: Менеджер базы данных
            embedding_service: Сервис для генерации embeddings
            llm_enrichment_service: Сервис для генерации названий через LLM
            chunk_repository: Репозиторий чанков
            document_repository: Репозиторий документов
            cluster_repository: Репозиторий кластеров
            strategy: Стратегия кластеризации (по умолчанию KMeansClusteringStrategy)
        """
        self._db_manager = db_manager
        self._embedding_service = embedding_service
        self._llm_enrichment_service = llm_enrichment_service
        self._chunk_repository = chunk_repository
        self._document_repository = document_repository
        self._cluster_repository = cluster_repository
        
        # Выбор стратегии
        if strategy is None:
            from obsidian_kb.enrichment.strategies.clustering.kmeans_clustering import (
                KMeansClusteringStrategy,
            )
            strategy = KMeansClusteringStrategy()
        
        self._strategy = strategy
        
        # HTTP сессия для LLM запросов (если нужна прямая интеграция)
        self._session: aiohttp.ClientSession | None = None
        self._connector = TCPConnector(
            limit=settings.ollama_connector_limit,
            limit_per_host=settings.ollama_connector_limit_per_host,
        )
        self._timeout = ClientTimeout(total=settings.llm_timeout)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                connector=self._connector,
            )
        return self._session
    
    async def cluster_documents(
        self,
        vault_name: str,
        n_clusters: int | None = None,
        method: str = "kmeans",
    ) -> list[KnowledgeCluster]:
        """Кластеризация документов vault'а.
        
        Args:
            vault_name: Имя vault'а
            n_clusters: Количество кластеров (None для автоматического определения)
            method: Метод кластеризации ("kmeans" | "dbscan")
            
        Returns:
            Список кластеров знаний
            
        Raises:
            VaultNotFoundError: Если vault не найден
        """
        logger.info(f"Starting clustering for vault '{vault_name}'")
        
        # Получаем все документы из vault'а
        document_ids = await self._get_all_document_ids(vault_name)
        
        if not document_ids:
            logger.warning(f"No documents found in vault '{vault_name}'")
            return []
        
        logger.info(f"Found {len(document_ids)} documents in vault '{vault_name}'")
        
        # Вычисляем средние embeddings для каждого документа
        document_vectors = await self._compute_document_embeddings(vault_name, document_ids)
        
        if not document_vectors:
            logger.warning(f"No document vectors computed for vault '{vault_name}'")
            return []
        
        # Применяем кластеризацию через стратегию
        clustering_result = await self._strategy.cluster(document_vectors, n_clusters)
        
        if not clustering_result:
            logger.warning(f"No clusters created for vault '{vault_name}'")
            return []
        
        # Генерируем названия кластеров через LLM
        clusters = await self._generate_cluster_names(vault_name, clustering_result)
        
        logger.info(f"Created {len(clusters)} clusters for vault '{vault_name}'")
        return clusters
    
    async def update_clusters(
        self,
        vault_name: str,
    ) -> list[KnowledgeCluster]:
        """Обновление кластеров после изменений в vault'е.
        
        Args:
            vault_name: Имя vault'а
            
        Returns:
            Обновленный список кластеров
        """
        # Для обновления просто пересоздаем кластеры
        return await self.cluster_documents(vault_name)
    
    async def get_cluster_for_document(
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
        """
        return await self._cluster_repository.get_for_document(vault_name, document_id)
    
    async def _get_all_document_ids(self, vault_name: str) -> set[str]:
        """Получение всех document_ids из vault'а.
        
        Args:
            vault_name: Имя vault'а
            
        Returns:
            Множество document_ids
        """
        try:
            documents_table = await self._db_manager._ensure_table(vault_name, "documents")
            
            def _get_document_ids() -> set[str]:
                try:
                    arrow_table = documents_table.to_arrow()
                    if arrow_table.num_rows == 0:
                        return set()
                    
                    doc_ids = arrow_table["document_id"].to_pylist()
                    return set(doc_ids)
                except Exception as e:
                    logger.error(f"Error getting document IDs: {e}")
                    return set()
            
            return await asyncio.to_thread(_get_document_ids)
        except Exception as e:
            logger.error(f"Error in _get_all_document_ids for vault '{vault_name}': {e}")
            from obsidian_kb.types import DatabaseError
            
            if "was not found" in str(e) or "does not exist" in str(e).lower():
                raise VaultNotFoundError(vault_name) from e
            raise DatabaseError(f"Failed to get document IDs: {e}", vault_name=vault_name) from e
    
    async def _compute_document_embeddings(
        self,
        vault_name: str,
        document_ids: set[str],
    ) -> list[tuple[str, list[float]]]:
        """Вычисление средних embeddings для документов.
        
        Args:
            vault_name: Имя vault'а
            document_ids: Множество document_ids
            
        Returns:
            Список кортежей (document_id, average_embedding)
        """
        document_vectors = []
        
        # Обрабатываем документы параллельно с ограничением
        semaphore = asyncio.Semaphore(10)  # Макс 10 параллельных документов
        
        async def process_document(doc_id: str) -> tuple[str, list[float]] | None:
            async with semaphore:
                try:
                    # Получаем все чанки документа
                    chunks = await self._chunk_repository.get_by_document(vault_name, doc_id)
                    
                    if not chunks:
                        return None
                    
                    # Извлекаем векторы из чанков
                    vectors = []
                    for chunk in chunks:
                        if chunk.vector and len(chunk.vector) > 0:
                            vectors.append(chunk.vector)
                    
                    if not vectors:
                        return None
                    
                    # Вычисляем средний вектор
                    import numpy as np
                    
                    vectors_array = np.array(vectors)
                    avg_vector = vectors_array.mean(axis=0).tolist()
                    
                    return (doc_id, avg_vector)
                except Exception as e:
                    logger.error(f"Error computing embedding for document {doc_id}: {e}")
                    return None
        
        # Обрабатываем все документы параллельно
        tasks = [process_document(doc_id) for doc_id in document_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Фильтруем успешные результаты
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error processing document: {result}")
                continue
            if result:
                document_vectors.append(result)
        
        return document_vectors
    
    async def _generate_cluster_names(
        self,
        vault_name: str,
        clustering_result: list[dict[str, Any]],
    ) -> list[KnowledgeCluster]:
        """Генерация названий кластеров через LLM.
        
        Args:
            vault_name: Имя vault'а
            clustering_result: Результат кластеризации
            
        Returns:
            Список KnowledgeCluster с названиями
        """
        clusters = []
        now = datetime.now()
        
        # Обрабатываем кластеры параллельно с ограничением
        semaphore = asyncio.Semaphore(5)  # Макс 5 параллельных запросов к LLM
        
        async def process_cluster(cluster_data: dict[str, Any], cluster_index: int) -> KnowledgeCluster:
            async with semaphore:
                cluster_id = f"{vault_name}::cluster_{cluster_index}"
                document_ids = cluster_data["document_ids"]
                centroid_vector = cluster_data.get("centroid_vector")
                
                # Получаем обогащения документов (если доступны)
                cluster_summaries = await self._get_cluster_summaries(vault_name, document_ids)
                
                # Генерируем название через LLM
                try:
                    cluster_info = await self._generate_cluster_name_llm(cluster_summaries)
                    cluster_name = cluster_info.get("cluster_name", f"Кластер {cluster_index + 1}")
                    description = cluster_info.get("description", "")
                    keywords = cluster_info.get("keywords", [])
                except Exception as e:
                    logger.warning(f"Failed to generate cluster name via LLM: {e}, using fallback")
                    # Fallback: используем простые названия
                    cluster_name = f"Кластер {cluster_index + 1}"
                    description = f"Кластер из {len(document_ids)} документов"
                    keywords = []
                
                return KnowledgeCluster(
                    cluster_id=cluster_id,
                    vault_name=vault_name,
                    cluster_name=cluster_name,
                    description=description,
                    document_ids=document_ids,
                    keywords=keywords,
                    created_at=now,
                    updated_at=now,
                    centroid_vector=centroid_vector,
                )
        
        # Обрабатываем все кластеры параллельно
        tasks = [
            process_cluster(cluster_data, idx)
            for idx, cluster_data in enumerate(clustering_result)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Фильтруем успешные результаты
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error processing cluster: {result}")
                continue
            if isinstance(result, KnowledgeCluster):
                clusters.append(result)
        
        return clusters
    
    async def _get_cluster_summaries(
        self,
        vault_name: str,
        document_ids: list[str],
    ) -> list[str]:
        """Получение резюме документов для генерации названия кластера.
        
        Args:
            vault_name: Имя vault'а
            document_ids: Список document_ids
            
        Returns:
            Список резюме документов
        """
        summaries = []
        
        # Пытаемся получить обогащения через LLMEnrichmentService
        try:
            # Получаем чанки документов
            all_chunks = []
            for doc_id in document_ids:
                chunks = await self._chunk_repository.get_by_document(vault_name, doc_id)
                all_chunks.extend(chunks)
            
            # Пытаемся получить обогащения для чанков
            from obsidian_kb.interfaces import IChunkEnrichmentRepository
            
            chunk_enrichment_repo = getattr(
                self._llm_enrichment_service, "_repository", None
            )
            if chunk_enrichment_repo:
                chunk_ids = [chunk.chunk_id for chunk in all_chunks[:10]]  # Берем первые 10 чанков
                enrichments = await chunk_enrichment_repo.get_many(vault_name, chunk_ids)
                
                for enrichment in enrichments.values():
                    if enrichment.summary:
                        summaries.append(enrichment.summary)
        except Exception as e:
            logger.debug(f"Could not get enrichments: {e}")
        
        # Fallback: используем первые несколько чанков документов
        if not summaries:
            for doc_id in document_ids[:5]:  # Берем первые 5 документов
                chunks = await self._chunk_repository.get_by_document(vault_name, doc_id)
                if chunks:
                    # Берем первые 200 символов первого чанка
                    content = chunks[0].content[:200] if chunks[0].content else ""
                    if content:
                        summaries.append(content)
        
        return summaries
    
    async def _generate_cluster_name_llm(self, cluster_summaries: list[str]) -> dict[str, Any]:
        """Генерация названия кластера через LLM.
        
        Args:
            cluster_summaries: Список резюме документов в кластере
            
        Returns:
            Словарь с cluster_name, description, keywords
        """
        if not cluster_summaries:
            return {
                "cluster_name": "Неизвестный кластер",
                "description": "",
                "keywords": [],
            }
        
        # Формируем текст для промпта
        summaries_text = "\n".join(
            f"- {summary}" for summary in cluster_summaries[:10]  # Ограничиваем до 10
        )
        
        prompt = CLUSTER_NAMING_PROMPT.format(cluster_documents_summaries=summaries_text)
        
        # Используем LLMEnrichmentService для генерации
        # Но для простоты можем использовать прямую интеграцию с Ollama
        try:
            # Пытаемся использовать существующий метод обогащения
            # Если нет, используем прямую интеграцию
            response_text = await self._call_llm_direct(prompt)
            return self._parse_cluster_naming_response(response_text)
        except Exception as e:
            logger.error(f"Error calling LLM for cluster naming: {e}")
            raise
    
    async def _call_llm_direct(self, prompt: str) -> str:
        """Прямой вызов LLM для генерации названия кластера.
        
        Args:
            prompt: Промпт для LLM
            
        Returns:
            Текст ответа от LLM
        """
        session = await self._get_session()
        base_url = settings.ollama_url.rstrip("/")
        model = settings.llm_model
        
        url = f"{base_url}/api/chat"
        
        messages = [
            {"role": "system", "content": ENRICHMENT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "format": "json",
        }
        
        try:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ProviderConnectionError(
                        f"LLM request failed with status {response.status}: {error_text}"
                    )

                result = await response.json()
                return result.get("message", {}).get("content", "")
        except aiohttp.ClientError as e:
            raise ProviderConnectionError(f"Failed to connect to LLM: {e}") from e
    
    def _parse_cluster_naming_response(self, response_text: str) -> dict[str, Any]:
        """Парсинг ответа LLM для генерации названия кластера.
        
        Args:
            response_text: Текст ответа от LLM
            
        Returns:
            Словарь с cluster_name, description, keywords
        """
        try:
            # Пытаемся извлечь JSON из ответа
            response_text = response_text.strip()
            
            # Удаляем markdown code blocks если есть
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            
            # Парсим JSON
            data = json.loads(response_text)
            
            return {
                "cluster_name": data.get("cluster_name", "Неизвестный кластер"),
                "description": data.get("description", ""),
                "keywords": data.get("keywords", []),
            }
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}, response: {response_text}")
            # Fallback: пытаемся извлечь название из текста
            return {
                "cluster_name": "Неизвестный кластер",
                "description": response_text[:200] if response_text else "",
                "keywords": [],
            }

