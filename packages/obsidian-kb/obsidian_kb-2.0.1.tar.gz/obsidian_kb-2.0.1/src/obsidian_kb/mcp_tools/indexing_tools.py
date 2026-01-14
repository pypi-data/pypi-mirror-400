"""MCP tools для управления индексацией документов."""

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING

# Объект mcp будет передан из mcp_server.py при регистрации
# Используем глобальную переменную для хранения ссылки на mcp
_mcp_instance = None


def register_mcp(mcp_instance):
    """Регистрация объекта mcp для использования в декораторах.
    
    Args:
        mcp_instance: Экземпляр FastMCP из mcp_server.py
    """
    global _mcp_instance
    _mcp_instance = mcp_instance


def _get_mcp():
    """Получение объекта mcp для декораторов."""
    if _mcp_instance is None:
        raise RuntimeError("MCP instance not registered. Call register_mcp() first.")
    return _mcp_instance

from obsidian_kb.config.manager import get_config_manager
from obsidian_kb.indexing.chunking import ChunkingService, ChunkingStrategy
from obsidian_kb.indexing.orchestrator import (
    EnrichmentStrategy,
    IndexingOrchestrator,
)
from obsidian_kb.service_container import get_service_container
from obsidian_kb.types import VaultNotFoundError

if TYPE_CHECKING:
    from obsidian_kb.storage.chunk_repository import ChunkRepository
    from obsidian_kb.storage.document_repository import DocumentRepository

logger = logging.getLogger(__name__)

# Глобальный контейнер сервисов
services = get_service_container()

# Глобальные оркестраторы по vault'ам (для отслеживания задач)
_orchestrators: dict[str, IndexingOrchestrator] = {}


def _get_orchestrator(vault_name: str) -> IndexingOrchestrator:
    """Получение или создание оркестратора для vault'а.

    Args:
        vault_name: Имя vault'а

    Returns:
        IndexingOrchestrator для vault'а
    """
    if vault_name not in _orchestrators:
        # Получаем провайдеры из ServiceContainer
        embedding_provider = services.embedding_provider
        # Используем enrichment_chat_provider для обогащения контекстом
        chat_provider = services.enrichment_chat_provider

        # Получаем репозитории
        chunk_repository = services.chunk_repository
        document_repository = services.document_repository

        # Получаем ConfigManager
        config_manager = get_config_manager()

        # Создаём оркестратор
        orchestrator = IndexingOrchestrator(
            embedding_provider=embedding_provider,
            chat_provider=chat_provider,
            chunk_repository=chunk_repository,
            document_repository=document_repository,
            config_manager=config_manager,
        )

        _orchestrators[vault_name] = orchestrator

    return _orchestrators[vault_name]


def _get_vault_path(vault_name: str) -> Path:
    """Получение пути к vault'у по имени.
    
    Args:
        vault_name: Имя vault'а
        
    Returns:
        Path к vault'у
        
    Raises:
        ValueError: Если vault не найден в конфигурации
    """
    from obsidian_kb.config import settings
    
    config_path = settings.vaults_config
    if not config_path.exists():
        raise ValueError(f"Конфигурация vault'ов не найдена: {config_path}")
    
    import json
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    vaults = config.get("vaults", [])
    for v in vaults:
        if v.get("name") == vault_name:
            vault_path_str = v.get("path")
            if not vault_path_str:
                raise ValueError(f"Путь для vault '{vault_name}' не указан в конфигурации")
            vault_path = Path(vault_path_str)
            if not vault_path.exists():
                raise ValueError(f"Путь к vault'у не существует: {vault_path}")
            return vault_path
    
    raise ValueError(f"Vault '{vault_name}' не найден в конфигурации")


