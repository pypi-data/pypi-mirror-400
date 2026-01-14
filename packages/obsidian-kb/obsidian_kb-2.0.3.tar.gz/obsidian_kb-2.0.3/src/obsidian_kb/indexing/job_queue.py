"""Очередь фоновых задач для индексации."""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class CancellationToken:
    """Токен отмены для graceful shutdown задачи.

    Позволяет запросить отмену выполняющейся задачи и проверять
    её статус в точках проверки (между итерациями обработки).
    """

    def __init__(self) -> None:
        self._cancelled = False
        self._callbacks: list[Callable[[], None]] = []

    def cancel(self) -> None:
        """Запросить отмену."""
        self._cancelled = True
        for callback in self._callbacks:
            try:
                callback()
            except Exception:
                pass

    def is_cancelled(self) -> bool:
        """Проверить, запрошена ли отмена."""
        return self._cancelled

    def on_cancel(self, callback: Callable[[], None]) -> None:
        """Зарегистрировать callback при отмене."""
        self._callbacks.append(callback)
        if self._cancelled:
            callback()

    def raise_if_cancelled(self) -> None:
        """Поднять исключение если отмена запрошена."""
        if self._cancelled:
            raise CancellationError("Job was cancelled")


class CancellationError(Exception):
    """Исключение при отмене задачи."""
    pass

from obsidian_kb.enrichment.contextual_retrieval import EnrichmentStats
from obsidian_kb.indexing.orchestrator import (
    EnrichmentStrategy,
    IndexingOrchestrator,
    IndexingResult,
)

logger = logging.getLogger(__name__)


