"""SearchVault MCP Tool implementation."""

import logging
from typing import Any

from obsidian_kb.config import settings
from obsidian_kb.mcp.base import InputSchema, MCPTool
from obsidian_kb.search_optimizer import AgentQueryNormalizer
from obsidian_kb.service_container import get_service_container
from obsidian_kb.types import RetrievalGranularity, SearchRequest, VaultNotFoundError
from obsidian_kb.validation import validate_search_params

logger = logging.getLogger(__name__)


class SearchVaultTool(MCPTool):
    """Tool to search in Obsidian vault using vector, FTS, or hybrid search."""

    @property
    def name(self) -> str:
        return "search_vault"

    @property
    def description(self) -> str:
        return """Поиск в Obsidian vault (v5).

Args:
    vault_name: Имя vault'а для поиска
    query: Поисковый запрос (текст + фильтры tags:, type:, created:)
    limit: Максимум результатов (default: 10)
    search_type: "vector" | "fts" | "hybrid" (default: hybrid)
    detail_level: Уровень детализации результатов
        - "auto": Автоматически на основе типа запроса (рекомендуется)
        - "full": Полный контент документов
        - "snippets": Только snippets
        - "metadata": Только метаданные

Returns:
    Структурированные результаты поиска в Markdown"""

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {
                "vault_name": {
                    "type": "string",
                    "description": "Имя vault'а для поиска",
                },
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос (текст + фильтры tags:, type:, created:)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Максимум результатов (default: 10)",
                },
                "search_type": {
                    "type": "string",
                    "description": '"vector" | "fts" | "hybrid" (default: hybrid)',
                },
                "detail_level": {
                    "type": "string",
                    "description": 'Уровень детализации: "auto" | "full" | "snippets" | "metadata"',
                },
            },
            "required": ["vault_name", "query"],
        }

    async def execute(self, **kwargs: Any) -> str:
        """Execute search in vault."""
        vault_name: str = kwargs["vault_name"]
        query: str = kwargs["query"]
        limit: int = kwargs.get("limit", 10) or 10
        search_type: str = kwargs.get("search_type", "hybrid") or "hybrid"
        detail_level: str = kwargs.get("detail_level", "auto") or "auto"

        container = get_service_container()

        if container.mcp_rate_limiter:
            await container.mcp_rate_limiter.acquire()

        # Валидация входных параметров
        validate_search_params(
            query=query, vault_name=vault_name, limit=limit, search_type=search_type
        )

        try:
            # Нормализуем агентный запрос
            normalized_query = AgentQueryNormalizer.normalize(query)
            if normalized_query != query:
                logger.debug(f"Normalized agent query: '{query}' -> '{normalized_query}'")

            # Маппинг detail_level → RetrievalGranularity
            granularity_map = {
                "auto": RetrievalGranularity.AUTO,
                "full": RetrievalGranularity.DOCUMENT,
                "snippets": RetrievalGranularity.CHUNK,
                "metadata": RetrievalGranularity.DOCUMENT,
            }
            granularity = granularity_map.get(detail_level, RetrievalGranularity.AUTO)

            # Создаём SearchRequest
            request = SearchRequest(
                vault_name=vault_name,
                query=normalized_query,
                limit=limit,
                search_type=search_type,
                granularity=granularity,
                include_content=(detail_level not in ("metadata", "snippets")),
            )

            # Выполняем поиск через SearchService
            response = await container.search_service.search(request)

            # Записываем метрику поиска
            try:
                avg_relevance = (
                    sum(r.score.value for r in response.results) / len(response.results)
                    if response.results
                    else 0.0
                )
                await container.metrics_collector.record_search(
                    vault_name=vault_name,
                    query=query,
                    search_type=search_type,
                    result_count=response.total_found,
                    execution_time_ms=response.execution_time_ms,
                    avg_relevance_score=avg_relevance,
                )
            except Exception as e:
                logger.warning(f"Failed to record search metric: {e}")

            # Логируем поисковый запрос
            try:
                # Извлекаем информацию о фильтрах из response
                filters_info = (
                    response.filters_applied.copy() if response.filters_applied else {}
                )

                # Получаем статистику vault'а (опционально)
                vault_stats_info = None
                try:
                    stats = await container.db_manager.get_vault_stats(vault_name)
                    vault_stats_info = {
                        "file_count": stats.file_count,
                        "chunk_count": stats.chunk_count,
                        "total_size_bytes": stats.total_size_bytes,
                        "tags_count": len(stats.tags),
                    }
                except Exception as e:
                    logger.debug(f"Failed to get vault stats for logging: {e}")

                container.search_logger.log_search(
                    original_query=query,
                    normalized_query=normalized_query,
                    vault_name=vault_name,
                    search_type=search_type,
                    result_count=response.total_found,
                    execution_time_ms=response.execution_time_ms,
                    avg_relevance_score=avg_relevance if response.results else 0.0,
                    empty_results=len(response.results) == 0,
                    used_optimizer=False,
                    source="mcp",
                    requested_search_type=search_type,
                    was_fallback=False,
                    ollama_available=True,
                    filters=filters_info if filters_info else None,
                    limit=limit,
                    vault_stats=vault_stats_info,
                    embedding_model=settings.embedding_model,
                )
            except Exception as e:
                logger.warning(f"Failed to log search query: {e}")

            # Форматируем результаты через Formatter
            return container.formatter.format_markdown(response)

        except VaultNotFoundError:
            logger.error(f"Vault not found: {vault_name}", exc_info=True)
            return f"Ошибка: Vault '{vault_name}' не найден. Используйте `index_vault` для индексирования."
        except Exception as e:
            logger.error(f"Error in search_vault: {e}", exc_info=True)
            return f"Ошибка поиска: {e}"