async def index_documents(
    vault_name: str,
    paths: list[str] | None = None,
    force: bool = False,
    enrichment: str = "contextual",  # none | contextual | full
    background: bool = True,
) -> str:
    """Индексация документов в vault.

    Args:
        vault_name: Имя vault'а
        paths: Список путей для индексации (None = все изменённые)
        force: Принудительная переиндексация даже без изменений
        enrichment: Уровень обогащения:
            - "none": только chunking + embedding
            - "contextual": + context prefix (рекомендуется)
            - "full": + document summary + semantic analysis
        background: Запустить в фоне (True) или синхронно (False)

    Returns:
        Job ID или результат индексации в Markdown формате

    Examples:
        # Индексация всех изменённых файлов
        index_documents("naumen-cto")

        # Принудительная переиндексация конкретных файлов
        index_documents("naumen-cto", paths=["People/Иванов.md"], force=True)

        # Полная переиндексация без обогащения (быстро, дёшево)
        index_documents("naumen-cto", force=True, enrichment="none")
    """
    try:
        # Получаем путь к vault'у
        vault_path = _get_vault_path(vault_name)

        if background:
            # Используем BackgroundJobQueue для регистрации и выполнения задачи
            from obsidian_kb.mcp_server import get_job_queue
            from obsidian_kb.indexing.job_queue import JobPriority

            job_queue = get_job_queue()
            if not job_queue:
                return "❌ Ошибка: Очередь фоновых задач недоступна."

            # Регистрируем задачу в job_queue
            job = await job_queue.enqueue(
                vault_name=vault_name,
                vault_path=vault_path,
                operation="index_documents",
                params={
                    "paths": paths,
                    "force": force,
                    "enrichment": enrichment.lower(),
                },
                priority=JobPriority.NORMAL,
            )

            lines = ["## Индексация запущена\n"]
            lines.append(f"- **Job ID:** `{job.id}`")
            lines.append(f"- **Vault:** {vault_name}")
            lines.append(f"- **Статус:** {job.status.value}")
            lines.append(f"- **Обогащение:** {enrichment}")
            lines.append(f"\nИспользуйте `get_job_status(job_id=\"{job.id}\")` для отслеживания прогресса.")

            return "\n".join(lines)
        else:
            # Синхронное выполнение через orchestrator
            orchestrator = _get_orchestrator(vault_name)

            # Конвертируем enrichment string в EnrichmentStrategy
            enrichment_strategy_map = {
                "none": EnrichmentStrategy.NONE,
                "contextual": EnrichmentStrategy.CONTEXTUAL,
                "full": EnrichmentStrategy.FULL,
            }
            enrichment_strategy = enrichment_strategy_map.get(
                enrichment.lower(), EnrichmentStrategy.CONTEXTUAL
            )

            # Конвертируем paths в Path объекты если указаны
            path_objects: list[Path] | None = None
            if paths:
                path_objects = []
                for p in paths:
                    path_obj = Path(p)
                    if not path_obj.is_absolute():
                        path_obj = vault_path / path_obj
                    path_objects.append(path_obj)

            # Создаём и выполняем задачу синхронно
            job = await orchestrator.create_job(
                vault_name=vault_name,
                vault_path=vault_path,
                paths=path_objects,
                force=force,
                enrichment=enrichment_strategy,
            )

            result = await orchestrator.run_job(job.id)

            lines = ["## Индексация завершена\n"]
            lines.append(f"- **Job ID:** `{result.job_id}`")
            lines.append(f"- **Обработано:** {result.documents_processed}/{result.documents_total}")
            lines.append(f"- **Создано чанков:** {result.chunks_created}")
            lines.append(f"- **Длительность:** {result.duration_seconds:.1f} сек")

            if result.errors:
                lines.append(f"\n**Ошибки:** {len(result.errors)}")
                for error in result.errors[:5]:
                    lines.append(f"  - {error}")
                if len(result.errors) > 5:
                    lines.append(f"  ... и ещё {len(result.errors) - 5} ошибок")

            return "\n".join(lines)

    except ValueError as e:
        return f"❌ Ошибка: {e}"
    except Exception as e:
        logger.error(f"Error in index_documents: {e}", exc_info=True)
        return f"❌ Ошибка индексации: {e}"


async def _run_job_background(orchestrator: IndexingOrchestrator, job_id: str) -> None:
    """Запуск задачи индексации в фоне."""
    try:
        await orchestrator.run_job(job_id)
    except Exception as e:
        logger.error(f"Background job {job_id} failed: {e}", exc_info=True)


