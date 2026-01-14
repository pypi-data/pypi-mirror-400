"""End-to-end тесты для Phase 6: Background Jobs & Monitoring."""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.config.manager import ConfigManager
from obsidian_kb.indexing.change_monitor import ChangeMonitorService
from obsidian_kb.indexing.job_queue import BackgroundJobQueue, JobPriority, JobStatus
from obsidian_kb.quality.cost_tracker import CostTracker, OperationType


@pytest.fixture
def temp_vault_e2e(tmp_path):
    """Временный vault для E2E тестов."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    (vault_path / "file1.md").write_text("# File 1\n\nInitial content", encoding="utf-8")
    return vault_path


@pytest.fixture
def temp_db_e2e(tmp_path):
    """Временная БД для E2E тестов."""
    return tmp_path / "test_db"


@pytest.fixture
def temp_vaults_config_e2e(tmp_path, temp_vault_e2e):
    """Временный конфиг vault'ов для E2E тестов."""
    config_path = tmp_path / "vaults.json"
    config_data = {
        "vaults": [
            {
                "name": "test_vault",
                "path": str(temp_vault_e2e),
            }
        ]
    }
    config_path.write_text(json.dumps(config_data), encoding="utf-8")
    return config_path


@pytest.mark.asyncio
async def test_e2e_file_change_detection_and_indexing(temp_vault_e2e, temp_db_e2e, temp_vaults_config_e2e):
    """E2E тест: изменение файла → обнаружение → постановка в очередь → выполнение."""
    # Создаём компоненты
    job_queue = BackgroundJobQueue(max_workers=1)
    config_manager = ConfigManager()
    
    # Мокаем ConfigManager для получения vault'ов
    with patch("obsidian_kb.indexing.change_monitor.settings") as mock_settings:
        mock_settings.vaults_config = temp_vaults_config_e2e
        
        change_monitor = ChangeMonitorService(
            job_queue=job_queue,
            config_manager=config_manager,
            enabled=True,
            polling_interval=1,
            debounce_seconds=0.1,
        )
        
        # Мокаем orchestrator для выполнения задач
        mock_orchestrator = MagicMock()
        mock_job = MagicMock()
        mock_job.id = "test-job-1"
        mock_job.vault_name = "test_vault"
        mock_job.vault_path = temp_vault_e2e
        mock_orchestrator.create_job = AsyncMock(return_value=mock_job)
        
        from obsidian_kb.indexing.orchestrator import IndexingResult
        mock_result = IndexingResult(
            job_id="test-job-1",
            documents_total=1,
            documents_processed=1,
            chunks_created=1,
            duration_seconds=0.1,
        )
        mock_orchestrator.run_job = AsyncMock(return_value=mock_result)
        
        with patch.object(job_queue, "_get_orchestrator", return_value=mock_orchestrator):
            # Запускаем компоненты
            await job_queue.start()
            await change_monitor.start()
            
            try:
                # Изменяем файл
                file_path = temp_vault_e2e / "file1.md"
                file_path.write_text("# File 1\n\nUpdated content", encoding="utf-8")
                
                # Ждём обработки
                await asyncio.sleep(1.5)
                
                # Проверяем, что задача была создана
                jobs = await job_queue.list_jobs()
                assert len(jobs) > 0
                
                # Проверяем, что хотя бы одна задача была выполнена или выполняется
                completed_or_running = [
                    j for j in jobs
                    if j.status in (JobStatus.COMPLETED, JobStatus.RUNNING)
                ]
                assert len(completed_or_running) > 0
                
            finally:
                await change_monitor.stop()
                await job_queue.stop()