class JobPriority(Enum):
    """Приоритет задачи."""
    
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class JobStatus(Enum):
    """Статус задачи."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackgroundJob:
    """Фоновая задача индексации."""

    id: str
    vault_name: str
    vault_path: Path
    operation: str  # "index_documents", "reindex_vault", etc.
    params: dict[str, Any]  # Параметры операции
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0  # 0.0 - 1.0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    result: IndexingResult | None = None
    retry_count: int = 0
    max_retries: int = 3
    cancellation_token: CancellationToken = field(default_factory=CancellationToken)
    # Phase 2: Enrichment статистика
    enrichment_stats: EnrichmentStats | None = None

    @property
    def cancellable(self) -> bool:
        """Можно ли отменить задачу."""
        return self.status in (JobStatus.PENDING, JobStatus.RUNNING)

    def to_dict(self) -> dict[str, Any]:
        """Сериализация для MCP и API.

        Включает всю информацию о задаче, включая enrichment статистику.

        Returns:
            Словарь с данными задачи
        """
        result_dict: dict[str, Any] = {
            "id": self.id,
            "vault_name": self.vault_name,
            "operation": self.operation,
            "status": self.status.value,
            "progress": round(self.progress, 3),
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "retry_count": self.retry_count,
            "cancellable": self.cancellable,
        }

        # Добавляем результат если есть
        if self.result:
            result_dict["result"] = {
                "documents_processed": self.result.documents_processed,
                "documents_total": self.result.documents_total,
                "chunks_created": self.result.chunks_created,
                "duration_seconds": round(self.result.duration_seconds, 2),
                "errors_count": len(self.result.errors),
                "warnings_count": len(self.result.warnings),
            }
            if self.result.errors:
                result_dict["result"]["errors"] = self.result.errors[:10]  # Первые 10
            if self.result.warnings:
                result_dict["result"]["warnings"] = self.result.warnings[:10]

        # Добавляем enrichment статистику
        enrichment = self.enrichment_stats or (
            self.result.enrichment_stats if self.result else None
        )
        if enrichment:
            result_dict["enrichment"] = enrichment.to_dict()

        return result_dict


class BackgroundJobQueue:
    """Очередь фоновых задач для индексации.
    
    Управляет задачами индексации, которые выполняются в фоне без блокировки MCP сервера.
    Поддерживает приоритеты, retry логику и отслеживание прогресса.
    """
    
    def __init__(
        self,
        max_workers: int = 2,
    ) -> None:
        """Инициализация очереди задач.
        
        Args:
            max_workers: Максимальное количество параллельных воркеров
        """
        self._jobs: dict[str, BackgroundJob] = {}
        self._queue: asyncio.Queue[BackgroundJob] = asyncio.Queue()
        self._max_workers = max_workers
        self._workers: list[asyncio.Task] = []
        self._running = False
        self._lock = asyncio.Lock()
        # Vault-level locks для предотвращения параллельной индексации одного vault'а
        self._vault_locks: dict[str, asyncio.Lock] = {}
        self._vault_locks_lock = asyncio.Lock()
    
    def _find_mergeable_job(
        self,
        vault_name: str,
        operation: str,
        params: dict[str, Any],
    ) -> BackgroundJob | None:
        """Найти pending задачу для объединения.

        Ищет PENDING задачу с тем же vault_name и operation.
        Если новая задача с force=True, не объединяем (force требует полной обработки).
        Если существующая задача с force=True, возвращаем её (она уже обработает всё).

        Args:
            vault_name: Имя vault'а
            operation: Тип операции
            params: Параметры новой задачи

        Returns:
            Существующая задача для объединения или None
        """
        for job in self._jobs.values():
            if (
                job.status == JobStatus.PENDING
                and job.vault_name == vault_name
                and job.operation == operation
            ):
                # Если существующая задача force=True - она обработает всё
                if job.params.get("force", False):
                    return job
                # Если новая задача force=True - не объединяем
                if params.get("force", False):
                    return None
                return job
        return None

    def _merge_job_paths(
        self,
        existing: BackgroundJob,
        new_params: dict[str, Any],
    ) -> None:
        """Объединить paths из новой задачи в существующую.

        Args:
            existing: Существующая задача
            new_params: Параметры новой задачи
        """
        existing_paths = set(existing.params.get("paths", []) or [])
        new_paths = set(new_params.get("paths", []) or [])
        merged = list(existing_paths | new_paths)
        existing.params["paths"] = merged

    async def enqueue(
        self,
        vault_name: str,
        vault_path: Path,
        operation: str,
        params: dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
    ) -> BackgroundJob:
        """Добавление задачи в очередь.

        Поддерживает дедупликацию: если уже есть pending задача для того же
        vault и operation, пути объединяются вместо создания новой задачи.

        Args:
            vault_name: Имя vault'а
            vault_path: Путь к vault'у
            operation: Тип операции ("index_documents", "reindex_vault", etc.)
            params: Параметры операции
            priority: Приоритет задачи

        Returns:
            Созданная или существующая задача
        """
        async with self._lock:
            # Проверяем возможность объединения с существующей задачей
            existing = self._find_mergeable_job(vault_name, operation, params)
            if existing:
                self._merge_job_paths(existing, params)
                logger.info(
                    f"Merged paths into existing job {existing.id} for vault '{vault_name}'"
                )
                return existing

            # Создаём новую задачу
            job = BackgroundJob(
                id=str(uuid.uuid4()),
                vault_name=vault_name,
                vault_path=vault_path,
                operation=operation,
                params=params,
                priority=priority,
            )
            self._jobs[job.id] = job

        await self._queue.put(job)
        logger.info(
            f"Enqueued job {job.id} for vault '{vault_name}': "
            f"{operation} (priority: {priority.value})"
        )

        return job
    
    async def get_job_status(self, job_id: str) -> BackgroundJob | None:
        """Получение статуса задачи.
        
        Args:
            job_id: ID задачи
            
        Returns:
            Задача или None если не найдена
        """
        async with self._lock:
            return self._jobs.get(job_id)
    
    async def list_jobs(
        self,
        status: JobStatus | None = None,
        vault_name: str | None = None,
    ) -> list[BackgroundJob]:
        """Получение списка задач с фильтрацией.
        
        Args:
            status: Фильтр по статусу
            vault_name: Фильтр по vault'у
            
        Returns:
            Список задач
        """
        async with self._lock:
            jobs = list(self._jobs.values())
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        if vault_name:
            jobs = [j for j in jobs if j.vault_name == vault_name]
        
        # Сортируем по времени создания (новые первыми)
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        
        return jobs
    
    async def cancel_job(self, job_id: str) -> str:
        """Отмена задачи.

        Реализует graceful shutdown:
        - Для PENDING задач: немедленная отмена
        - Для RUNNING задач: сигнал через cancellation_token,
          задача завершит текущий документ и остановится

        Args:
            job_id: ID задачи

        Returns:
            Статус отмены:
            - "cancelled": задача успешно отменена
            - "not_found": задача не найдена
            - "already_completed": задача уже завершена
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return "not_found"

            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                return "already_completed"

            if job.status == JobStatus.CANCELLED:
                return "cancelled"  # Уже отменена

            # Активируем токен отмены (для running задач)
            job.cancellation_token.cancel()

            # Устанавливаем статус
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()

            logger.info(
                f"Cancelled job {job_id} (was {job.status.value}), "
                f"progress: {job.progress:.1%}"
            )
            return "cancelled"
    
    async def start(self) -> None:
        """Запуск воркеров для обработки задач."""
        if self._running:
            logger.warning("Job queue already started")
            return
        
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self._max_workers)
        ]
        logger.info(f"Started {self._max_workers} job workers")
    
    async def stop(self) -> None:
        """Остановка воркеров."""
        if not self._running:
            return
        
        self._running = False
        
        # Ждём завершения всех воркеров
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers = []
        
        logger.info("Stopped job workers")

    async def _get_vault_lock(self, vault_name: str) -> asyncio.Lock:
        """Получение lock для vault'а.

        Гарантирует, что только одна задача индексации может выполняться
        для данного vault'а в любой момент времени.

        Args:
            vault_name: Имя vault'а

        Returns:
            Lock для данного vault'а
        """
        async with self._vault_locks_lock:
            if vault_name not in self._vault_locks:
                self._vault_locks[vault_name] = asyncio.Lock()
            return self._vault_locks[vault_name]

    async def _worker(self, worker_name: str) -> None:
        """Воркер для обработки задач.
        
        Args:
            worker_name: Имя воркера для логирования
        """
        logger.info(f"Worker {worker_name} started")
        
        while self._running:
            try:
                # Получаем задачу из очереди с таймаутом
                try:
                    job = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Проверяем, не отменена ли задача
                if job.status == JobStatus.CANCELLED:
                    logger.debug(f"Job {job.id} was cancelled, skipping")
                    continue
                
                # Выполняем задачу
                await self._execute_job(job, worker_name)
                
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}", exc_info=True)
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _execute_job(self, job: BackgroundJob, worker_name: str) -> None:
        """Выполнение задачи.

        Использует vault-level lock для предотвращения параллельной индексации
        одного vault'а, что может привести к race condition и потере данных.

        Args:
            job: Задача для выполнения
            worker_name: Имя воркера для логирования
        """
        # Получаем lock для vault'а перед началом выполнения
        vault_lock = await self._get_vault_lock(job.vault_name)

        # Проверяем, не заблокирован ли vault другой задачей
        if vault_lock.locked():
            logger.info(
                f"Job {job.id} waiting for vault '{job.vault_name}' lock "
                f"(another job is running)"
            )

        async with vault_lock:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()

            logger.info(
                f"Worker {worker_name} executing job {job.id} "
                f"for vault '{job.vault_name}': {job.operation}"
            )

            try:
                # Получаем orchestrator для vault'а
                orchestrator = await self._get_orchestrator(job.vault_name, job.vault_path)

                # Выполняем операцию
                if job.operation == "index_documents":
                    result = await self._execute_index_documents(job, orchestrator)
                elif job.operation == "reindex_vault":
                    result = await self._execute_reindex_vault(job, orchestrator)
                elif job.operation == "index_vault":
                    result = await self._execute_index_vault(job)
                else:
                    raise ValueError(f"Unknown operation: {job.operation}")

                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now()
                job.result = result
                job.progress = 1.0

                logger.info(
                    f"Job {job.id} completed: {result.documents_processed}/{result.documents_total} "
                    f"documents, {result.chunks_created} chunks"
                )

            except Exception as e:
                logger.error(f"Job {job.id} failed: {e}", exc_info=True)

                job.retry_count += 1
                if job.retry_count < job.max_retries:
                    # Повторная попытка
                    job.status = JobStatus.PENDING
                    job.error = str(e)
                    await self._queue.put(job)
                    logger.info(f"Job {job.id} will retry ({job.retry_count}/{job.max_retries})")
                else:
                    # Превышен лимит попыток
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.now()
                    job.error = str(e)
                    logger.error(f"Job {job.id} failed after {job.max_retries} retries")
    
    async def _get_orchestrator(
        self,
        vault_name: str,
        vault_path: Path,
    ) -> IndexingOrchestrator:
        """Получение orchestrator для vault'а.

        Args:
            vault_name: Имя vault'а
            vault_path: Путь к vault'у

        Returns:
            IndexingOrchestrator
        """
        from obsidian_kb.service_container import get_service_container

        services = get_service_container()

        # Получаем провайдеры и репозитории
        embedding_provider = services.embedding_provider
        # Используем enrichment_chat_provider для обогащения контекстом
        chat_provider = services.enrichment_chat_provider
        chunk_repository = services.chunk_repository
        document_repository = services.document_repository

        # Получаем ConfigManager
        from obsidian_kb.config.manager import get_config_manager
        config_manager = get_config_manager()

        # Создаём orchestrator
        orchestrator = IndexingOrchestrator(
            embedding_provider=embedding_provider,
            chat_provider=chat_provider,
            chunk_repository=chunk_repository,
            document_repository=document_repository,
            config_manager=config_manager,
        )

        return orchestrator
    
    async def _execute_index_documents(
        self,
        job: BackgroundJob,
        orchestrator: IndexingOrchestrator,
    ) -> IndexingResult:
        """Выполнение операции index_documents.

        Args:
            job: Задача
            orchestrator: IndexingOrchestrator

        Returns:
            IndexingResult
        """
        params = job.params

        # Преобразуем paths если указаны
        paths = None
        if params.get("paths"):
            paths = [Path(p) for p in params["paths"]]

        # Преобразуем enrichment strategy
        enrichment_str = params.get("enrichment", "contextual")
        enrichment_map = {
            "none": EnrichmentStrategy.NONE,
            "contextual": EnrichmentStrategy.CONTEXTUAL,
            "full": EnrichmentStrategy.FULL,
        }
        enrichment = enrichment_map.get(enrichment_str, EnrichmentStrategy.CONTEXTUAL)

        # Создаём задачу в orchestrator
        indexing_job = await orchestrator.create_job(
            vault_name=job.vault_name,
            vault_path=job.vault_path,
            paths=paths,
            force=params.get("force", False),
            enrichment=enrichment,
        )

        # Выполняем задачу с мониторингом прогресса
        result = await self._run_with_progress_tracking(job, orchestrator, indexing_job.id)

        return result
    
    async def _execute_reindex_vault(
        self,
        job: BackgroundJob,
        orchestrator: IndexingOrchestrator,
    ) -> IndexingResult:
        """Выполнение операции reindex_vault.

        Args:
            job: Задача
            orchestrator: IndexingOrchestrator

        Returns:
            IndexingResult
        """
        params = job.params

        # Очищаем старый индекс перед переиндексацией
        if params.get("clear_before_reindex", True):
            await self._clear_vault_index(job.vault_name)

        # Преобразуем enrichment strategy
        enrichment_str = params.get("enrichment", "contextual")
        enrichment_map = {
            "none": EnrichmentStrategy.NONE,
            "contextual": EnrichmentStrategy.CONTEXTUAL,
            "full": EnrichmentStrategy.FULL,
        }
        enrichment = enrichment_map.get(enrichment_str, EnrichmentStrategy.CONTEXTUAL)

        # Создаём задачу с force=True для полной переиндексации
        indexing_job = await orchestrator.create_job(
            vault_name=job.vault_name,
            vault_path=job.vault_path,
            paths=None,
            force=True,
            enrichment=enrichment,
        )

        # Выполняем задачу с мониторингом прогресса
        result = await self._run_with_progress_tracking(job, orchestrator, indexing_job.id)

        return result

    async def _run_with_progress_tracking(
        self,
        job: BackgroundJob,
        orchestrator: IndexingOrchestrator,
        indexing_job_id: str,
    ) -> IndexingResult:
        """Выполнение задачи с трекингом прогресса.

        Запускает orchestrator.run_job() и периодически обновляет прогресс
        в BackgroundJob для отображения в UI.

        Args:
            job: Задача BackgroundJob (для обновления прогресса)
            orchestrator: IndexingOrchestrator
            indexing_job_id: ID задачи в orchestrator

        Returns:
            IndexingResult
        """
        async def update_progress():
            """Периодическое обновление прогресса."""
            while True:
                await asyncio.sleep(0.5)  # Обновляем каждые 500ms
                orch_job = orchestrator.get_job(indexing_job_id)
                if orch_job:
                    job.progress = orch_job.progress
                    if orch_job.status in ("completed", "failed", "cancelled"):
                        break
                # Проверяем отмену
                if job.cancellation_token.is_cancelled():
                    break

        # Запускаем мониторинг прогресса
        progress_task = asyncio.create_task(update_progress())
        try:
            result = await orchestrator.run_job(
                indexing_job_id,
                cancellation_token=job.cancellation_token,
            )
        except CancellationError:
            # Задача отменена - создаём частичный результат
            orch_job = orchestrator.get_job(indexing_job_id)
            result = IndexingResult(
                job_id=indexing_job_id,
                documents_processed=orch_job.documents_processed if orch_job else 0,
                documents_total=orch_job.documents_total if orch_job else 0,
                chunks_created=0,
                errors=["Job was cancelled"],
                duration_seconds=0.0,
            )
        finally:
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass

        return result

    async def _clear_vault_index(self, vault_name: str) -> None:
        """Очистка индекса vault'а перед полной переиндексацией.

        Удаляет все таблицы vault'а: documents, chunks, document_properties, metadata.

        Args:
            vault_name: Имя vault'а
        """
        from obsidian_kb.service_container import get_service_container

        services = get_service_container()

        try:
            # Используем IndexingService.delete_vault для удаления всех таблиц
            await services.db_manager._indexing_service.delete_vault(vault_name)
            logger.info(f"Cleared all tables for vault '{vault_name}' before reindex")

        except Exception as e:
            logger.warning(f"Failed to clear vault index for '{vault_name}': {e}")
    
    async def _execute_index_vault(self, job: BackgroundJob) -> IndexingResult:
        """Выполнение операции index_vault через orchestrator.

        Использует IndexingOrchestrator для индексации с поддержкой enrichment.

        Args:
            job: Задача

        Returns:
            IndexingResult
        """
        params = job.params

        # Получаем orchestrator
        orchestrator = await self._get_orchestrator(job.vault_name, job.vault_path)

        # Определяем enrichment strategy
        enrichment_str = params.get("enrichment", "none")
        enrichment_map = {
            "none": EnrichmentStrategy.NONE,
            "contextual": EnrichmentStrategy.CONTEXTUAL,
            "full": EnrichmentStrategy.FULL,
        }
        enrichment = enrichment_map.get(enrichment_str, EnrichmentStrategy.NONE)

        # Проверяем инкрементальное индексирование
        only_changed = params.get("only_changed", False)
        force = not only_changed  # force=True если не only_changed

        # Создаём задачу в orchestrator
        indexing_job = await orchestrator.create_job(
            vault_name=job.vault_name,
            vault_path=job.vault_path,
            paths=None,  # Все файлы
            force=force,
            enrichment=enrichment,
        )

        # Выполняем задачу с мониторингом прогресса
        result = await self._run_with_progress_tracking(job, orchestrator, indexing_job.id)

        return result