async def reindex_vault(
    vault_name: str,
    confirm: bool = False,
    enrichment: str = "contextual",
) -> str:
    """Полная переиндексация vault'а.

    ⚠️ Удаляет существующий индекс и создаёт заново.

    Args:
        vault_name: Имя vault'а
        confirm: Подтверждение операции (требуется True)
        enrichment: Уровень обогащения

    Returns:
        Job ID для отслеживания прогресса
    """
    if not confirm:
        return (
            "⚠️ **Требуется подтверждение**\n\n"
            "Полная переиндексация удалит существующий индекс и создаст заново.\n"
            f"Используйте `reindex_vault(vault_name=\"{vault_name}\", confirm=True)` для подтверждения."
        )

    try:
        # Получаем путь к vault'у
        vault_path = _get_vault_path(vault_name)

        # Используем BackgroundJobQueue для регистрации и выполнения задачи
        from obsidian_kb.mcp_server import get_job_queue
        from obsidian_kb.indexing.job_queue import JobPriority

        job_queue = get_job_queue()
        if not job_queue:
            return "❌ Ошибка: Очередь фоновых задач недоступна."

        # Регистрируем задачу в job_queue
        job = await job_queue.enqueue(
            vault_name=vault_name,
            vault_path=vault_path,
            operation="reindex_vault",
            params={
                "enrichment": enrichment.lower(),
                "clear_before_reindex": True,  # Флаг для очистки перед переиндексацией
            },
            priority=JobPriority.NORMAL,
        )

        lines = ["## Переиндексация запущена\n"]
        lines.append(f"- **Job ID:** `{job.id}`")
        lines.append(f"- **Vault:** {vault_name}")
        lines.append(f"- **Статус:** {job.status.value}")
        lines.append(f"- **Обогащение:** {enrichment}")
        lines.append(f"\nИспользуйте `get_job_status(job_id=\"{job.id}\")` для отслеживания прогресса.")

        return "\n".join(lines)

    except ValueError as e:
        return f"❌ Ошибка: {e}"
    except Exception as e:
        logger.error(f"Error in reindex_vault: {e}", exc_info=True)
        return f"❌ Ошибка переиндексации: {e}"


