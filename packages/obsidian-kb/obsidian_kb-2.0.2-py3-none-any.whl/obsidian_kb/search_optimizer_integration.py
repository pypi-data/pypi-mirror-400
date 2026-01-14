"""Пример интеграции SearchOptimizer с существующим кодом."""

import logging

from obsidian_kb.config import settings
from obsidian_kb.embedding_service import EmbeddingService
from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.search_optimizer import SearchOptimizer
from obsidian_kb.types import SearchResult

logger = logging.getLogger(__name__)


async def optimized_search(
    db_manager: LanceDBManager,
    embedding_service: EmbeddingService,
    vault_name: str,
    query: str,
    limit: int = 10,
    search_type: str = "hybrid",
    use_optimizer: bool = True,
    where: str | None = None,
    document_ids: set[str] | None = None,
) -> list[SearchResult]:
    """Оптимизированный поиск с интеграцией SearchOptimizer (v4).

    Args:
        db_manager: Менеджер БД
        embedding_service: Сервис embeddings
        vault_name: Имя vault'а
        query: Поисковый запрос (уже нормализованный через QueryParser)
        limit: Максимум результатов
        search_type: Тип поиска ("vector", "fts", "hybrid")
        use_optimizer: Использовать оптимизатор поиска
        where: WHERE clause для фильтрации чанков (SQL-подобный синтаксис)
        document_ids: Опциональный фильтр по document_id для двухэтапных запросов (v4)

    Returns:
        Результаты поиска
    """
    # Получаем embedding для запроса (query уже нормализован через QueryParser)
    query_embedding: list[float] | None = None
    try:
        query_embedding = await embedding_service.get_embedding(query, embedding_type="query")
    except Exception as e:
        logger.warning(f"Failed to get embedding: {e}")
        if search_type in ("vector", "hybrid"):
            # Fallback на FTS
            search_type = "fts"

    # Если оптимизатор включён и доступен embedding, используем его
    if use_optimizer and query_embedding and search_type == "hybrid":
        try:
            # ВАЖНО: Отключаем agent_normalization, т.к. запрос уже нормализован через QueryParser
            # QueryParser уже обработал стоп-слова, синонимы и lowercase
            # AgentQueryNormalizer нужен только для исходных запросов от агентов, не для уже нормализованных
            optimizer = SearchOptimizer(
                embedding_service=embedding_service,
                db_manager=db_manager,
                enable_rerank=settings.enable_rerank,
                enable_query_expansion=settings.enable_query_expansion,
                enable_feature_ranking=settings.enable_feature_ranking,
                enable_agent_normalization=False,  # Отключаем, т.к. запрос уже нормализован
                enable_query_cache=settings.enable_search_optimizer,
            )

            results = await optimizer.optimize_search(
                vault_name=vault_name,
                query=query,  # Используем уже нормализованный запрос
                query_vector=query_embedding,  # Embedding для того же запроса
                limit=limit,
                adaptive_alpha=settings.adaptive_alpha,
                where=where,
                document_ids=document_ids,
            )

            return results

        except Exception as e:
            logger.warning(f"Search optimizer failed: {e}, falling back to standard search")
            # Fallback на стандартный поиск

    # Стандартный поиск (fallback или если оптимизатор отключён)
    if search_type == "vector":
        if query_embedding is None:
            raise ValueError("Query embedding required for vector search")
        return await db_manager.vector_search(
            vault_name, query_embedding, limit=limit, where=where, document_ids=document_ids
        )
    elif search_type == "fts":
        return await db_manager.fts_search(
            vault_name, query, limit=limit, where=where, document_ids=document_ids
        )
    else:  # hybrid
        if query_embedding is None:
            # Fallback на FTS
            return await db_manager.fts_search(
                vault_name, query, limit=limit, where=where, document_ids=document_ids
            )
        return await db_manager.hybrid_search(
            vault_name, query_embedding, query, limit=limit, alpha=settings.hybrid_alpha, where=where, document_ids=document_ids
        )


# Пример использования в mcp_server.py:
"""
# В начале файла добавить:
from obsidian_kb.search_optimizer_integration import optimized_search

# В функции search_vault заменить:
# Старый код:
# results = await db_manager.hybrid_search(...)

# Новый код:
results = await optimized_search(
    db_manager=db_manager,
    embedding_service=embedding_service,
    vault_name=vault_name,
    query=text_query,
    limit=limit,
    search_type=search_type,
    use_optimizer=True,  # Можно сделать настраиваемым через settings
)
"""

