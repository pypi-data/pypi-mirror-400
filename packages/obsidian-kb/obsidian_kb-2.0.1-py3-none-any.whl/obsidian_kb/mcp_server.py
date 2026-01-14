"""MCP сервер для интеграции с Claude Desktop."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from functools import wraps
from pathlib import Path
from typing import AsyncIterator

from fastmcp import FastMCP

from obsidian_kb.config import settings
from obsidian_kb.diagnostics import send_notification
from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.indexing_utils import index_with_cache
from obsidian_kb.search_optimizer import AgentQueryNormalizer
from obsidian_kb.service_container import get_service_container
from obsidian_kb.interfaces import RipgrepMatch
from obsidian_kb.types import (
    HealthStatus,
    RetrievalGranularity,
    SearchRequest,
    VaultNotFoundError,
)
from obsidian_kb.vault_indexer import VaultIndexer

logger = logging.getLogger(__name__)

# Получение контейнера сервисов происходит лениво через get_service_container()
# Это позволяет избежать инициализации при импорте модуля

# MCP сервер создаётся ниже после определения lifespan функции
# Здесь только forward declaration для type hints
# Rate limiter и job_queue теперь управляются через ServiceContainer
# См. get_service_container().mcp_rate_limiter и get_service_container().job_queue


def get_job_queue():
    """Получение глобальной очереди фоновых задач.

    Returns:
        BackgroundJobQueue или None если не инициализирована
    """
    return get_service_container().job_queue


def set_job_queue(job_queue):
    """Установка глобальной очереди фоновых задач.

    Args:
        job_queue: Экземпляр BackgroundJobQueue
    """
    get_service_container().set_job_queue(job_queue)


def with_rate_limit(func):
    """Декоратор для применения rate limiting к MCP инструментам.
    
    Args:
        func: Функция для обёртки
        
    Returns:
        Обёрнутая функция с rate limiting
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if get_service_container().mcp_rate_limiter:
            await get_service_container().mcp_rate_limiter.acquire()
        return await func(*args, **kwargs)
    return wrapper


@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncIterator[None]:
    """Lifespan context manager для MCP сервера.

    Управляет жизненным циклом фоновых сервисов:
    - BackgroundJobQueue
    - ChangeMonitorService
    """
    from obsidian_kb.indexing.job_queue import BackgroundJobQueue
    from obsidian_kb.indexing.change_monitor import ChangeMonitorService
    from obsidian_kb.config.manager import get_config_manager

    job_queue = None
    change_monitor = None

    try:
        # Запускаем фоновые проверки как task (функция определена ниже)
        asyncio.create_task(_background_startup_checks())

        # Создаём и запускаем очередь задач
        job_queue = BackgroundJobQueue(max_workers=2)
        await job_queue.start()

        # Устанавливаем очередь для доступа из MCP команд
        set_job_queue(job_queue)

        # Создаём и запускаем монитор изменений
        config_manager = get_config_manager()
        change_monitor = ChangeMonitorService(
            job_queue=job_queue,
            config_manager=config_manager,
            enabled=True,
        )
        await change_monitor.start()

        logger.info("Background services (JobQueue, ChangeMonitor) started")

        yield  # Сервер работает

    finally:
        # Graceful shutdown
        if change_monitor:
            await change_monitor.stop()
        if job_queue:
            await job_queue.stop()
        set_job_queue(None)
        logger.info("Background services stopped")


# Создаём MCP сервер с lifespan
mcp = FastMCP("obsidian-kb", lifespan=lifespan)

# ============================================================================
# Auto-registration of MCPTool classes from mcp/tools/ directory
# ============================================================================
# New tools should be added as MCPTool subclasses in src/obsidian_kb/mcp/tools/
# They will be automatically discovered and registered here.
# ============================================================================

from obsidian_kb.mcp.registry import ToolRegistry

# Create registry and discover tools from mcp/tools/ directory
_tool_registry = ToolRegistry()
_discovered_tools_count = _tool_registry.discover()
logger.info(f"Auto-discovered {_discovered_tools_count} MCP tools from mcp/tools/")

# Register all discovered tools with FastMCP
_tool_registry.register_all(mcp)

# ============================================================================
# Legacy tool registration (for backward compatibility)
# These tools are registered using the old pattern and will be migrated
# to MCPTool classes incrementally.
# ============================================================================

# Регистрируем indexing tools
from obsidian_kb.mcp_tools.indexing_tools import (
    enrich_document,
    index_documents,
    index_status,
    preview_chunks,
    reindex_vault,
    register_mcp,
)

# Регистрируем provider tools
from obsidian_kb.mcp_tools.provider_tools import (
    estimate_cost,
    list_providers,
    list_yandex_models,
    provider_health,
    set_provider,
    test_provider,
)

# Регистрируем quality tools
from obsidian_kb.mcp_tools.quality_tools import (
    audit_index,
    cost_report,
    index_coverage,
    performance_report,
    test_retrieval,
)

# Регистрируем объект mcp для использования в indexing_tools
register_mcp(mcp)

# Регистрируем инструменты через декораторы
# Indexing tools
mcp.tool()(index_documents)
mcp.tool()(reindex_vault)
mcp.tool()(index_status)
mcp.tool()(preview_chunks)
mcp.tool()(enrich_document)

# Provider tools
mcp.tool()(list_providers)
mcp.tool()(list_yandex_models)
mcp.tool()(set_provider)
mcp.tool()(test_provider)
mcp.tool()(provider_health)
mcp.tool()(estimate_cost)

# Quality tools
mcp.tool()(index_coverage)
mcp.tool()(test_retrieval)
mcp.tool()(audit_index)
mcp.tool()(cost_report)
mcp.tool()(performance_report)