async def index_status(
    vault_name: str | None = None,
    job_id: str | None = None,
) -> str:
    """Статус индексации.
    
    Args:
        vault_name: Показать статус для vault'а (все активные задачи)
        job_id: Показать статус конкретной задачи
    
    Returns:
        Markdown с информацией о статусе:
        - Активные задачи индексации
        - Прогресс (документов обработано / всего)
        - Ошибки если есть
        - Оценка времени завершения
    """
    try:
        if job_id:
            # Ищем задачу по ID во всех оркестраторах
            job = None
            found_vault = None
            
            for vault, orchestrator in _orchestrators.items():
                job = orchestrator.get_job(job_id)
                if job:
                    found_vault = vault
                    break
            
            if not job:
                return f"❌ Задача `{job_id}` не найдена."
            
            lines = [f"## Статус задачи: {job_id}\n"]
            lines.append(f"- **Vault:** {found_vault}")
            lines.append(f"- **Статус:** {job.status}")
            lines.append(f"- **Прогресс:** {job.documents_processed}/{job.documents_total} ({job.progress * 100:.1f}%)")
            lines.append(f"- **Обогащение:** {job.enrichment.value}")
            
            if job.started_at:
                lines.append(f"- **Начато:** {job.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if job.completed_at:
                lines.append(f"- **Завершено:** {job.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
                duration = (job.completed_at - job.started_at).total_seconds() if job.started_at else 0
                lines.append(f"- **Длительность:** {duration:.1f} сек")
            elif job.started_at:
                # Оценка времени завершения
                from datetime import datetime
                now = datetime.now()
                elapsed = (now - job.started_at).total_seconds() if job.started_at else 0
                if job.progress > 0 and elapsed > 0:
                    estimated_total = elapsed / job.progress if job.progress > 0 else 0
                    estimated_remaining = estimated_total - elapsed
                    if estimated_remaining > 0:
                        lines.append(f"- **Осталось:** ~{estimated_remaining:.0f} сек")
            
            if job.errors:
                lines.append(f"\n**Ошибки:** {len(job.errors)}")
                for error in job.errors[:5]:
                    lines.append(f"  - {error}")
                if len(job.errors) > 5:
                    lines.append(f"  ... и ещё {len(job.errors) - 5} ошибок")
            
            return "\n".join(lines)
        
        elif vault_name:
            # Показываем все активные задачи для vault'а
            orchestrator = _get_orchestrator(vault_name)
            
            # Получаем все задачи для vault'а
            # Используем прямой доступ к _jobs, так как это допустимо в рамках пакета
            active_jobs = []
            if hasattr(orchestrator, '_jobs'):
                for job in orchestrator._jobs.values():
                    if job.vault_name == vault_name and job.status in ("pending", "running"):
                        active_jobs.append(job)
            
            if not active_jobs:
                return f"## Статус индексации: {vault_name}\n\n*Нет активных задач индексации*"
            
            lines = [f"## Активные задачи индексации: {vault_name}\n"]
            
            for job in active_jobs:
                lines.append(f"### Job ID: `{job.id}`")
                lines.append(f"- **Статус:** {job.status}")
                lines.append(f"- **Прогресс:** {job.documents_processed}/{job.documents_total} ({job.progress * 100:.1f}%)")
                lines.append(f"- **Обогащение:** {job.enrichment.value}")
                if job.started_at:
                    lines.append(f"- **Начато:** {job.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append("")
            
            return "\n".join(lines)
        
        else:
            return "❌ Укажите либо `vault_name`, либо `job_id`"
    
    except ValueError as e:
        return f"❌ Ошибка: {e}"
    except Exception as e:
        logger.error(f"Error in index_status: {e}", exc_info=True)
        return f"❌ Ошибка получения статуса: {e}"


async def preview_chunks(
    vault_name: str,
    file_path: str,
    strategy: str = "auto",  # auto | headers | semantic | fixed
) -> str:
    """Превью разбиения документа на чанки (без сохранения).
    
    Полезно для понимания как будет разбит документ.
    
    Args:
        vault_name: Имя vault'а
        file_path: Путь к файлу (относительный от корня vault)
        strategy: Стратегия chunking
    
    Returns:
        Markdown с превью чанков:
        - Количество чанков
        - Размер каждого чанка (токены)
        - Первые 100 символов каждого чанка
        - Рекомендации по улучшению
    """
    try:
        # Получаем путь к vault'у
        vault_path = _get_vault_path(vault_name)
        
        # Определяем полный путь к файлу
        file_path_obj = Path(file_path)
        if not file_path_obj.is_absolute():
            file_path_obj = vault_path / file_path_obj
        
        if not file_path_obj.exists():
            return f"❌ Файл не найден: {file_path_obj}"
        
        # Читаем файл
        from obsidian_kb.file_parsers import extract_text_from_file
        
        content = extract_text_from_file(file_path_obj)
        if not content:
            return f"❌ Не удалось прочитать файл: {file_path_obj}"
        
        # Парсим frontmatter для получения body
        from obsidian_kb.frontmatter_parser import FrontmatterParser
        
        _, body = FrontmatterParser.parse(content, str(file_path_obj))
        
        # Получаем ConfigManager и конфигурацию
        config_manager = get_config_manager()
        config = config_manager.get_config(vault_name)
        
        # Создаём ChunkingService
        chat_provider = services.chat_provider
        chunking_service = ChunkingService(
            chat_provider=chat_provider,
            config=config.indexing,
        )
        
        # Конвертируем strategy string в ChunkingStrategy
        strategy_map = {
            "auto": ChunkingStrategy.AUTO,
            "headers": ChunkingStrategy.HEADERS,
            "semantic": ChunkingStrategy.SEMANTIC,
            "fixed": ChunkingStrategy.FIXED,
        }
        chunking_strategy = strategy_map.get(strategy.lower(), ChunkingStrategy.AUTO)
        
        # Разбиваем на чанки
        chunks = await chunking_service.chunk_document(body, chunking_strategy)
        
        if not chunks:
            return f"## Превью разбиения: {file_path}\n\n*Чанки не найдены*"
        
        lines = [f"## Превью разбиения: {file_path}\n"]
        lines.append(f"- **Стратегия:** {strategy}")
        lines.append(f"- **Количество чанков:** {len(chunks)}")
        lines.append(f"- **Общий размер:** {sum(c.token_count for c in chunks)} токенов\n")
        
        # Показываем каждый чанк
        for i, chunk in enumerate(chunks, 1):
            lines.append(f"### Чанк {i}")
            lines.append(f"- **Размер:** {chunk.token_count} токенов")
            lines.append(f"- **Тип:** {chunk.chunk_type}")
            if chunk.headers:
                lines.append(f"- **Заголовки:** {' > '.join(chunk.headers)}")
            
            # Первые 100 символов
            preview_text = chunk.text[:100].replace("\n", " ")
            if len(chunk.text) > 100:
                preview_text += "..."
            lines.append(f"- **Превью:** {preview_text}")
            lines.append("")
        
        # Рекомендации
        lines.append("### Рекомендации\n")
        
        # Проверяем размеры чанков
        large_chunks = [c for c in chunks if c.token_count > config.indexing.chunk_size]
        small_chunks = [c for c in chunks if c.token_count < config.indexing.min_chunk_size]
        
        if large_chunks:
            lines.append(f"- ⚠️ {len(large_chunks)} чанков превышают максимальный размер ({config.indexing.chunk_size} токенов)")
            lines.append("  Рекомендуется уменьшить `chunk_size` или использовать стратегию `semantic`")
        
        if small_chunks:
            lines.append(f"- ⚠️ {len(small_chunks)} чанков меньше минимального размера ({config.indexing.min_chunk_size} токенов)")
            lines.append("  Рекомендуется объединить мелкие чанки")
        
        if not large_chunks and not small_chunks:
            lines.append("- ✅ Размеры чанков оптимальны")
        
        return "\n".join(lines)
    
    except ValueError as e:
        return f"❌ Ошибка: {e}"
    except Exception as e:
        logger.error(f"Error in preview_chunks: {e}", exc_info=True)
        return f"❌ Ошибка превью: {e}"


async def enrich_document(
    vault_name: str,
    file_path: str,
    enrichment_type: str = "all",  # context | summary | all
) -> str:
    """Обогащение конкретного документа.
    
    Args:
        vault_name: Имя vault'а
        file_path: Путь к файлу (относительный от корня vault)
        enrichment_type: Тип обогащения:
            - "context": только context prefix для чанков
            - "summary": только document summary
            - "all": context + summary
    
    Returns:
        Результат обогащения с preview в Markdown
    """
    try:
        # Получаем путь к vault'у
        vault_path = _get_vault_path(vault_name)
        
        # Определяем полный путь к файлу
        file_path_obj = Path(file_path)
        if not file_path_obj.is_absolute():
            file_path_obj = vault_path / file_path_obj
        
        if not file_path_obj.exists():
            return f"❌ Файл не найден: {file_path_obj}"
        
        # Читаем и обрабатываем документ
        from obsidian_kb.file_parsers import extract_text_from_file
        from obsidian_kb.frontmatter_parser import FrontmatterParser
        
        content = extract_text_from_file(file_path_obj)
        if not content:
            return f"❌ Не удалось прочитать файл: {file_path_obj}"
        
        frontmatter_data, body = FrontmatterParser.parse(content, str(file_path_obj))
        metadata = frontmatter_data.to_dict()
        title = metadata.get("title", "") or frontmatter_data.title or file_path_obj.stem
        
        # Получаем ConfigManager и конфигурацию
        config_manager = get_config_manager()
        config = config_manager.get_config(vault_name)
        
        # Получаем chat_provider
        chat_provider = services.chat_provider
        if not chat_provider:
            return "❌ Chat provider не доступен. Обогащение требует LLM провайдера."
        
        # Создаём сервисы обогащения
        from obsidian_kb.enrichment.contextual_retrieval import ContextualRetrievalService
        from obsidian_kb.enrichment.summarization import SummarizationService
        
        contextual_service = ContextualRetrievalService(
            chat_provider=chat_provider,
            config=config.enrichment,
        )
        summarization_service = SummarizationService(
            chat_provider=chat_provider,
            config=config.enrichment,
        )
        
        # Разбиваем на чанки для context prefix
        chunking_service = ChunkingService(
            chat_provider=chat_provider,
            config=config.indexing,
        )
        chunks = await chunking_service.chunk_document(body, ChunkingStrategy.AUTO)
        
        lines = [f"## Обогащение документа: {file_path}\n"]
        lines.append(f"- **Тип обогащения:** {enrichment_type}\n")
        
        # Context prefix
        if enrichment_type in ("context", "all"):
            lines.append("### Context Prefix\n")
            
            if not chunks:
                lines.append("*Чанки не найдены*")
            else:
                enriched_chunks = await contextual_service.enrich_chunks(
                    chunks=chunks,
                    document_context=title,
                )
                
                lines.append(f"**Обработано чанков:** {len(enriched_chunks)}\n")
                
                for i, enriched_chunk in enumerate(enriched_chunks[:5], 1):  # Показываем первые 5
                    lines.append(f"#### Чанк {i}")
                    if enriched_chunk.context_prefix:
                        preview = enriched_chunk.context_prefix[:150].replace("\n", " ")
                        if len(enriched_chunk.context_prefix) > 150:
                            preview += "..."
                        lines.append(f"**Context prefix:** {preview}")
                    else:
                        lines.append("*Context prefix не сгенерирован*")
                    lines.append("")
                
                if len(enriched_chunks) > 5:
                    lines.append(f"*... и ещё {len(enriched_chunks) - 5} чанков*\n")
        
        # Summary
        if enrichment_type in ("summary", "all"):
            lines.append("### Document Summary\n")
            
            summary = await summarization_service.summarize_document(
                content=content,
                metadata=metadata,
            )
            
            if summary and summary.summary_text:
                lines.append(f"**Summary:**\n{summary.summary_text}")
                if summary.key_points:
                    lines.append("\n**Ключевые моменты:**")
                    for point in summary.key_points:
                        lines.append(f"- {point}")
            else:
                lines.append("*Summary не сгенерирован*")
        
        return "\n".join(lines)
    
    except ValueError as e:
        return f"❌ Ошибка: {e}"
    except Exception as e:
        logger.error(f"Error in enrich_document: {e}", exc_info=True)
        return f"❌ Ошибка обогащения: {e}"


async def cancel_job(job_id: str) -> str:
    """Отмена фоновой задачи индексации.

    Реализует graceful shutdown:
    - Для ожидающих задач (pending): немедленная отмена
    - Для выполняющихся задач (running): завершает текущий документ и останавливается
    - Частично проиндексированные данные сохраняются (не откатываются)

    Args:
        job_id: ID задачи из get_job_status()

    Returns:
        Markdown с результатом отмены:
        - "cancelled": задача успешно отменена
        - "not_found": задача не найдена
        - "already_completed": задача уже завершена

    Examples:
        # Получить список задач
        get_job_status()

        # Отменить конкретную задачу
        cancel_job(job_id="abc123-...")
    """
    try:
        from obsidian_kb.mcp_server import get_job_queue

        job_queue = get_job_queue()
        if not job_queue:
            return "❌ Ошибка: Очередь фоновых задач недоступна."

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
            lines.append("\n*Частично проиндексированные данные сохранены.*")
            return "\n".join(lines)

        return f"❌ Неизвестный результат отмены: {result}"

    except Exception as e:
        logger.error(f"Error in cancel_job: {e}", exc_info=True)
        return f"❌ Ошибка отмены задачи: {e}"