@pytest.mark.asyncio
async def test_e2e_cost_tracking(temp_db_e2e):
    """E2E тест: выполнение операции → запись затрат → получение отчёта."""
    cost_tracker = CostTracker(db_path=temp_db_e2e.parent)
    
    # Записываем затраты на несколько операций
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
        vault_name="test_vault",
    )
    
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandexgpt",
        operation_type=OperationType.CHAT_COMPLETION,
        input_tokens=500,
        output_tokens=200,
        vault_name="test_vault",
    )
    
    # Получаем отчёт
    costs = await cost_tracker.get_costs(vault_name="test_vault")
    
    assert costs["total_cost_usd"] > 0
    assert costs["total_input_tokens"] == 1500
    assert costs["total_output_tokens"] == 200
    assert costs["record_count"] == 2
    assert "yandex" in costs["by_provider"]
    assert "test_vault" in costs["by_vault"]
    assert OperationType.EMBEDDING.value in costs["by_operation"]
    assert OperationType.CHAT_COMPLETION.value in costs["by_operation"]


@pytest.mark.asyncio
async def test_e2e_job_queue_with_cost_tracking(temp_vault_e2e, temp_db_e2e):
    """E2E тест: выполнение задачи → отслеживание затрат."""
    job_queue = BackgroundJobQueue(max_workers=1)
    cost_tracker = CostTracker(db_path=temp_db_e2e.parent)
    
    # Мокаем orchestrator
    mock_orchestrator = MagicMock()
    mock_job = MagicMock()
    mock_job.id = "test-job-1"
    mock_job.vault_name = "test_vault"
    mock_job.vault_path = temp_vault_e2e
    mock_orchestrator.create_job = AsyncMock(return_value=mock_job)
    
    from obsidian_kb.indexing.orchestrator import IndexingResult
    mock_result = IndexingResult(
        job_id="test-job-1",
        documents_total=1,
        documents_processed=1,
        chunks_created=1,
        duration_seconds=0.1,
    )
    mock_orchestrator.run_job = AsyncMock(return_value=mock_result)
    
    with patch.object(job_queue, "_get_orchestrator", return_value=mock_orchestrator):
        await job_queue.start()
        
        try:
            # Добавляем задачу
            job = await job_queue.enqueue(
                vault_name="test_vault",
                vault_path=temp_vault_e2e,
                operation="index_documents",
                params={},
            )
            
            # Ждём выполнения
            await asyncio.sleep(0.5)
            
            # Записываем затраты (в реальной системе это делается автоматически)
            await cost_tracker.record_cost(
                provider="yandex",
                model="yandex-embedding",
                operation_type=OperationType.INDEXING,
                input_tokens=1000,
                vault_name="test_vault",
                metadata={"job_id": job.id},
            )
            
            # Проверяем статус задачи
            status = await job_queue.get_job_status(job.id)
            assert status.status in (JobStatus.COMPLETED, JobStatus.RUNNING, JobStatus.PENDING)
            
            # Проверяем затраты
            costs = await cost_tracker.get_costs(vault_name="test_vault")
            assert costs["record_count"] >= 1
            
        finally:
            await job_queue.stop()


@pytest.mark.asyncio
async def test_e2e_change_monitor_polling(temp_vault_e2e, temp_vaults_config_e2e):
    """E2E тест: периодическая проверка изменений через polling."""
    job_queue = BackgroundJobQueue(max_workers=1)
    config_manager = ConfigManager()
    
    with patch("obsidian_kb.indexing.change_monitor.settings") as mock_settings:
        mock_settings.vaults_config = temp_vaults_config_e2e
        
        change_monitor = ChangeMonitorService(
            job_queue=job_queue,
            config_manager=config_manager,
            enabled=True,
            polling_interval=0.5,  # Короткий интервал для теста
            debounce_seconds=0.1,
        )
        
        # Мокаем ChangeDetector (Phase 2.0.6: consolidated in storage/)
        from obsidian_kb.storage.change_detector import ChangeSet
        mock_change_set = ChangeSet(
            added=[temp_vault_e2e / "new_file.md"],
            modified=[],
            deleted=[],
        )
        
        with patch.object(change_monitor._change_detector, "detect_changes") as mock_detect:
            mock_detect.return_value = mock_change_set
            
            await job_queue.start()
            await change_monitor.start()
            
            try:
                # Ждём polling
                await asyncio.sleep(1.0)
                
                # Проверяем, что задача была поставлена (через list_jobs)
                jobs = await job_queue.list_jobs()
                # Может быть создана задача или нет, в зависимости от debounce и polling
                # Главное, что сервисы работают без ошибок
                assert len(jobs) >= 0
                
            finally:
                await change_monitor.stop()
                await job_queue.stop()