@mcp.tool()
async def search_vault(vault_name: str, query: str, limit: int = 10, search_type: str = "hybrid", detail_level: str = "auto") -> str:
    """Поиск в Obsidian vault (v5).

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
        Структурированные результаты поиска в Markdown
    """
    if get_service_container().mcp_rate_limiter:
        await get_service_container().mcp_rate_limiter.acquire()
    from obsidian_kb.validation import validate_search_params
    
    # Валидация входных параметров
    validate_search_params(query=query, vault_name=vault_name, limit=limit, search_type=search_type)
    
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
        response = await get_service_container().search_service.search(request)
        
        # Записываем метрику поиска
        try:
            avg_relevance = sum(r.score.value for r in response.results) / len(response.results) if response.results else 0.0
            await get_service_container().metrics_collector.record_search(
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
            filters_info = response.filters_applied.copy() if response.filters_applied else {}
            
            # Получаем статистику vault'а (опционально)
            vault_stats_info = None
            try:
                stats = await get_service_container().db_manager.get_vault_stats(vault_name)
                vault_stats_info = {
                    "file_count": stats.file_count,
                    "chunk_count": stats.chunk_count,
                    "total_size_bytes": stats.total_size_bytes,
                    "tags_count": len(stats.tags),
                }
            except Exception as e:
                logger.debug(f"Failed to get vault stats for logging: {e}")
            
            get_service_container().search_logger.log_search(
                original_query=query,
                normalized_query=normalized_query,
                vault_name=vault_name,
                search_type=search_type,
                result_count=response.total_found,
                execution_time_ms=response.execution_time_ms,
                avg_relevance_score=avg_relevance if response.results else 0.0,
                empty_results=len(response.results) == 0,
                used_optimizer=False,  # Оптимизатор теперь внутри SearchService
                source="mcp",
                requested_search_type=search_type,
                was_fallback=False,
                ollama_available=True,  # SearchService обрабатывает это внутри
                filters=filters_info if filters_info else None,
                limit=limit,
                vault_stats=vault_stats_info,
                embedding_model=settings.embedding_model,
            )
        except Exception as e:
            logger.warning(f"Failed to log search query: {e}")
        
        # Форматируем результаты через Formatter
        return get_service_container().formatter.format_markdown(response)

    except VaultNotFoundError:
        logger.error(f"Vault not found: {vault_name}", exc_info=True)
        return f"Ошибка: Vault '{vault_name}' не найден. Используйте `index_vault` для индексирования."
    except Exception as e:
        logger.error(f"Error in search_vault: {e}", exc_info=True)
        return f"Ошибка поиска: {e}"


@mcp.tool()
async def search_multi_vault(vault_names: list[str], query: str, limit: int = 10) -> str:
    """Поиск по нескольким vault'ам одновременно (v5).

    Args:
        vault_names: Список имён vault'ов для поиска
        query: Поисковый запрос
        limit: Максимум результатов (default: 10)

    Returns:
        Форматированные результаты поиска из всех vault'ов
    """
    if get_service_container().mcp_rate_limiter:
        await get_service_container().mcp_rate_limiter.acquire()
    
    try:
        # Нормализуем агентный запрос
        normalized_query = AgentQueryNormalizer.normalize(query)
        if normalized_query != query:
            logger.debug(f"Normalized agent query: '{query}' -> '{normalized_query}'")
        
        # Создаём SearchRequest
        request = SearchRequest(
            vault_name="",  # Будет переопределён для каждого vault
            query=normalized_query,
            limit=limit,
            search_type="hybrid",
            granularity=RetrievalGranularity.AUTO,
        )
        
        # Выполняем поиск через SearchService
        response = await get_service_container().search_service.search_multi_vault(vault_names, request)
        
        # Записываем метрику поиска
        try:
            avg_relevance = sum(r.score.value for r in response.results) / len(response.results) if response.results else 0.0
            await get_service_container().metrics_collector.record_search(
                vault_name=None,  # None для multi-vault поиска
                query=query,
                search_type=response.strategy_used,
                result_count=response.total_found,
                execution_time_ms=response.execution_time_ms,
                avg_relevance_score=avg_relevance,
            )
        except Exception as e:
            logger.warning(f"Failed to record search metric: {e}")
        
        # Логируем поисковый запрос
        try:
            filters_info = response.filters_applied.copy() if response.filters_applied else {}
            
            get_service_container().search_logger.log_search(
                original_query=query,
                normalized_query=normalized_query,
                vault_name=None,  # None для multi-vault
                search_type=response.strategy_used,
                result_count=response.total_found,
                execution_time_ms=response.execution_time_ms,
                avg_relevance_score=avg_relevance if response.results else 0.0,
                empty_results=len(response.results) == 0,
                used_optimizer=False,
                source="mcp",
                requested_search_type="hybrid",
                was_fallback=False,
                ollama_available=True,
                filters=filters_info if filters_info else None,
                limit=limit,
                embedding_model=settings.embedding_model,
            )
        except Exception as e:
            logger.warning(f"Failed to log search query: {e}")
        
        # Форматируем результаты через Formatter
        return get_service_container().formatter.format_markdown(response)

    except Exception as e:
        logger.error(f"Error in search_multi_vault: {e}", exc_info=True)
        return f"Ошибка поиска: {e}"


# NOTE: list_vaults and vault_stats are now auto-registered via MCPTool classes
# See: src/obsidian_kb/mcp/tools/list_vaults_tool.py and vault_stats_tool.py


@mcp.tool()
async def index_vault(vault_name: str, vault_path: str) -> str:
    """Переиндексировать vault (или создать новый индекс).

    Индексация выполняется в фоновом режиме, чтобы не блокировать агента.

    Args:
        vault_name: Имя vault'а
        vault_path: Путь к vault'у

    Returns:
        Результат запуска индексации (ID задачи для отслеживания)
    """
    if get_service_container().mcp_rate_limiter:
        await get_service_container().mcp_rate_limiter.acquire()
    try:
        vault_path_obj = Path(vault_path)
        if not vault_path_obj.exists():
            return f"Ошибка: Путь '{vault_path}' не существует."

        if not vault_path_obj.is_dir():
            return f"Ошибка: Путь '{vault_path}' не является директорией."

        # Проверяем инкрементальное индексирование
        indexed_files = None
        try:
            indexed_files = await get_service_container().db_manager.get_indexed_files(vault_name)
            only_changed = len(indexed_files) > 0
        except Exception as e:
            logger.debug(f"Failed to get indexed files, using full indexing: {e}")
            only_changed = False

        # Запускаем индексацию в фоне
        job_queue = get_job_queue()
        if job_queue:
            from obsidian_kb.indexing.job_queue import JobPriority
            try:
                job = await job_queue.enqueue(
                    vault_name=vault_name,
                    vault_path=vault_path_obj,
                    operation="index_vault",
                    params={"only_changed": only_changed},
                    priority=JobPriority.NORMAL,
                )
                
                lines = [f"## Индексация vault '{vault_name}' запущена в фоне\n"]
                lines.append(f"- **ID задачи:** `{job.id}`")
                lines.append(f"- **Статус:** {job.status.value}")
                lines.append(f"- **Режим:** {'Инкрементальное' if only_changed else 'Полное'}")
                lines.append(f"\nИспользуйте `get_job_status` для проверки прогресса.")
                return "\n".join(lines)
            except Exception as e:
                logger.error(f"Ошибка запуска фоновой индексации: {e}", exc_info=True)
                return f"Ошибка запуска индексации: {e}"
        else:
            # Fallback: синхронная индексация если очередь недоступна
            logger.warning("Job queue недоступна, выполняем синхронную индексацию")
            indexer = VaultIndexer(vault_path_obj, vault_name)
            embedding_cache = EmbeddingCache()
            chunks, embeddings, stats = await index_with_cache(
                vault_name=vault_name,
                indexer=indexer,
                embedding_service=get_service_container().embedding_service,
                db_manager=get_service_container().db_manager,
                embedding_cache=embedding_cache,
                only_changed=only_changed,
                indexed_files=indexed_files,
            )

            if not chunks:
                if only_changed:
                    return f"Vault '{vault_name}': все файлы актуальны, индексирование не требуется."
                return f"Vault '{vault_name}' просканирован, но не найдено чанков для индексирования."

            # Сохраняем в БД
            await get_service_container().db_manager.upsert_chunks(vault_name, chunks, embeddings)

            file_count = len(set(c.file_path for c in chunks))
            cache_info = f" (кэш: {stats.get('cached', 0)}, вычислено: {stats.get('computed', 0)})" if stats else ""
            return f"Vault '{vault_name}' успешно проиндексирован: {len(chunks)} чанков из {file_count} файлов{cache_info}."

    except Exception as e:
        logger.error(f"Error in index_vault: {e}")
        return f"Ошибка индексирования: {e}"


@mcp.tool()
async def get_job_status(job_id: str | None = None, vault_name: str | None = None) -> str:
    """Получить статус фоновых задач индексации.

    Args:
        job_id: ID конкретной задачи (опционально)
        vault_name: Фильтр по vault'у (опционально)

    Returns:
        Статус задачи(ей) в markdown формате
    """
    try:
        job_queue = get_job_queue()
        if not job_queue:
            return "Ошибка: Очередь фоновых задач недоступна."

        if job_id:
            # Получаем конкретную задачу
            job = await job_queue.get_job_status(job_id)
            if not job:
                return f"Задача с ID '{job_id}' не найдена."

            lines = [f"## Статус задачи: {job_id}\n"]
            lines.append(f"- **Vault:** {job.vault_name}")
            lines.append(f"- **Операция:** {job.operation}")
            lines.append(f"- **Статус:** {job.status.value}")
            lines.append(f"- **Прогресс:** {job.progress * 100:.1f}%")
            lines.append(f"- **Можно отменить:** {'да' if job.cancellable else 'нет'}")
            lines.append(f"- **Создана:** {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if job.started_at:
                lines.append(f"- **Начата:** {job.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if job.completed_at:
                lines.append(f"- **Завершена:** {job.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if job.error:
                lines.append(f"- **Ошибка:** {job.error}")
            if job.result:
                result = job.result
                lines.append(f"\n### Результаты")
                lines.append(f"- **Документов обработано:** {result.documents_processed}/{result.documents_total}")
                lines.append(f"- **Чанков создано:** {result.chunks_created}")
                lines.append(f"- **Длительность:** {result.duration_seconds:.1f} сек")
                if result.errors:
                    lines.append(f"- **Ошибок:** {len(result.errors)}")
                    for error in result.errors[:3]:
                        lines.append(f"  - {error[:100]}")
                    if len(result.errors) > 3:
                        lines.append(f"  - ... и ещё {len(result.errors) - 3}")
                if result.warnings:
                    lines.append(f"- **Предупреждений:** {len(result.warnings)}")
                    for warning in result.warnings[:3]:
                        lines.append(f"  - {warning}")

            # Phase 2: Enrichment статистика
            enrichment_stats = job.enrichment_stats or (job.result.enrichment_stats if job.result else None)
            if enrichment_stats:
                lines.append(f"\n### Обогащение (Enrichment)")
                lines.append(f"- **Всего чанков:** {enrichment_stats.total_chunks}")
                lines.append(f"- **Успешно обогащено:** {enrichment_stats.enriched_ok}")
                if enrichment_stats.enriched_fallback > 0:
                    fallback_pct = (enrichment_stats.enriched_fallback / enrichment_stats.total_chunks * 100) if enrichment_stats.total_chunks > 0 else 0
                    lines.append(f"- **⚠️ Fallback (без контекста):** {enrichment_stats.enriched_fallback} ({fallback_pct:.1f}%)")
                lines.append(f"- **Успешность:** {enrichment_stats.success_rate:.1f}%")
                if enrichment_stats.errors:
                    lines.append(f"- **Ошибок enrichment:** {len(enrichment_stats.errors)}")
                    for error in enrichment_stats.errors[:3]:
                        lines.append(f"  - {error[:80]}")
                    if len(enrichment_stats.errors) > 3:
                        lines.append(f"  - ... и ещё {len(enrichment_stats.errors) - 3}")

            return "\n".join(lines)
        else:
            # Получаем список задач
            from obsidian_kb.indexing.job_queue import JobStatus
            jobs = await job_queue.list_jobs(vault_name=vault_name)
            
            if not jobs:
                filter_text = f" для vault '{vault_name}'" if vault_name else ""
                return f"## Фоновые задачи{filter_text}\n\n*Задач не найдено*"

            lines = [f"## Фоновые задачи"]
            if vault_name:
                lines[0] += f" (vault: {vault_name})"
            lines.append("")

            # Группируем по статусам
            status_groups: dict[JobStatus, list] = {}
            for job in jobs:
                if job.status not in status_groups:
                    status_groups[job.status] = []
                status_groups[job.status].append(job)

            status_order = [JobStatus.RUNNING, JobStatus.PENDING, JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
            status_names = {
                JobStatus.RUNNING: "Выполняются",
                JobStatus.PENDING: "Ожидают",
                JobStatus.COMPLETED: "Завершены",
                JobStatus.FAILED: "Ошибки",
                JobStatus.CANCELLED: "Отменены",
            }

            for status in status_order:
                if status not in status_groups:
                    continue
                
                jobs_list = status_groups[status]
                lines.append(f"### {status_names[status]} ({len(jobs_list)})")
                
                for job in jobs_list[:10]:  # Максимум 10 задач на статус
                    lines.append(f"\n**{job.id}**")
                    lines.append(f"- Vault: {job.vault_name}")
                    lines.append(f"- Операция: {job.operation}")
                    lines.append(f"- Прогресс: {job.progress * 100:.1f}%")
                    lines.append(f"- Можно отменить: {'да' if job.cancellable else 'нет'}")
                    lines.append(f"- Создана: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    if job.error:
                        lines.append(f"- Ошибка: {job.error}")
                    # Phase 2: Краткая статистика enrichment для списка
                    enrichment = job.enrichment_stats or (job.result.enrichment_stats if job.result else None)
                    if enrichment and enrichment.total_chunks > 0:
                        if enrichment.enriched_fallback > 0:
                            lines.append(f"- Enrichment: {enrichment.enriched_ok}/{enrichment.total_chunks} ⚠️ ({enrichment.enriched_fallback} fallback)")
                        else:
                            lines.append(f"- Enrichment: {enrichment.enriched_ok}/{enrichment.total_chunks} ✓")
                
                if len(jobs_list) > 10:
                    lines.append(f"\n*... и ещё {len(jobs_list) - 10} задач*")
                lines.append("")

            return "\n".join(lines)

    except Exception as e:
        logger.error(f"Error in get_job_status: {e}", exc_info=True)
        return f"Ошибка получения статуса задачи: {e}"


@mcp.tool()
async def cancel_job(job_id: str) -> str:
    """Отменить фоновую задачу индексации.

    Реализует graceful shutdown:
    - Для ожидающих задач (pending): немедленная отмена
    - Для выполняющихся задач (running): завершает текущий документ и останавливается
    - Частично проиндексированные данные сохраняются (не откатываются)

    Args:
        job_id: ID задачи из get_job_status()

    Returns:
        Результат отмены в markdown формате
    """
    try:
        job_queue = get_job_queue()
        if not job_queue:
            return "Ошибка: Очередь фоновых задач недоступна."

        # Получаем информацию о задаче до отмены
        job = await job_queue.get_job_status(job_id)

        # Выполняем отмену
        result = await job_queue.cancel_job(job_id)

        if result == "not_found":
            return f"❌ Задача `{job_id}` не найдена."

        if result == "already_completed":
            return (
                f"⚠️ Задача `{job_id}` уже завершена.\n\n"
                f"Статус: {job.status.value if job else 'unknown'}"
            )

        if result == "cancelled":
            lines = ["## Задача отменена\n"]
            lines.append(f"- **Job ID:** `{job_id}`")
            if job:
                lines.append(f"- **Vault:** {job.vault_name}")
                lines.append(f"- **Операция:** {job.operation}")
                lines.append(f"- **Прогресс при отмене:** {job.progress:.1%}")
                lines.append(f"- **Можно ли отменить (cancellable):** {job.cancellable}")
            lines.append("\n*Частично проиндексированные данные сохранены.*")
            return "\n".join(lines)

        return f"❌ Неизвестный результат отмены: {result}"

    except Exception as e:
        logger.error(f"Error in cancel_job: {e}", exc_info=True)
        return f"Ошибка отмены задачи: {e}"


# NOTE: system_health is now auto-registered via MCPTool class
# See: src/obsidian_kb/mcp/tools/system_health_tool.py


@mcp.tool()
async def get_metrics(days: int = 7, limit: int = 10, vault_name: str | None = None) -> str:
    """Получить метрики использования системы за период.

    Args:
        days: Количество дней для анализа (default: 7)
        limit: Максимум популярных запросов/vault'ов (default: 10)
        vault_name: Фильтр по конкретному vault'у (опционально)

    Returns:
        Форматированная сводка метрик в markdown
    """
    try:
        summary = await get_service_container().metrics_collector.get_summary(days=days, limit=limit, vault_name=vault_name)

        vault_filter_text = f" для vault '{vault_name}'" if vault_name else ""
        lines = [f"## 📊 Метрики использования obsidian-kb{vault_filter_text}\n"]
        lines.append(f"**Период:** {summary.period_start.strftime('%Y-%m-%d')} - {summary.period_end.strftime('%Y-%m-%d')}\n")

        # Общая статистика
        lines.append("### Общая статистика\n")
        lines.append(f"- **Всего запросов:** {summary.total_searches}")
        lines.append(f"- **Среднее время выполнения:** {summary.avg_execution_time_ms:.2f} мс")
        lines.append(f"- **Уникальных vault'ов:** {summary.total_vaults_searched}")
        lines.append(f"- **Пустых результатов:** {summary.empty_results_count} ({summary.empty_results_percentage:.1f}%)")
        lines.append(f"- **Средняя релевантность:** {summary.avg_relevance_score:.3f}\n")

        # По типам поиска
        if summary.searches_by_type:
            lines.append("### По типам поиска\n")
            for search_type, count in sorted(summary.searches_by_type.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / summary.total_searches * 100) if summary.total_searches > 0 else 0
                lines.append(f"- **{search_type}:** {count} ({percentage:.1f}%)")
            lines.append("")

        # Популярные запросы
        if summary.popular_queries:
            lines.append("### Популярные запросы\n")
            for idx, (query, count) in enumerate(summary.popular_queries, 1):
                lines.append(f"{idx}. `{query[:50]}{'...' if len(query) > 50 else ''}` — {count} раз")
            lines.append("")

        # Популярные vault'ы
        if summary.popular_vaults:
            lines.append("### Популярные vault'ы\n")
            for idx, (vault, count) in enumerate(summary.popular_vaults, 1):
                lines.append(f"{idx}. **{vault}** — {count} запросов")
            lines.append("")

        # Запросы без результатов
        if summary.queries_with_no_results:
            lines.append("### Запросы без результатов\n")
            for idx, (query, count) in enumerate(summary.queries_with_no_results, 1):
                lines.append(f"{idx}. `{query[:50]}{'...' if len(query) > 50 else ''}` — {count} раз")
            lines.append("")

        if summary.total_searches == 0:
            lines.append("*Метрики за указанный период отсутствуют*")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        return f"Ошибка получения метрик: {e}"


@mcp.tool()
async def add_vault_to_config(vault_path: str, vault_name: str | None = None, auto_index: bool = True) -> str:
    """Добавить vault в конфигурацию obsidian-kb.

    Args:
        vault_path: Путь к директории vault'а (может быть относительным или абсолютным)
        vault_name: Имя vault'а. Если не указано, будет использовано имя директории
        auto_index: Автоматически проиндексировать vault после добавления (default: True)

    Returns:
        Результат добавления vault'а в конфигурацию
    """
    try:
        # Преобразуем путь в абсолютный
        vault_path_obj = Path(vault_path).resolve()
        
        if not vault_path_obj.exists():
            return f"Ошибка: Путь '{vault_path_obj}' не существует."
        
        if not vault_path_obj.is_dir():
            return f"Ошибка: Путь '{vault_path_obj}' не является директорией."
        
        # Если имя не указано, используем имя директории
        if vault_name is None:
            vault_name = vault_path_obj.name
        
        config_path = settings.vaults_config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Загружаем существующий конфиг или создаём новый
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                logger.warning(f"Ошибка чтения конфига: {e}, создаём новый")
                config = {"vaults": []}
        else:
            config = {"vaults": []}
        
        vaults = config.get("vaults", [])
        vault_path_str = str(vault_path_obj)
        is_new_vault = True
        
        # Проверяем, нет ли уже такого vault'а
        for v in vaults:
            if v.get("name") == vault_name:
                # Обновляем путь для существующего vault'а
                v["path"] = vault_path_str
                is_new_vault = False
                break
            if v.get("path") == vault_path_str:
                existing_name = v.get("name")
                return f"Vault с путём '{vault_path_str}' уже существует в конфигурации (имя: '{existing_name}')."
        
        if is_new_vault:
            # Добавляем новый vault
            vaults.append({"name": vault_name, "path": vault_path_str})
        
        config["vaults"] = vaults
        
        # Сохраняем конфиг
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        result_lines = ["## Vault добавлен в конфигурацию\n"]
        result_lines.append(f"- **Имя:** {vault_name}")
        result_lines.append(f"- **Путь:** {vault_path_str}")
        result_lines.append(f"- **Конфиг:** {config_path}")
        
        # Автоматическая индексация нового vault'а в фоне
        if auto_index and is_new_vault:
            job_queue = get_job_queue()
            if job_queue:
                # Запускаем индексацию в фоне
                from obsidian_kb.indexing.job_queue import JobPriority
                try:
                    job = await job_queue.enqueue(
                        vault_name=vault_name,
                        vault_path=vault_path_obj,
                        operation="index_vault",
                        params={"only_changed": False},
                        priority=JobPriority.NORMAL,
                    )
                    result_lines.append(f"\n✅ **Индексация запущена в фоне**")
                    result_lines.append(f"- **ID задачи:** `{job.id}`")
                    result_lines.append(f"- **Статус:** {job.status.value}")
                    result_lines.append(f"\nИспользуйте `get_job_status` для проверки прогресса.")
                except Exception as e:
                    logger.error(f"Ошибка запуска фоновой индексации: {e}", exc_info=True)
                    result_lines.append(f"\n⚠️ **Ошибка запуска индексации:** {e}")
            else:
                # Fallback: синхронная индексация если очередь недоступна
                result_lines.append(f"\n[Индексирование vault '{vault_name}'...]")
                try:
                    indexer = VaultIndexer(vault_path_obj, vault_name)
                    embedding_cache = EmbeddingCache()
                    
                    chunks, embeddings, stats = await index_with_cache(
                        vault_name=vault_name,
                        indexer=indexer,
                        embedding_service=get_service_container().embedding_service,
                        db_manager=get_service_container().db_manager,
                        embedding_cache=embedding_cache,
                        only_changed=False,
                        indexed_files=None,
                    )
                    
                    if chunks:
                        await get_service_container().db_manager.upsert_chunks(vault_name, chunks, embeddings)
                        file_count = len(set(c.file_path for c in chunks))
                        cache_info = f" (кэш: {stats.get('cached', 0)}, вычислено: {stats.get('computed', 0)})" if stats else ""
                        result_lines.append(f"\n✅ **Индексировано:** {len(chunks)} чанков из {file_count} файлов{cache_info}")
                    else:
                        result_lines.append("\n⚠️ Нет чанков для индексирования")
                except Exception as e:
                    logger.error(f"Ошибка индексирования vault '{vault_name}': {e}", exc_info=True)
                    result_lines.append(f"\n⚠️ **Ошибка индексирования:** {e}")
        elif not is_new_vault:
            result_lines.append("\nℹ️ Путь обновлён для существующего vault'а")
        
        return "\n".join(result_lines)
    
    except Exception as e:
        logger.error(f"Error in add_vault_to_config: {e}", exc_info=True)
        return f"Ошибка добавления vault'а: {e}"


@mcp.tool()
async def check_vault_in_config(vault_path: str | None = None, vault_name: str | None = None) -> str:
    """Проверить, есть ли vault в конфигурации obsidian-kb.

    Args:
        vault_path: Путь к vault'у для проверки (может быть относительным или абсолютным)
        vault_name: Имя vault'а для проверки

    Returns:
        Информация о наличии vault'а в конфигурации
    """
    try:
        if not vault_path and not vault_name:
            return "Ошибка: Укажите либо vault_path, либо vault_name для проверки."
        
        config_path = settings.vaults_config
        
        if not config_path.exists():
            return "Конфигурационный файл не найден. Vault'ы не настроены."
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        vaults = config.get("vaults", [])
        
        if vault_path:
            vault_path_obj = Path(vault_path).resolve()
            vault_path_str = str(vault_path_obj)
            
            for v in vaults:
                if v.get("path") == vault_path_str:
                    return f"✅ Vault найден в конфигурации:\n- **Имя:** {v.get('name')}\n- **Путь:** {v.get('path')}"
            
            return f"❌ Vault с путём '{vault_path_str}' не найден в конфигурации."
        
        if vault_name:
            for v in vaults:
                if v.get("name") == vault_name:
                    return f"✅ Vault найден в конфигурации:\n- **Имя:** {v.get('name')}\n- **Путь:** {v.get('path')}"
            
            return f"❌ Vault с именем '{vault_name}' не найден в конфигурации."
        
        return "Ошибка: Не удалось выполнить проверку."
    
    except Exception as e:
        logger.error(f"Error in check_vault_in_config: {e}", exc_info=True)
        return f"Ошибка проверки vault'а: {e}"


# NOTE: list_configured_vaults and list_tags are now auto-registered via MCPTool classes
# See: src/obsidian_kb/mcp/tools/list_configured_vaults_tool.py and list_tags_tool.py


@mcp.tool()
async def list_doc_types(vault_name: str) -> str:
    """Получить список всех типов документов в vault'е для автодополнения.
    
    Args:
        vault_name: Имя vault'а
    
    Returns:
        Список типов документов в markdown формате
    """
    try:
        # В схеме v4 типы документов хранятся в таблице document_properties с ключом "type"
        properties_table = await get_service_container().db_manager._ensure_table(vault_name, "document_properties")
        db = get_service_container().db_manager._get_db()
        
        def _get_types() -> list[str]:
            try:
                arrow_table = properties_table.search().where("property_key = 'type'").to_arrow()
                
                if arrow_table.num_rows == 0:
                    return []
                
                # Получаем все значения типов документов
                doc_types = arrow_table["property_value"].to_pylist()
                # Фильтруем пустые и получаем уникальные
                unique_types = set(t for t in doc_types if t and t.strip())
                return sorted(unique_types)
            except Exception as e:
                logger.error(f"Error getting doc types: {e}")
                return []
        
        types_list = await asyncio.to_thread(_get_types)
        
        if not types_list:
            return f"## Типы документов в vault: {vault_name}\n\n*Типы документов не найдены*"
        
        lines = [f"## Типы документов в vault: {vault_name}\n"]
        lines.append(f"*Найдено {len(types_list)} уникальных типов*\n")
        
        for doc_type in types_list:
            lines.append(f"- `{doc_type}`")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"Ошибка: Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in list_doc_types: {e}", exc_info=True)
        return f"Ошибка получения типов документов: {e}"


@mcp.tool()
async def list_links(vault_name: str, limit: int = 100) -> str:
    """Получить список всех wikilinks в vault'е для автодополнения.
    
    Args:
        vault_name: Имя vault'а
        limit: Максимум links для возврата (default: 100)
    
    Returns:
        Список links в markdown формате
    """
    try:
        # В схеме v4 links хранятся в таблице chunks
        chunks_table = await get_service_container().db_manager._ensure_table(vault_name, "chunks")
        db = get_service_container().db_manager._get_db()
        
        def _get_links() -> list[str]:
            try:
                arrow_table = chunks_table.to_arrow()
                
                if arrow_table.num_rows == 0:
                    return []
                
                # Получаем все links из всех чанков
                links_list = arrow_table["links"].to_pylist()
                # Объединяем все links из всех чанков
                all_links = set()
                for links in links_list:
                    if isinstance(links, list):
                        all_links.update(links)
                
                return sorted(list(all_links))[:limit]
            except Exception as e:
                logger.error(f"Error getting links: {e}")
                return []
        
        links = await asyncio.to_thread(_get_links)
        
        if not links:
            return f"## Wikilinks в vault: {vault_name}\n\n*Wikilinks не найдены*"
        
        lines = [f"## Wikilinks в vault: {vault_name}\n"]
        lines.append(f"*Найдено {len(links)} уникальных links*\n")
        
        for link in links:
            lines.append(f"- `{link}`")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"Ошибка: Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in list_links: {e}", exc_info=True)
        return f"Ошибка получения links: {e}"


# ============================================================================
# Extended Query API Tools (v6)
# ============================================================================


@mcp.tool()
async def get_frontmatter(vault_name: str, file_path: str) -> str:
    """Получить frontmatter конкретного файла.
    
    Args:
        vault_name: Имя vault'а
        file_path: Путь к файлу (относительный от корня vault)
    
    Returns:
        YAML frontmatter файла или сообщение об ошибке
    
    Examples:
        get_frontmatter("naumen-cto", "People/Иван Иванов.md")
    """
    if get_service_container().mcp_rate_limiter:
        await get_service_container().mcp_rate_limiter.acquire()
    
    try:
        api = get_service_container().frontmatter_api
        result = await api.get_frontmatter(vault_name, file_path)
        
        if result is None:
            return f"Файл '{file_path}' не найден в vault '{vault_name}'"
        
        import yaml
        lines = [f"## Frontmatter: {file_path}\n"]
        lines.append("```yaml")
        lines.append(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        lines.append("```")
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Error getting frontmatter: {e}")
        return f"Ошибка получения frontmatter: {e}"


@mcp.tool()
async def get_vault_schema(
    vault_name: str,
    doc_type: str | None = None,
    top_values: int = 10,
) -> str:
    """Получить схему frontmatter vault'а — все поля, их типы и значения.
    
    Полезно для понимания структуры данных vault'а и доступных полей
    для фильтрации.
    
    Args:
        vault_name: Имя vault'а
        doc_type: Опционально — ограничить типом документа
        top_values: Количество примеров значений для каждого поля (default: 10)
    
    Returns:
        Структурированная схема полей с примерами значений
    
    Examples:
        get_vault_schema("naumen-cto")  # Все поля vault'а
        get_vault_schema("naumen-cto", "person")  # Только для type:person
        get_vault_schema("naumen-cto", "1-1", top_values=5)
    """
    if get_service_container().mcp_rate_limiter:
        await get_service_container().mcp_rate_limiter.acquire()
    
    try:
        api = get_service_container().frontmatter_api
        schema = await api.get_schema(vault_name, doc_type, top_values)
        
        type_filter = f" (type: {doc_type})" if doc_type else ""
        lines = [f"## Схема vault: {vault_name}{type_filter}\n"]
        lines.append(f"**Всего документов:** {schema.total_documents}\n")
        
        if not schema.fields:
            lines.append("*Поля не найдены*")
            return "\n".join(lines)
        
        lines.append("### Поля frontmatter\n")
        lines.append("| Поле | Тип | Документов | Уникальных | Примеры значений |")
        lines.append("|------|-----|------------|------------|------------------|")
        
        for field_name, info in sorted(schema.fields.items()):
            examples = ", ".join(f"`{v}`" for v in info.unique_values[:5])
            if info.unique_count > 5:
                examples += f" ... (+{info.unique_count - 5})"
            
            lines.append(
                f"| {field_name} | {info.field_type} | {info.document_count} | "
                f"{info.unique_count} | {examples} |"
            )
        
        if schema.common_patterns:
            lines.append("\n### Частые комбинации полей\n")
            for pattern in schema.common_patterns:
                lines.append(f"- {pattern}")
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Error getting vault schema: {e}")
        return f"Ошибка получения схемы vault'а: {e}"


@mcp.tool()
async def list_by_property(
    vault_name: str,
    property_key: str,
    property_value: str | None = None,
    limit: int = 50,
) -> str:
    """Получить документы по значению свойства frontmatter.
    
    Позволяет искать по любому полю frontmatter, не только по стандартным
    (type, tags). Если property_value не указан, возвращает все документы
    с этим полем.
    
    Args:
        vault_name: Имя vault'а
        property_key: Имя свойства (например "status", "role", "project", "priority")
        property_value: Значение свойства (если None — все документы с этим полем)
        limit: Максимум результатов (default: 50)
    
    Returns:
        Список документов с запрошенным свойством
    
    Examples:
        list_by_property("vault", "status", "in-progress")  # Документы со статусом
        list_by_property("vault", "role")  # Все документы с полем role
        list_by_property("vault", "priority", "high", limit=10)
    """
    if get_service_container().mcp_rate_limiter:
        await get_service_container().mcp_rate_limiter.acquire()
    
    try:
        api = get_service_container().frontmatter_api
        results = await api.list_by_property(vault_name, property_key, property_value, limit)
        
        value_filter = f" = {property_value}" if property_value else ""
        lines = [f"## Документы: {property_key}{value_filter}\n"]
        lines.append(f"**Найдено:** {len(results)} документов\n")
        
        if not results:
            lines.append("*Документы не найдены*")
            return "\n".join(lines)
        
        for doc in results:
            title = doc.get("title") or doc.get("file_path", "Без названия")
            file_path = doc.get("file_path", "")
            modified = doc.get("modified_at")
            modified_str = modified.strftime("%Y-%m-%d") if modified else "—"
            
            lines.append(f"- **{title}**")
            lines.append(f"  - Путь: `{file_path}`")
            lines.append(f"  - Изменён: {modified_str}")
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Error listing by property: {e}")
        return f"Ошибка получения документов по свойству: {e}"


@mcp.tool()
async def aggregate_by_property(
    vault_name: str,
    property_key: str,
    doc_type: str | None = None,
) -> str:
    """Агрегация по свойству — количество документов для каждого значения.
    
    Полезно для получения статистики по vault'у: распределение по статусам,
    приоритетам, ролям и т.д.
    
    Args:
        vault_name: Имя vault'а
        property_key: Имя свойства для группировки (status, priority, role, etc.)
        doc_type: Опционально — ограничить типом документа
    
    Returns:
        Таблица: значение → количество документов
    
    Examples:
        aggregate_by_property("vault", "status")  # Распределение по статусам
        aggregate_by_property("vault", "priority", "task")  # Приоритеты задач
        aggregate_by_property("vault", "role", "person")  # Роли людей
    """
    if get_service_container().mcp_rate_limiter:
        await get_service_container().mcp_rate_limiter.acquire()
    
    try:
        api = get_service_container().frontmatter_api
        result = await api.aggregate_by_property(vault_name, property_key, doc_type)
        
        type_filter = f" (type: {doc_type})" if doc_type else ""
        lines = [f"## Агрегация: {property_key}{type_filter}\n"]
        lines.append(f"**Всего документов:** {result.total_documents}\n")
        
        if not result.values:
            lines.append("*Значения не найдены*")
            return "\n".join(lines)
        
        lines.append("| Значение | Количество | % |")
        lines.append("|----------|------------|---|")
        
        total = result.total_documents
        for value, count in sorted(result.values.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"| {value} | {count} | {percentage:.1f}% |")
        
        if result.null_count > 0:
            percentage = (result.null_count / total * 100) if total > 0 else 0
            lines.append(f"| *(пусто)* | {result.null_count} | {percentage:.1f}% |")
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Error aggregating by property: {e}")
        return f"Ошибка агрегации по свойству: {e}"


@mcp.tool()
async def dataview_query(
    vault_name: str,
    query: str | None = None,
    select: str = "*",
    from_type: str | None = None,
    from_path: str | None = None,
    where: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "desc",
    limit: int = 50,
) -> str:
    """SQL-подобный запрос по документам vault'а (Dataview-style).
    
    Можно использовать либо полный SQL-like синтаксис в параметре `query`,
    либо отдельные параметры.
    
    Args:
        vault_name: Имя vault'а
        query: Полный SQL-like запрос (если указан, остальные параметры игнорируются)
               Пример: "SELECT title, status FROM type:task WHERE status != done SORT BY priority DESC"
        select: Поля через запятую (по умолчанию "*")
        from_type: Фильтр по типу документа
        from_path: Фильтр по пути (например "Projects/Alpha")
        where: Условия фильтрации (status != done, priority > 2)
        sort_by: Поле для сортировки
        sort_order: Порядок сортировки (asc/desc)
        limit: Максимум результатов (default: 50)
    
    Returns:
        Таблица результатов в markdown формате
    
    Examples:
        # Полный SQL-like синтаксис
        dataview_query("vault", query="SELECT * FROM type:1-1 WHERE status != done SORT BY date DESC")
        
        # Отдельные параметры
        dataview_query("vault", from_type="person", where="role = manager", sort_by="name")
        
        # Комбинация
        dataview_query("vault", select="title,status", from_path="Projects", where="status = active")
    """
    if get_service_container().mcp_rate_limiter:
        await get_service_container().mcp_rate_limiter.acquire()
    
    try:
        service = get_service_container().dataview_service
        
        if query:
            # Используем полный SQL-like синтаксис
            result = await service.query_string(vault_name, query)
        else:
            # Собираем DataviewQuery из параметров
            from obsidian_kb.interfaces import DataviewQuery
            from obsidian_kb.query.where_parser import WhereParser
            
            select_fields = [s.strip() for s in select.split(",")] if select != "*" else ["*"]
            where_conditions = WhereParser.parse(where) if where else None
            
            dv_query = DataviewQuery(
                select=select_fields,
                from_type=from_type,
                from_path=from_path,
                where=where_conditions,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=limit,
            )
            result = await service.query(vault_name, dv_query)
        
        # Форматируем результат
        lines = ["## Dataview Query Results\n"]
        lines.append(f"**Запрос:** `{result.query_string}`")
        lines.append(f"**Найдено:** {result.total_count} документов")
        lines.append(f"**Время:** {result.query_time_ms:.1f} мс\n")
        
        if not result.documents:
            lines.append("*Документы не найдены*")
            return "\n".join(lines)
        
        # Определяем колонки для таблицы
        if result.documents:
            columns = list(result.documents[0].keys())
            # Убираем служебные поля
            columns = [c for c in columns if not c.startswith("_") and c != "document_id"]
            
            # Формируем таблицу
            lines.append("| " + " | ".join(columns) + " |")
            lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
            
            for doc in result.documents:
                values = []
                for col in columns:
                    val = doc.get(col, "")
                    if isinstance(val, list):
                        val = ", ".join(str(v) for v in val)
                    elif val is None:
                        val = "—"
                    else:
                        val = str(val)[:50]  # Обрезаем длинные значения
                    values.append(val)
                lines.append("| " + " | ".join(values) + " |")
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Error executing dataview query: {e}", exc_info=True)
        return f"Ошибка выполнения Dataview запроса: {e}"


# NOTE: search_help is now auto-registered via MCPTool class
# See: src/obsidian_kb/mcp/tools/search_help_tool.py


@mcp.tool()
async def delete_vault(vault_name: str) -> str:
    """Удалить vault из индекса (удаляет все данные vault'а из базы данных).

    Внимание: Это удалит все данные vault'а из базы данных, но не затронет файлы в vault'е.

    Args:
        vault_name: Имя vault'а для удаления

    Returns:
        Результат удаления
    """
    try:
        # Проверяем, существует ли vault
        try:
            await get_service_container().db_manager.get_vault_stats(vault_name)
        except VaultNotFoundError:
            return f"Vault '{vault_name}' не найден в индексе. Удаление не требуется."

        # Очищаем кэш embeddings
        embedding_cache = EmbeddingCache()
        try:
            await embedding_cache.clear_vault_cache(vault_name)
            logger.info(f"Cleared embedding cache for vault '{vault_name}' before deletion")
        except Exception as e:
            logger.warning(f"Failed to clear cache for vault '{vault_name}': {e}")

        # Удаляем vault из базы данных
        await get_service_container().db_manager.delete_vault(vault_name)
        
        return f"Vault '{vault_name}' успешно удалён из индекса. Файлы в vault'е не затронуты."

    except VaultNotFoundError:
        return f"Vault '{vault_name}' не найден в индексе."
    except Exception as e:
        logger.error(f"Error in delete_vault: {e}", exc_info=True)
        return f"Ошибка удаления vault'а: {e}"


async def quick_startup_check() -> None:
    """Быстрая проверка только критичных компонентов при старте."""
    logger.info("Starting obsidian-kb MCP server...")
    
    # Проверяем только Ollama синхронно (быстрая проверка)
    try:
        ollama_check = await get_service_container().diagnostics_service.check_ollama()
        if ollama_check.status == HealthStatus.ERROR:
            logger.error(f"[ollama] {ollama_check.message}")
            raise SystemExit("Ollama недоступна. Запустите: ollama serve")
        logger.info(f"[ollama] {ollama_check.message}")
    except Exception as e:
        logger.warning(f"Ошибка проверки Ollama: {e}")
        # Продолжаем запуск, если проверка не критична


async def background_startup_checks() -> None:
    """Фоновые проверки после запуска сервера."""
    try:
        logger.info("Выполнение фоновых проверок системы...")
        health = await get_service_container().diagnostics_service.full_check()

        if health.overall == HealthStatus.ERROR:
            for check in health.checks:
                if check.status == HealthStatus.ERROR:
                    logger.error(f"[{check.component}] {check.message}")
                    send_notification("obsidian-kb", f"Ошибка: {check.message}")

        elif health.overall == HealthStatus.WARNING:
            for check in health.checks:
                if check.status == HealthStatus.WARNING:
                    logger.warning(f"[{check.component}] {check.message}")

        logger.info(f"Фоновые проверки завершены. Статус: {health.overall.value}")
    except Exception as e:
        logger.error(f"Ошибка фоновых проверок: {e}")


# Алиас для обратной совместимости (lifespan использует _background_startup_checks)
_background_startup_checks = background_startup_checks


def main() -> None:
    """Точка входа для запуска MCP сервера."""
    # Настраиваем структурированное логирование
    # MCP Server по умолчанию использует JSON для машинного парсинга
    from obsidian_kb.structured_logging import setup_structured_logging
    setup_structured_logging(level=logging.INFO, json_format=True)

    # Выполняем только быструю проверку критичных компонентов
    try:
        asyncio.run(quick_startup_check())
    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Продолжаем запуск даже при ошибках startup

    # Запускаем сервер (lifespan управляет фоновыми сервисами)
    mcp.run()


def _get_vault_path_from_name(vault_name: str) -> str | None:
    """Получить путь к vault'у по его имени из конфигурации.
    
    Args:
        vault_name: Имя vault'а
    
    Returns:
        Путь к vault'у или None если не найден
    """
    try:
        config_path = settings.vaults_config
        if not config_path.exists():
            return None
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        vaults = config.get("vaults", [])
        for v in vaults:
            if v.get("name") == vault_name:
                return v.get("path")

        return None
    except Exception as e:
        logger.debug(f"Failed to get vault path from config for {vault_name}: {e}")
        return None


@mcp.tool()
@with_rate_limit
async def search_text(
    vault_name: str,
    query: str,
    case_sensitive: bool = False,
    whole_word: bool = False,
    context_lines: int = 2,
    file_pattern: str = "*.md",
    max_results: int = 100
) -> str:
    """Текстовый поиск по файлам vault'а (ripgrep/grep/python fallback).
    
    Прямой текстовый поиск без использования индекса. Использует ripgrep если доступен,
    иначе fallback на grep или pure Python поиск.
    
    Args:
        vault_name: Имя vault'а
        query: Текст для поиска
        case_sensitive: Учитывать регистр (default: False)
        whole_word: Искать целые слова (default: False)
        context_lines: Количество строк контекста до/после (default: 2)
        file_pattern: Паттерн файлов для поиска (default: "*.md")
        max_results: Максимум результатов (default: 100)
    
    Returns:
        Форматированные результаты поиска в markdown формате
    
    Examples:
        search_text("vault", "async def")
        search_text("vault", "TODO", whole_word=True, context_lines=3)
        search_text("vault", "test", file_pattern="*.py")
    """
    try:
        # Получаем путь к vault'у
        vault_path = _get_vault_path_from_name(vault_name)
        if not vault_path:
            return f"Ошибка: Vault '{vault_name}' не найден в конфигурации."
        
        vault_path_obj = Path(vault_path)
        if not vault_path_obj.exists():
            return f"Ошибка: Путь к vault'у '{vault_path}' не существует."
        
        # Выполняем поиск
        service = get_service_container().ripgrep_service
        result = await service.search_text(
            vault_path=str(vault_path_obj),
            query=query,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
            context_lines=context_lines,
            file_pattern=file_pattern,
            max_results=max_results
        )
        
        # Форматируем результат
        lines = ["## Текстовый поиск\n"]
        lines.append(f"**Запрос:** `{query}`")
        lines.append(f"**Найдено:** {result.total_matches} совпадений в {result.files_searched} файлах")
        lines.append(f"**Время:** {result.search_time_ms:.1f} мс")
        lines.append(f"**Инструмент:** {'ripgrep' if service.is_ripgrep_available() else 'grep/python'}\n")
        
        if not result.matches:
            lines.append("*Совпадения не найдены*")
            return "\n".join(lines)
        
        # Группируем по файлам
        matches_by_file: dict[str, list[RipgrepMatch]] = {}
        for match in result.matches:
            if match.file_path not in matches_by_file:
                matches_by_file[match.file_path] = []
            matches_by_file[match.file_path].append(match)
        
        for file_path, file_matches in list(matches_by_file.items())[:20]:  # Максимум 20 файлов
            lines.append(f"### {file_path}")
            
            for match in file_matches[:10]:  # Максимум 10 совпадений на файл
                lines.append(f"\n**Строка {match.line_number}:**")
                
                # Контекст до
                if match.context_before:
                    for ctx_line in match.context_before:
                        lines.append(f"  {ctx_line}")
                
                # Строка с совпадением
                line_pre = match.line_content[:match.match_start]
                line_match = match.line_content[match.match_start:match.match_end]
                line_post = match.line_content[match.match_end:]
                lines.append(f"  {line_pre}**{line_match}**{line_post}")
                
                # Контекст после
                if match.context_after:
                    for ctx_line in match.context_after:
                        lines.append(f"  {ctx_line}")
                
                lines.append("")
            
            if len(file_matches) > 10:
                lines.append(f"*... и ещё {len(file_matches) - 10} совпадений в этом файле*\n")
        
        if len(matches_by_file) > 20:
            lines.append(f"\n*... и ещё {len(matches_by_file) - 20} файлов с совпадениями*")
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.error(f"Error in search_text: {e}", exc_info=True)
        return f"Ошибка текстового поиска: {e}"


@mcp.tool()
@with_rate_limit
async def search_regex(
    vault_name: str,
    pattern: str,
    context_lines: int = 2,
    file_pattern: str = "*.md",
    max_results: int = 100
) -> str:
    """Поиск по regex паттерну в файлах vault'а.
    
    Args:
        vault_name: Имя vault'а
        pattern: Regex паттерн для поиска
        context_lines: Количество строк контекста до/после (default: 2)
        file_pattern: Паттерн файлов для поиска (default: "*.md")
        max_results: Максимум результатов (default: 100)
    
    Returns:
        Форматированные результаты поиска в markdown формате
    
    Examples:
        search_regex("vault", r"def\\s+\\w+\\(")
        search_regex("vault", r"TODO|FIXME", file_pattern="*.py")
    """
    try:
        # Получаем путь к vault'у
        vault_path = _get_vault_path_from_name(vault_name)
        if not vault_path:
            return f"Ошибка: Vault '{vault_name}' не найден в конфигурации."
        
        vault_path_obj = Path(vault_path)
        if not vault_path_obj.exists():
            return f"Ошибка: Путь к vault'у '{vault_path}' не существует."
        
        # Выполняем поиск
        service = get_service_container().ripgrep_service
        result = await service.search_regex(
            vault_path=str(vault_path_obj),
            pattern=pattern,
            context_lines=context_lines,
            file_pattern=file_pattern,
            max_results=max_results
        )
        
        # Форматируем результат
        lines = ["## Regex поиск\n"]
        lines.append(f"**Паттерн:** `{pattern}`")
        lines.append(f"**Найдено:** {result.total_matches} совпадений в {result.files_searched} файлах")
        lines.append(f"**Время:** {result.search_time_ms:.1f} мс")
        lines.append(f"**Инструмент:** {'ripgrep' if service.is_ripgrep_available() else 'python'}\n")
        
        if not result.matches:
            lines.append("*Совпадения не найдены*")
            return "\n".join(lines)
        
        # Группируем по файлам
        matches_by_file: dict[str, list[RipgrepMatch]] = {}
        for match in result.matches:
            if match.file_path not in matches_by_file:
                matches_by_file[match.file_path] = []
            matches_by_file[match.file_path].append(match)
        
        for file_path, file_matches in list(matches_by_file.items())[:20]:  # Максимум 20 файлов
            lines.append(f"### {file_path}")
            
            for match in file_matches[:10]:  # Максимум 10 совпадений на файл
                lines.append(f"\n**Строка {match.line_number}:**")
                
                # Контекст до
                if match.context_before:
                    for ctx_line in match.context_before:
                        lines.append(f"  {ctx_line}")
                
                # Строка с совпадением
                line_pre = match.line_content[:match.match_start]
                line_match = match.line_content[match.match_start:match.match_end]
                line_post = match.line_content[match.match_end:]
                lines.append(f"  {line_pre}**{line_match}**{line_post}")
                
                # Контекст после
                if match.context_after:
                    for ctx_line in match.context_after:
                        lines.append(f"  {ctx_line}")
                
                lines.append("")
            
            if len(file_matches) > 10:
                lines.append(f"*... и ещё {len(file_matches) - 10} совпадений в этом файле*\n")
        
        if len(matches_by_file) > 20:
            lines.append(f"\n*... и ещё {len(matches_by_file) - 20} файлов с совпадениями*")
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.error(f"Error in search_regex: {e}", exc_info=True)
        return f"Ошибка regex поиска: {e}"


@mcp.tool()
@with_rate_limit
async def find_files(
    vault_name: str,
    name_pattern: str,
    content_contains: str | None = None
) -> str:
    """Поиск файлов по имени и/или содержимому.
    
    Args:
        vault_name: Имя vault'а
        name_pattern: Паттерн имени файла (например, "*.md" или "**/test*.md")
        content_contains: Опционально — текст, который должен содержаться в файле
    
    Returns:
        Список найденных файлов в markdown формате
    
    Examples:
        find_files("vault", "*.md")
        find_files("vault", "**/test*.py", content_contains="async def")
        find_files("vault", "README.md")
    """
    try:
        # Получаем путь к vault'у
        vault_path = _get_vault_path_from_name(vault_name)
        if not vault_path:
            return f"Ошибка: Vault '{vault_name}' не найден в конфигурации."
        
        vault_path_obj = Path(vault_path)
        if not vault_path_obj.exists():
            return f"Ошибка: Путь к vault'у '{vault_path}' не существует."
        
        # Выполняем поиск
        service = get_service_container().ripgrep_service
        files = await service.find_files(
            vault_path=str(vault_path_obj),
            name_pattern=name_pattern,
            content_contains=content_contains
        )
        
        # Форматируем результат
        lines = ["## Поиск файлов\n"]
        lines.append(f"**Паттерн:** `{name_pattern}`")
        if content_contains:
            lines.append(f"**Содержит текст:** `{content_contains}`")
        lines.append(f"**Найдено:** {len(files)} файлов\n")
        
        if not files:
            lines.append("*Файлы не найдены*")
            return "\n".join(lines)
        
        for file_path in files[:100]:  # Максимум 100 файлов
            lines.append(f"- `{file_path}`")
        
        if len(files) > 100:
            lines.append(f"\n*... и ещё {len(files) - 100} файлов*")
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.error(f"Error in find_files: {e}", exc_info=True)
        return f"Ошибка поиска файлов: {e}"


# ============================================================================
# Graph Query Service MCP Tools (v6 Phase 4)
# ============================================================================


@mcp.tool()
@with_rate_limit
async def find_connected(
    vault_name: str,
    document_path: str,
    direction: str = "both",
    depth: int = 1,
    limit: int = 50
) -> str:
    """Найти документы, связанные с указанным через wikilinks.
    
    Args:
        vault_name: Имя vault'а
        document_path: Путь к документу (относительный от корня vault)
        direction: "incoming" (кто ссылается), "outgoing" (на кого ссылается), "both"
        depth: Глубина поиска (1 = прямые связи, 2 = связи связей)
        limit: Максимум результатов
    
    Returns:
        Список связанных документов в markdown формате
    
    Examples:
        find_connected("vault", "People/Иван.md")  # Все связи
        find_connected("vault", "Projects/Alpha.md", "incoming")  # Кто ссылается на проект
        find_connected("vault", "Notes/Meeting.md", "outgoing")  # На кого ссылается встреча
    """
    try:
        service = get_service_container().graph_query_service
        result = await service.find_connected(
            vault_name=vault_name,
            document_path=document_path,
            direction=direction,
            depth=depth,
            limit=limit
        )
        
        # Форматируем результат
        lines = [f"## Связанные документы: `{result.center_document}`\n"]
        lines.append(f"**Направление:** {direction}")
        lines.append(f"**Глубина:** {depth}")
        lines.append(f"**Входящие ссылки:** {result.total_incoming}")
        lines.append(f"**Исходящие ссылки:** {result.total_outgoing}")
        lines.append(f"**Найдено:** {len(result.connected)} документов\n")
        
        if not result.connected:
            lines.append("*Связанные документы не найдены*")
            return "\n".join(lines)
        
        # Группируем по направлению
        incoming = [d for d in result.connected if d.direction == "incoming"]
        outgoing = [d for d in result.connected if d.direction == "outgoing"]
        
        if incoming:
            lines.append("### Входящие ссылки (кто ссылается на этот документ)\n")
            for doc in incoming:
                lines.append(f"- **{doc.title}** (`{doc.file_path}`)")
                if doc.link_context:
                    lines.append(f"  > {doc.link_context}")
            lines.append("")
        
        if outgoing:
            lines.append("### Исходящие ссылки (на кого ссылается этот документ)\n")
            for doc in outgoing:
                lines.append(f"- **{doc.title}** (`{doc.file_path}`)")
                if doc.link_context:
                    lines.append(f"  > {doc.link_context}")
            lines.append("")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"Ошибка: Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in find_connected: {e}", exc_info=True)
        return f"Ошибка поиска связанных документов: {e}"


@mcp.tool()
@with_rate_limit
async def find_orphans(
    vault_name: str,
    doc_type: str | None = None
) -> str:
    """Найти документы без входящих ссылок (orphans).
    
    Полезно для аудита базы знаний — orphans могут быть забытыми
    или требовать интеграции.
    
    Args:
        vault_name: Имя vault'а
        doc_type: Опционально — ограничить типом документа
    
    Returns:
        Список orphan документов в markdown формате
    
    Examples:
        find_orphans("vault")  # Все orphans
        find_orphans("vault", "note")  # Только заметки без ссылок
    """
    try:
        service = get_service_container().graph_query_service
        orphans = await service.find_orphans(
            vault_name=vault_name,
            doc_type=doc_type
        )
        
        # Форматируем результат
        lines = [f"## Orphan документы: {vault_name}\n"]
        if doc_type:
            lines.append(f"**Тип:** {doc_type}")
        lines.append(f"**Найдено:** {len(orphans)} документов\n")
        
        if not orphans:
            lines.append("*Orphan документы не найдены*")
            return "\n".join(lines)
        
        for file_path in orphans[:100]:  # Максимум 100
            lines.append(f"- `{file_path}`")
        
        if len(orphans) > 100:
            lines.append(f"\n*... и ещё {len(orphans) - 100} документов*")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"Ошибка: Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in find_orphans: {e}", exc_info=True)
        return f"Ошибка поиска orphan документов: {e}"


@mcp.tool()
@with_rate_limit
async def find_broken_links(
    vault_name: str
) -> str:
    """Найти битые wikilinks — ссылки на несуществующие документы.
    
    Args:
        vault_name: Имя vault'а
    
    Returns:
        Список битых ссылок в markdown формате
    
    Examples:
        find_broken_links("vault")  # Все битые ссылки
    """
    try:
        service = get_service_container().graph_query_service
        broken_links = await service.find_broken_links(vault_name=vault_name)
        
        # Форматируем результат
        lines = [f"## Битые ссылки: {vault_name}\n"]
        lines.append(f"**Найдено:** {len(broken_links)} битых ссылок\n")
        
        if not broken_links:
            lines.append("*Битые ссылки не найдены*")
            return "\n".join(lines)
        
        # Группируем по файлу
        by_file: dict[str, list[str]] = {}
        for file_path, broken_link in broken_links:
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(broken_link)
        
        for file_path, links in list(by_file.items())[:50]:  # Максимум 50 файлов
            lines.append(f"### `{file_path}`\n")
            for link in links:
                lines.append(f"- `{link}`")
            lines.append("")
        
        if len(by_file) > 50:
            lines.append(f"*... и ещё {len(by_file) - 50} файлов с битыми ссылками*")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"Ошибка: Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in find_broken_links: {e}", exc_info=True)
        return f"Ошибка поиска битых ссылок: {e}"


@mcp.tool()
@with_rate_limit
async def get_backlinks(
    vault_name: str,
    document_path: str
) -> str:
    """Получить все backlinks (входящие ссылки) для документа.
    
    Аналог панели Backlinks в Obsidian.
    
    Args:
        vault_name: Имя vault'а
        document_path: Путь к документу
    
    Returns:
        Список backlinks в markdown формате
    
    Examples:
        get_backlinks("vault", "People/Иван.md")  # Все кто ссылается на профиль
    """
    try:
        service = get_service_container().graph_query_service
        backlinks = await service.get_backlinks(
            vault_name=vault_name,
            document_path=document_path
        )
        
        # Форматируем результат
        lines = [f"## Backlinks: `{document_path}`\n"]
        lines.append(f"**Найдено:** {len(backlinks)} документов\n")
        
        if not backlinks:
            lines.append("*Backlinks не найдены*")
            return "\n".join(lines)
        
        for doc in backlinks:
            lines.append(f"- **{doc.title}** (`{doc.file_path}`)")
            if doc.link_context:
                lines.append(f"  > {doc.link_context}")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"Ошибка: Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in get_backlinks: {e}", exc_info=True)
        return f"Ошибка получения backlinks: {e}"


# ============================================================================
# Timeline Service MCP Tools (v6 Phase 4)
# ============================================================================


@mcp.tool()
@with_rate_limit
async def timeline(
    vault_name: str,
    doc_type: str | None = None,
    date_field: str = "created",
    after: str | None = None,
    before: str | None = None,
    limit: int = 50
) -> str:
    """Хронологическая лента документов.
    
    Args:
        vault_name: Имя vault'а
        doc_type: Опционально — фильтр по типу
        date_field: Поле для сортировки ("created", "modified" или кастомное)
        after: Документы после даты (ISO или "last_week", "last_month")
        before: Документы до даты
        limit: Максимум результатов
    
    Returns:
        Хронологическая лента в markdown формате
    
    Examples:
        timeline("vault", "meeting", date_field="date", after="2024-12-01")
        timeline("vault", after="last_week")  # Созданные за неделю
        timeline("vault", doc_type="task", date_field="modified")  # Изменённые задачи
    """
    try:
        service = get_service_container().timeline_service
        results = await service.timeline(
            vault_name=vault_name,
            doc_type=doc_type,
            date_field=date_field,
            after=after,
            before=before,
            limit=limit
        )
        
        # Форматируем результат
        lines = [f"## Timeline: {vault_name}\n"]
        if doc_type:
            lines.append(f"**Тип:** {doc_type}")
        lines.append(f"**Поле даты:** {date_field}")
        if after:
            lines.append(f"**После:** {after}")
        if before:
            lines.append(f"**До:** {before}")
        lines.append(f"**Найдено:** {len(results)} документов\n")
        
        if not results:
            lines.append("*Документы не найдены*")
            return "\n".join(lines)
        
        for doc in results:
            date_value = doc.get(date_field) or doc.get("created_at") or doc.get("modified_at")
            lines.append(f"### {doc.get('title', 'Без названия')}")
            lines.append(f"- **Файл:** `{doc.get('file_path', '')}`")
            if date_value:
                lines.append(f"- **Дата:** {date_value}")
            lines.append("")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"Ошибка: Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in timeline: {e}", exc_info=True)
        return f"Ошибка получения timeline: {e}"


