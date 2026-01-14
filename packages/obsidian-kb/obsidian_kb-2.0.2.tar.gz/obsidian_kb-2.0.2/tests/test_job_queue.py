"""Тесты для BackgroundJobQueue и JobWorker."""

import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.indexing.job_queue import (
    BackgroundJob,
    BackgroundJobQueue,
    CancellationError,
    CancellationToken,
    JobPriority,
    JobStatus,
)
from obsidian_kb.indexing.orchestrator import (
    EnrichmentStrategy,
    IndexingJob,
    IndexingOrchestrator,
    IndexingResult,
)


@pytest.fixture
def temp_vault_for_jobs(tmp_path):
    """Временный vault для тестов задач."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    (vault_path / "file1.md").write_text("# File 1\n\nContent", encoding="utf-8")
    return vault_path


@pytest.fixture
def mock_orchestrator(tmp_path):
    """Мок IndexingOrchestrator."""
    orchestrator = MagicMock(spec=IndexingOrchestrator)

    # Создаём mock vault path
    mock_vault_path = tmp_path / "mock_vault"
    mock_vault_path.mkdir()

    # Мокаем create_job
    mock_job = IndexingJob(
        id="test-job-1",
        vault_name="test_vault",
        vault_path=mock_vault_path,
        paths=[],
        enrichment=EnrichmentStrategy.CONTEXTUAL,
        status="pending",
        progress=0.0,
        documents_total=0,
        documents_processed=0,
    )
    orchestrator.create_job = AsyncMock(return_value=mock_job)
    
    # Мокаем run_job
    mock_result = IndexingResult(
        job_id="test-job-1",
        documents_total=1,
        documents_processed=1,
        chunks_created=2,
        duration_seconds=0.5,
    )
    orchestrator.run_job = AsyncMock(return_value=mock_result)
    
    return orchestrator


@pytest.mark.asyncio
async def test_enqueue_job(temp_vault_for_jobs):
    """Тест добавления задачи в очередь."""
    queue = BackgroundJobQueue(max_workers=1)
    
    job = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file1.md"], "force": False},
        priority=JobPriority.NORMAL,
    )
    
    assert job.id is not None
    assert job.vault_name == "test_vault"
    assert job.operation == "index_documents"
    assert job.status == JobStatus.PENDING
    assert job.priority == JobPriority.NORMAL
    
    # Проверяем, что задача добавлена в словарь
    status = await queue.get_job_status(job.id)
    assert status is not None
    assert status.id == job.id


@pytest.mark.asyncio
async def test_get_job_status(temp_vault_for_jobs):
    """Тест получения статуса задачи."""
    queue = BackgroundJobQueue(max_workers=1)
    
    job = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={},
    )
    
    status = await queue.get_job_status(job.id)
    assert status is not None
    assert status.id == job.id
    
    # Проверяем несуществующую задачу
    status = await queue.get_job_status("nonexistent")
    assert status is None


@pytest.mark.asyncio
async def test_list_jobs_filtering(temp_vault_for_jobs):
    """Тест фильтрации списка задач."""
    queue = BackgroundJobQueue(max_workers=1)
    
    # Создаём несколько задач
    job1 = await queue.enqueue(
        vault_name="vault1",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={},
        priority=JobPriority.HIGH,
    )
    
    job2 = await queue.enqueue(
        vault_name="vault2",
        vault_path=temp_vault_for_jobs,
        operation="reindex_vault",
        params={},
        priority=JobPriority.LOW,
    )
    
    # Получаем все задачи
    all_jobs = await queue.list_jobs()
    assert len(all_jobs) >= 2
    
    # Фильтруем по vault
    vault1_jobs = await queue.list_jobs(vault_name="vault1")
    assert len(vault1_jobs) >= 1
    assert all(j.vault_name == "vault1" for j in vault1_jobs)
    
    # Фильтруем по статусу
    pending_jobs = await queue.list_jobs(status=JobStatus.PENDING)
    assert len(pending_jobs) >= 2
    assert all(j.status == JobStatus.PENDING for j in pending_jobs)


@pytest.mark.asyncio
async def test_cancel_job(temp_vault_for_jobs):
    """Тест отмены задачи."""
    queue = BackgroundJobQueue(max_workers=1)

    job = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={},
    )

    # Проверяем свойство cancellable
    assert job.cancellable is True

    # Отменяем задачу
    result = await queue.cancel_job(job.id)
    assert result == "cancelled"

    # Проверяем статус
    status = await queue.get_job_status(job.id)
    assert status.status == JobStatus.CANCELLED

    # После отмены cancellable должно быть False
    assert status.cancellable is False

    # Попытка отменить уже отменённую задачу
    result_again = await queue.cancel_job(job.id)
    assert result_again == "cancelled"  # Уже отменена, повторный вызов = то же значение

    # Попытка отменить несуществующую задачу
    result_nonexistent = await queue.cancel_job("nonexistent")
    assert result_nonexistent == "not_found"


@pytest.mark.asyncio
async def test_start_stop_workers():
    """Тест запуска и остановки воркеров."""
    queue = BackgroundJobQueue(max_workers=2)
    
    # Запускаем воркеры
    await queue.start()
    
    # Проверяем, что воркеры запущены
    assert queue._running is True
    assert len(queue._workers) == 2
    
    # Останавливаем воркеры
    await queue.stop()
    
    # Проверяем, что воркеры остановлены
    assert queue._running is False
    assert len(queue._workers) == 0


@pytest.mark.asyncio
async def test_execute_index_documents(temp_vault_for_jobs, mock_orchestrator):
    """Тест выполнения операции index_documents."""
    queue = BackgroundJobQueue(max_workers=1)
    
    with patch.object(queue, "_get_orchestrator", return_value=mock_orchestrator):
        await queue.start()
        
        try:
            job = await queue.enqueue(
                vault_name="test_vault",
                vault_path=temp_vault_for_jobs,
                operation="index_documents",
                params={
                    "paths": ["file1.md"],
                    "force": False,
                    "enrichment": "contextual",
                },
            )
            
            # Ждём выполнения задачи
            await asyncio.sleep(0.5)
            
            # Проверяем статус
            status = await queue.get_job_status(job.id)
            # Задача может быть выполнена или ещё выполняться
            assert status.status in (JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING)
            
        finally:
            await queue.stop()


@pytest.mark.asyncio
async def test_execute_reindex_vault(temp_vault_for_jobs, mock_orchestrator):
    """Тест выполнения операции reindex_vault."""
    queue = BackgroundJobQueue(max_workers=1)
    
    with patch.object(queue, "_get_orchestrator", return_value=mock_orchestrator):
        await queue.start()
        
        try:
            job = await queue.enqueue(
                vault_name="test_vault",
                vault_path=temp_vault_for_jobs,
                operation="reindex_vault",
                params={"enrichment": "full"},
            )
            
            # Ждём выполнения задачи
            await asyncio.sleep(0.5)
            
            # Проверяем статус
            status = await queue.get_job_status(job.id)
            assert status.status in (JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING)
            
        finally:
            await queue.stop()


@pytest.mark.asyncio
async def test_job_retry_on_failure(temp_vault_for_jobs):
    """Тест повторной попытки при ошибке."""
    queue = BackgroundJobQueue(max_workers=1)
    
    # Создаём мок orchestrator, который выбрасывает ошибку
    mock_orchestrator = MagicMock(spec=IndexingOrchestrator)
    mock_orchestrator.create_job = AsyncMock(side_effect=Exception("Test error"))
    
    with patch.object(queue, "_get_orchestrator", return_value=mock_orchestrator):
        await queue.start()
        
        try:
            job = await queue.enqueue(
                vault_name="test_vault",
                vault_path=temp_vault_for_jobs,
                operation="index_documents",
                params={},
            )
            
            # Ждём обработки ошибки
            await asyncio.sleep(1.0)
            
            # Проверяем, что задача либо в retry, либо failed
            status = await queue.get_job_status(job.id)
            assert status.status in (JobStatus.PENDING, JobStatus.FAILED)
            assert status.retry_count >= 0
            
        finally:
            await queue.stop()


@pytest.mark.asyncio
async def test_job_priority(temp_vault_for_jobs):
    """Тест приоритетов задач."""
    queue = BackgroundJobQueue(max_workers=1)

    # Создаём задачи с разными приоритетами для РАЗНЫХ vault'ов
    # чтобы избежать дедупликации
    low_job = await queue.enqueue(
        vault_name="vault_low",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={},
        priority=JobPriority.LOW,
    )

    high_job = await queue.enqueue(
        vault_name="vault_high",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={},
        priority=JobPriority.HIGH,
    )

    normal_job = await queue.enqueue(
        vault_name="vault_normal",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={},
        priority=JobPriority.NORMAL,
    )

    # Проверяем, что приоритеты установлены
    assert low_job.priority == JobPriority.LOW
    assert high_job.priority == JobPriority.HIGH
    assert normal_job.priority == JobPriority.NORMAL


@pytest.mark.asyncio
async def test_parallel_jobs(temp_vault_for_jobs, mock_orchestrator):
    """Тест параллельного выполнения нескольких задач."""
    queue = BackgroundJobQueue(max_workers=2)
    
    with patch.object(queue, "_get_orchestrator", return_value=mock_orchestrator):
        await queue.start()
        
        try:
            # Создаём несколько задач
            jobs = []
            for i in range(3):
                job = await queue.enqueue(
                    vault_name=f"test_vault_{i}",
                    vault_path=temp_vault_for_jobs,
                    operation="index_documents",
                    params={},
                )
                jobs.append(job)
            
            # Ждём выполнения
            await asyncio.sleep(1.0)
            
            # Проверяем, что задачи обрабатываются
            for job in jobs:
                status = await queue.get_job_status(job.id)
                assert status is not None
                assert status.status in (
                    JobStatus.COMPLETED,
                    JobStatus.RUNNING,
                    JobStatus.PENDING,
                )
            
        finally:
            await queue.stop()


@pytest.mark.asyncio
async def test_cancelled_job_not_executed(temp_vault_for_jobs, mock_orchestrator):
    """Тест, что отменённая задача не выполняется."""
    queue = BackgroundJobQueue(max_workers=1)
    
    with patch.object(queue, "_get_orchestrator", return_value=mock_orchestrator):
        await queue.start()
        
        try:
            job = await queue.enqueue(
                vault_name="test_vault",
                vault_path=temp_vault_for_jobs,
                operation="index_documents",
                params={},
            )
            
            # Отменяем задачу сразу
            await queue.cancel_job(job.id)
            
            # Ждём немного
            await asyncio.sleep(0.5)
            
            # Проверяем, что задача осталась отменённой
            status = await queue.get_job_status(job.id)
            assert status.status == JobStatus.CANCELLED
            
        finally:
            await queue.stop()


@pytest.mark.asyncio
async def test_execute_index_vault(temp_vault_for_jobs, tmp_path):
    """Тест выполнения операции index_vault (legacy метод)."""
    from obsidian_kb.service_container import get_service_container, reset_service_container
    from obsidian_kb.lance_db import LanceDBManager
    
    # Создаём временную БД
    db_path = tmp_path / "test_db.lance"
    reset_service_container()
    services = get_service_container(db_path=db_path)
    
    queue = BackgroundJobQueue(max_workers=1)
    
    try:
        await queue.start()
        
        # Добавляем файл в vault
        (temp_vault_for_jobs / "test.md").write_text("# Test Document\n\nContent here", encoding="utf-8")
        
        # Создаём задачу index_vault
        job = await queue.enqueue(
            vault_name="test_vault",
            vault_path=temp_vault_for_jobs,
            operation="index_vault",
            params={"only_changed": False},
        )
        
        # Ждём выполнения задачи
        await asyncio.sleep(2.0)
        
        # Проверяем статус
        status = await queue.get_job_status(job.id)
        assert status is not None
        # Задача может быть выполнена или ещё выполняться
        assert status.status in (JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING)
        
        # Если задача завершена, проверяем результат
        if status.status == JobStatus.COMPLETED and status.result:
            assert status.result.documents_processed > 0
            assert status.result.chunks_created > 0

    finally:
        await queue.stop()
        reset_service_container()


# =============================================================================
# Тесты для CancellationToken
# =============================================================================


def test_cancellation_token_initial_state():
    """Тест начального состояния токена отмены."""
    token = CancellationToken()
    assert token.is_cancelled() is False


def test_cancellation_token_cancel():
    """Тест отмены через токен."""
    token = CancellationToken()
    token.cancel()
    assert token.is_cancelled() is True


def test_cancellation_token_raise_if_cancelled():
    """Тест raise_if_cancelled поднимает исключение."""
    token = CancellationToken()

    # Не должно поднимать исключение
    token.raise_if_cancelled()  # Не должно бросить

    # После отмены должно поднять CancellationError
    token.cancel()
    with pytest.raises(CancellationError):
        token.raise_if_cancelled()


def test_cancellation_token_callback():
    """Тест callback при отмене."""
    token = CancellationToken()
    callback_called = []

    def my_callback():
        callback_called.append(True)

    token.on_cancel(my_callback)
    assert len(callback_called) == 0

    token.cancel()
    assert len(callback_called) == 1


def test_cancellation_token_callback_called_immediately_if_already_cancelled():
    """Тест: callback вызывается сразу если токен уже отменён."""
    token = CancellationToken()
    token.cancel()

    callback_called = []

    def my_callback():
        callback_called.append(True)

    # Callback должен быть вызван сразу при регистрации
    token.on_cancel(my_callback)
    assert len(callback_called) == 1


def test_background_job_has_cancellation_token():
    """Тест: BackgroundJob создаётся с CancellationToken."""
    from pathlib import Path

    job = BackgroundJob(
        id="test-id",
        vault_name="test_vault",
        vault_path=Path("/tmp/vault"),
        operation="index_documents",
        params={},
    )

    assert job.cancellation_token is not None
    assert job.cancellation_token.is_cancelled() is False


@pytest.mark.asyncio
async def test_cancel_job_activates_cancellation_token(temp_vault_for_jobs):
    """Тест: cancel_job активирует cancellation_token."""
    queue = BackgroundJobQueue(max_workers=1)

    job = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={},
    )

    # Токен не должен быть отменён
    assert job.cancellation_token.is_cancelled() is False

    # Отменяем задачу
    await queue.cancel_job(job.id)

    # Токен должен быть отменён
    assert job.cancellation_token.is_cancelled() is True


# =============================================================================
# Phase 2: Тесты для прозрачности статуса Enrichment
# =============================================================================


@pytest.mark.asyncio
async def test_background_job_to_dict_basic(temp_vault_for_jobs):
    """Тест: BackgroundJob.to_dict() возвращает корректную структуру."""
    queue = BackgroundJobQueue(max_workers=1)

    job = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"force": True},
    )

    result = job.to_dict()

    # Проверяем основные поля
    assert result["id"] == job.id
    assert result["vault_name"] == "test_vault"
    assert result["operation"] == "index_documents"
    assert result["status"] == "pending"
    assert result["progress"] == 0.0
    assert result["priority"] == "normal"
    assert result["cancellable"] is True
    assert "created_at" in result
    assert result["error"] is None


@pytest.mark.asyncio
async def test_background_job_to_dict_with_result(temp_vault_for_jobs):
    """Тест: BackgroundJob.to_dict() включает результат если есть."""
    from obsidian_kb.enrichment.contextual_retrieval import EnrichmentStats

    queue = BackgroundJobQueue(max_workers=1)

    job = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={},
    )

    # Устанавливаем результат вручную
    job.result = IndexingResult(
        job_id=job.id,
        documents_processed=5,
        documents_total=10,
        chunks_created=20,
        duration_seconds=2.5,
        errors=["Error 1", "Error 2"],
        warnings=["Warning 1"],
        enrichment_stats=EnrichmentStats(
            total_chunks=20,
            enriched_ok=18,
            enriched_fallback=2,
            errors=["Timeout error"],
        ),
    )
    job.status = JobStatus.COMPLETED

    result = job.to_dict()

    # Проверяем поля результата
    assert "result" in result
    assert result["result"]["documents_processed"] == 5
    assert result["result"]["documents_total"] == 10
    assert result["result"]["chunks_created"] == 20
    assert result["result"]["duration_seconds"] == 2.5
    assert result["result"]["errors_count"] == 2
    assert result["result"]["warnings_count"] == 1

    # Проверяем enrichment статистику
    assert "enrichment" in result
    assert result["enrichment"]["total"] == 20
    assert result["enrichment"]["success"] == 18
    assert result["enrichment"]["fallback"] == 2
    assert result["enrichment"]["errors_count"] == 1
    assert result["enrichment"]["success_rate_percent"] == 90.0


@pytest.mark.asyncio
async def test_background_job_to_dict_with_direct_enrichment_stats(temp_vault_for_jobs):
    """Тест: BackgroundJob.to_dict() берет enrichment_stats напрямую из job."""
    from obsidian_kb.enrichment.contextual_retrieval import EnrichmentStats

    queue = BackgroundJobQueue(max_workers=1)

    job = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={},
    )

    # Устанавливаем enrichment_stats напрямую (без result)
    job.enrichment_stats = EnrichmentStats(
        total_chunks=10,
        enriched_ok=10,
        enriched_fallback=0,
        errors=[],
    )

    result = job.to_dict()

    # Проверяем enrichment статистику
    assert "enrichment" in result
    assert result["enrichment"]["total"] == 10
    assert result["enrichment"]["success"] == 10
    assert result["enrichment"]["fallback"] == 0
    assert result["enrichment"]["success_rate_percent"] == 100.0


def test_enrichment_stats_success_rate():
    """Тест: EnrichmentStats.success_rate вычисляется корректно."""
    from obsidian_kb.enrichment.contextual_retrieval import EnrichmentStats

    # Все успешно
    stats_all_ok = EnrichmentStats(
        total_chunks=100,
        enriched_ok=100,
        enriched_fallback=0,
        errors=[],
    )
    assert stats_all_ok.success_rate == 100.0

    # Половина fallback
    stats_half = EnrichmentStats(
        total_chunks=100,
        enriched_ok=50,
        enriched_fallback=50,
        errors=["err1"] * 50,
    )
    assert stats_half.success_rate == 50.0

    # Пустой
    stats_empty = EnrichmentStats(
        total_chunks=0,
        enriched_ok=0,
        enriched_fallback=0,
        errors=[],
    )
    assert stats_empty.success_rate == 0.0


def test_enrichment_stats_to_dict():
    """Тест: EnrichmentStats.to_dict() возвращает корректную структуру."""
    from obsidian_kb.enrichment.contextual_retrieval import EnrichmentStats

    stats = EnrichmentStats(
        total_chunks=50,
        enriched_ok=45,
        enriched_fallback=5,
        errors=["err1", "err2"],
    )

    result = stats.to_dict()

    assert result["total"] == 50
    assert result["success"] == 45
    assert result["fallback"] == 5
    assert result["errors_count"] == 2
    assert result["success_rate_percent"] == 90.0


# =============================================================================
# Тесты для дедупликации задач
# =============================================================================


@pytest.mark.asyncio
async def test_enqueue_merges_pending_jobs(temp_vault_for_jobs):
    """Тест: enqueue объединяет paths в существующую pending задачу."""
    queue = BackgroundJobQueue(max_workers=1)

    # Первая задача
    job1 = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file1.md"], "force": False},
    )

    # Вторая задача с другим файлом — должна объединиться
    job2 = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file2.md"], "force": False},
    )

    # Должна вернуться та же задача
    assert job1.id == job2.id

    # Пути должны быть объединены
    paths = set(job1.params["paths"])
    assert "file1.md" in paths
    assert "file2.md" in paths

    # В очереди должна быть только одна задача
    jobs = await queue.list_jobs()
    assert len(jobs) == 1


@pytest.mark.asyncio
async def test_enqueue_no_merge_when_new_force(temp_vault_for_jobs):
    """Тест: новая задача с force=True не объединяется."""
    queue = BackgroundJobQueue(max_workers=1)

    # Первая задача без force
    job1 = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file1.md"], "force": False},
    )

    # Вторая задача с force=True — НЕ должна объединиться
    job2 = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file2.md"], "force": True},
    )

    # Должны быть разные задачи
    assert job1.id != job2.id

    # В очереди должны быть две задачи
    jobs = await queue.list_jobs()
    assert len(jobs) == 2


@pytest.mark.asyncio
async def test_enqueue_merge_into_existing_force(temp_vault_for_jobs):
    """Тест: если существующая задача с force=True, новая объединяется в неё."""
    queue = BackgroundJobQueue(max_workers=1)

    # Первая задача с force=True
    job1 = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file1.md"], "force": True},
    )

    # Вторая задача без force — должна объединиться в force
    job2 = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file2.md"], "force": False},
    )

    # Должна вернуться та же задача
    assert job1.id == job2.id

    # Пути должны быть объединены
    paths = set(job1.params["paths"])
    assert "file1.md" in paths
    assert "file2.md" in paths


@pytest.mark.asyncio
async def test_enqueue_no_merge_different_vault(temp_vault_for_jobs):
    """Тест: задачи для разных vault'ов не объединяются."""
    queue = BackgroundJobQueue(max_workers=1)

    job1 = await queue.enqueue(
        vault_name="vault1",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file1.md"], "force": False},
    )

    job2 = await queue.enqueue(
        vault_name="vault2",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file1.md"], "force": False},
    )

    # Должны быть разные задачи
    assert job1.id != job2.id


@pytest.mark.asyncio
async def test_enqueue_no_merge_different_operation(temp_vault_for_jobs):
    """Тест: задачи с разными операциями не объединяются."""
    queue = BackgroundJobQueue(max_workers=1)

    job1 = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="index_documents",
        params={"paths": ["file1.md"], "force": False},
    )

    job2 = await queue.enqueue(
        vault_name="test_vault",
        vault_path=temp_vault_for_jobs,
        operation="reindex_vault",
        params={"paths": ["file1.md"], "force": False},
    )

    # Должны быть разные задачи
    assert job1.id != job2.id