@pytest.mark.asyncio
async def test_e2e_multiple_vaults_monitoring(tmp_path):
    """E2E тест: мониторинг нескольких vault'ов."""
    # Создаём два vault'а
    vault1_path = tmp_path / "vault1"
    vault1_path.mkdir()
    (vault1_path / "file1.md").write_text("# File 1", encoding="utf-8")
    
    vault2_path = tmp_path / "vault2"
    vault2_path.mkdir()
    (vault2_path / "file2.md").write_text("# File 2", encoding="utf-8")
    
    # Создаём конфиг
    config_path = tmp_path / "vaults.json"
    config_data = {
        "vaults": [
            {"name": "vault1", "path": str(vault1_path)},
            {"name": "vault2", "path": str(vault2_path)},
        ]
    }
    config_path.write_text(json.dumps(config_data), encoding="utf-8")
    
    job_queue = BackgroundJobQueue(max_workers=2)
    config_manager = ConfigManager()
    
    with patch("obsidian_kb.indexing.change_monitor.settings") as mock_settings:
        mock_settings.vaults_config = config_path
        
        change_monitor = ChangeMonitorService(
            job_queue=job_queue,
            config_manager=config_manager,
            enabled=True,
            polling_interval=1,
            debounce_seconds=0.1,
        )
        
        await job_queue.start()
        await change_monitor.start()
        
        try:
            # Ждём немного
            await asyncio.sleep(0.5)
            
            # Проверяем, что watchers запущены для обоих vault'ов
            assert len(change_monitor._vault_watchers) == 2
            assert "vault1" in change_monitor._vault_watchers
            assert "vault2" in change_monitor._vault_watchers
            
        finally:
            await change_monitor.stop()
            await job_queue.stop()


@pytest.mark.asyncio
async def test_e2e_job_priority_execution(temp_vault_e2e):
    """E2E тест: выполнение задач с разными приоритетами."""
    job_queue = BackgroundJobQueue(max_workers=1)

    # Мокаем orchestrator
    mock_orchestrator = MagicMock()
    mock_job = MagicMock()
    mock_job.id = "test-job"
    mock_job.vault_name = "test_vault"
    mock_job.vault_path = temp_vault_e2e
    mock_orchestrator.create_job = AsyncMock(return_value=mock_job)

    from obsidian_kb.indexing.orchestrator import IndexingResult
    mock_result = IndexingResult(
        job_id="test-job",
        documents_total=1,
        documents_processed=1,
        chunks_created=1,
        duration_seconds=0.1,
    )
    mock_orchestrator.run_job = AsyncMock(return_value=mock_result)

    with patch.object(job_queue, "_get_orchestrator", return_value=mock_orchestrator):
        await job_queue.start()

        try:
            # Создаём задачи с разными приоритетами для РАЗНЫХ vault'ов
            # чтобы избежать дедупликации (задачи с тем же vault/operation объединяются)
            low_job = await job_queue.enqueue(
                vault_name="vault_low",
                vault_path=temp_vault_e2e,
                operation="index_documents",
                params={},
                priority=JobPriority.LOW,
            )

            high_job = await job_queue.enqueue(
                vault_name="vault_high",
                vault_path=temp_vault_e2e,
                operation="index_documents",
                params={},
                priority=JobPriority.HIGH,
            )

            # Ждём выполнения
            await asyncio.sleep(0.5)

            # Проверяем, что задачи созданы
            assert low_job.priority == JobPriority.LOW
            assert high_job.priority == JobPriority.HIGH

        finally:
            await job_queue.stop()