@mcp.tool()
@with_rate_limit
async def recent_changes(
    vault_name: str,
    days: int = 7,
    doc_type: str | None = None
) -> str:
    """Документы, изменённые за последние N дней.
    
    Разделяет на созданные и изменённые.
    
    Args:
        vault_name: Имя vault'а
        days: Количество дней (default: 7)
        doc_type: Опционально — фильтр по типу
    
    Returns:
        Список изменений в markdown формате
    
    Examples:
        recent_changes("vault")  # Изменения за неделю
        recent_changes("vault", 30, "task")  # Задачи за месяц
    """
    try:
        service = get_service_container().timeline_service
        result = await service.recent_changes(
            vault_name=vault_name,
            days=days,
            doc_type=doc_type
        )
        
        # Форматируем результат
        lines = [f"## Недавние изменения: {vault_name}\n"]
        lines.append(f"**Период:** последние {days} дней")
        if doc_type:
            lines.append(f"**Тип:** {doc_type}")
        lines.append(f"**Всего:** {result.get('total', 0)} документов\n")
        
        created = result.get("created", [])
        modified = result.get("modified", [])
        
        if created:
            lines.append(f"### Создано ({len(created)})\n")
            for doc in created[:20]:  # Максимум 20
                lines.append(f"- **{doc.get('title', 'Без названия')}** (`{doc.get('file_path', '')}`)")
                if doc.get("created_at"):
                    lines.append(f"  > {doc.get('created_at')}")
            if len(created) > 20:
                lines.append(f"*... и ещё {len(created) - 20} документов*")
            lines.append("")
        
        if modified:
            lines.append(f"### Изменено ({len(modified)})\n")
            for doc in modified[:20]:  # Максимум 20
                lines.append(f"- **{doc.get('title', 'Без названия')}** (`{doc.get('file_path', '')}`)")
                if doc.get("modified_at"):
                    lines.append(f"  > {doc.get('modified_at')}")
            if len(modified) > 20:
                lines.append(f"*... и ещё {len(modified) - 20} документов*")
            lines.append("")
        
        if not created and not modified:
            lines.append("*Изменений не найдено*")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"Ошибка: Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in recent_changes: {e}", exc_info=True)
        return f"Ошибка получения недавних изменений: {e}"


@mcp.tool()
@with_rate_limit
async def export_to_csv(
    vault_name: str,
    output_path: str | None = None,
    doc_type: str | None = None,
    fields: str | None = None,
    where: str | None = None
) -> str:
    """Экспорт данных vault'а в CSV файл.
    
    Args:
        vault_name: Имя vault'а
        output_path: Путь для сохранения (если не указан — временный файл)
        doc_type: Опционально — фильтр по типу
        fields: Поля через запятую (если не указано — все поля)
        where: Условия фильтрации
    
    Returns:
        Путь к созданному CSV файлу
    
    Examples:
        export_to_csv("vault", doc_type="person", fields="title,role,team")
        export_to_csv("vault", where="status = active")
        export_to_csv("vault", output_path="/tmp/export.csv", doc_type="task")
    """
    try:
        batch_ops = get_service_container().batch_operations
        csv_path = await batch_ops.export_to_csv(
            vault_name=vault_name,
            output_path=output_path,
            doc_type=doc_type,
            fields=fields,
            where=where
        )
        
        # Форматируем результат
        lines = [f"## Экспорт данных: {vault_name}\n"]
        lines.append(f"**CSV файл:** `{csv_path}`")
        if doc_type:
            lines.append(f"**Тип документов:** {doc_type}")
        if fields:
            lines.append(f"**Поля:** {fields}")
        if where:
            lines.append(f"**Фильтр:** {where}")
        lines.append(f"\nФайл успешно создан. Используйте путь выше для доступа к файлу.")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"Ошибка: Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in export_to_csv: {e}", exc_info=True)
        return f"Ошибка экспорта в CSV: {e}"


@mcp.tool()
@with_rate_limit
async def compare_schemas(
    vault_names: list[str]
) -> str:
    """Сравнить схемы frontmatter нескольких vault'ов.
    
    Показывает общие поля, уникальные поля и различия в значениях.
    
    Args:
        vault_names: Список имён vault'ов для сравнения
    
    Returns:
        Сравнение схем в markdown формате
    
    Examples:
        compare_schemas(["vault1", "vault2"])
        compare_schemas(["vault1", "vault2", "vault3"])
    """
    try:
        batch_ops = get_service_container().batch_operations
        comparison = await batch_ops.compare_schemas(vault_names)
        
        # Форматируем результат
        lines = ["## Сравнение схем vault'ов\n"]
        lines.append(f"**Vault'ы:** {', '.join(vault_names)}\n")
        
        # Статистика по vault'ам
        lines.append("### Статистика\n")
        vault_stats = comparison.get("vault_stats", {})
        for vault_name, doc_count in vault_stats.items():
            lines.append(f"- **{vault_name}:** {doc_count} документов")
        lines.append("")
        
        # Общие поля
        common_fields = comparison.get("common_fields", [])
        lines.append(f"### Общие поля ({len(common_fields)})\n")
        if common_fields:
            for field in common_fields:
                lines.append(f"- `{field}`")
        else:
            lines.append("*Общих полей не найдено*")
        lines.append("")
        
        # Уникальные поля
        unique_fields = comparison.get("unique_fields", {})
        lines.append("### Уникальные поля\n")
        if unique_fields:
            for vault_name, fields in unique_fields.items():
                if fields:
                    lines.append(f"**{vault_name}:**")
                    for field in fields:
                        lines.append(f"  - `{field}`")
                    lines.append("")
        else:
            lines.append("*Уникальных полей не найдено*")
            lines.append("")
        
        # Различия в значениях
        field_differences = comparison.get("field_differences", {})
        if field_differences:
            lines.append("### Различия в значениях полей\n")
            for field, vault_examples in field_differences.items():
                lines.append(f"**`{field}`:**")
                for vault_name, examples in vault_examples.items():
                    examples_str = ", ".join(str(e) for e in examples[:3])
                    lines.append(f"  - {vault_name}: {examples_str}")
                lines.append("")
        
        return "\n".join(lines)
    
    except VaultNotFoundError as e:
        return f"Ошибка: Vault не найден: {e}"
    except Exception as e:
        logger.error(f"Error in compare_schemas: {e}", exc_info=True)
        return f"Ошибка сравнения схем: {e}"


if __name__ == "__main__":
    main()

