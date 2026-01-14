"""Тесты для ChangeMonitorService."""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.config.manager import ConfigManager
from obsidian_kb.storage.change_detector import ChangeDetector, ChangeSet
from obsidian_kb.indexing.change_monitor import ChangeMonitorService
from obsidian_kb.indexing.job_queue import BackgroundJobQueue, JobPriority, JobStatus


@pytest.fixture
def temp_vault_for_monitor(tmp_path):
    """Временный vault для тестов мониторинга."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    (vault_path / "file1.md").write_text("# File 1\n\nContent", encoding="utf-8")
    return vault_path


@pytest.fixture
def temp_vaults_config(tmp_path):
    """Временный конфиг vault'ов."""
    config_path = tmp_path / "vaults.json"
    return config_path


@pytest.fixture
def mock_job_queue():
    """Мок BackgroundJobQueue."""
    queue = MagicMock(spec=BackgroundJobQueue)
    queue.enqueue = AsyncMock()
    return queue


@pytest.fixture
def mock_config_manager(tmp_path, temp_vaults_config):
    """Мок ConfigManager."""
    config_manager = MagicMock(spec=ConfigManager)
    return config_manager


@pytest.fixture
def change_monitor(mock_job_queue, mock_config_manager):
    """ChangeMonitorService для тестов."""
    return ChangeMonitorService(
        job_queue=mock_job_queue,
        config_manager=mock_config_manager,
        enabled=True,
        polling_interval=1,  # Короткий интервал для тестов
        debounce_seconds=0.1,  # Короткий debounce для тестов
    )


@pytest.mark.asyncio
async def test_start_stop_monitor(change_monitor, temp_vault_for_monitor, temp_vaults_config):
    """Тест запуска и остановки мониторинга."""
    # Мокаем конфигурацию vault'ов
    with patch.object(change_monitor, "_get_configured_vaults") as mock_get_vaults:
        mock_get_vaults.return_value = {"test_vault": temp_vault_for_monitor}
        
        # Запускаем мониторинг
        await change_monitor.start()
        
        assert change_monitor._running is True
        
        # Останавливаем мониторинг
        await change_monitor.stop()
        
        assert change_monitor._running is False


@pytest.mark.asyncio
async def test_start_monitor_disabled(change_monitor):
    """Тест, что мониторинг не запускается если отключен."""
    change_monitor._enabled = False
    
    await change_monitor.start()
    
    assert change_monitor._running is False


@pytest.mark.asyncio
async def test_get_configured_vaults(change_monitor, temp_vault_for_monitor, tmp_path):
    """Тест получения списка настроенных vault'ов."""
    # Создаём временный конфиг
    config_path = tmp_path / "vaults.json"
    config_data = {
        "vaults": [
            {
                "name": "test_vault",
                "path": str(temp_vault_for_monitor),
            }
        ]
    }
    config_path.write_text(json.dumps(config_data), encoding="utf-8")
    
    # Мокаем settings.vaults_config
    with patch("obsidian_kb.indexing.change_monitor.settings") as mock_settings:
        mock_settings.vaults_config = config_path
        
        vaults = await change_monitor._get_configured_vaults()
        
        assert "test_vault" in vaults
        assert vaults["test_vault"] == temp_vault_for_monitor


@pytest.mark.asyncio
async def test_get_configured_vaults_empty(change_monitor, tmp_path):
    """Тест получения пустого списка vault'ов."""
    config_path = tmp_path / "vaults.json"
    config_path.write_text(json.dumps({"vaults": []}), encoding="utf-8")
    
    with patch("obsidian_kb.indexing.change_monitor.settings") as mock_settings:
        mock_settings.vaults_config = config_path
        
        vaults = await change_monitor._get_configured_vaults()
        
        assert len(vaults) == 0


@pytest.mark.asyncio
async def test_start_vault_watcher(change_monitor, temp_vault_for_monitor):
    """Тест запуска watcher для vault'а."""
    await change_monitor._start_vault_watcher("test_vault", temp_vault_for_monitor)
    
    assert "test_vault" in change_monitor._vault_watchers
    assert "test_vault" in change_monitor._debounce_timers


@pytest.mark.asyncio
async def test_handle_file_change(change_monitor, temp_vault_for_monitor):
    """Тест обработки изменения файла."""
    change_monitor._debounce_timers["test_vault"] = {}
    
    file_path = temp_vault_for_monitor / "file1.md"
    
    await change_monitor._handle_file_change(
        vault_name="test_vault",
        vault_path=temp_vault_for_monitor,
        file_path=file_path,
    )
    
    # Проверяем, что задача была поставлена в очередь
    # change_monitor использует mock_job_queue из фикстуры
    change_monitor._job_queue.enqueue.assert_called_once()
    call_args = change_monitor._job_queue.enqueue.call_args
    
    assert call_args.kwargs["vault_name"] == "test_vault"
    assert call_args.kwargs["operation"] == "index_documents"
    assert call_args.kwargs["priority"] == JobPriority.NORMAL


@pytest.mark.asyncio
async def test_handle_file_change_debounce(change_monitor, temp_vault_for_monitor):
    """Тест debounce для обработки изменений."""
    change_monitor._debounce_timers["test_vault"] = {}
    change_monitor._debounce_seconds = 1.0  # Увеличиваем debounce для теста
    
    file_path = temp_vault_for_monitor / "file1.md"
    
    # Первое изменение
    await change_monitor._handle_file_change(
        vault_name="test_vault",
        vault_path=temp_vault_for_monitor,
        file_path=file_path,
    )
    
    # Второе изменение сразу (должно быть проигнорировано)
    await change_monitor._handle_file_change(
        vault_name="test_vault",
        vault_path=temp_vault_for_monitor,
        file_path=file_path,
    )
    
    # Должно быть только одно обращение к enqueue
    assert change_monitor._job_queue.enqueue.call_count == 1


@pytest.mark.asyncio
async def test_check_vault_changes(change_monitor, temp_vault_for_monitor):
    """Тест проверки изменений через ChangeDetector."""
    # Мокаем ChangeDetector - использует новый API с added/modified/deleted
    mock_change_set = ChangeSet(
        added=[temp_vault_for_monitor / "new_file.md"],
        modified=[temp_vault_for_monitor / "file1.md"],
        deleted=[],
    )

    with patch.object(change_monitor._change_detector, "detect_changes") as mock_detect:
        mock_detect.return_value = mock_change_set

        # Мокаем db_manager для удаления файлов
        from obsidian_kb.service_container import get_service_container
        with patch("obsidian_kb.service_container.get_service_container") as mock_get_services:
            mock_services = MagicMock()
            mock_services.db_manager = MagicMock()
            mock_services.db_manager.delete_file = AsyncMock()
            mock_get_services.return_value = mock_services

            await change_monitor._check_vault_changes("test_vault", temp_vault_for_monitor)

            # Проверяем, что задача была поставлена
            change_monitor._job_queue.enqueue.assert_called_once()
            call_args = change_monitor._job_queue.enqueue.call_args

            assert call_args.kwargs["vault_name"] == "test_vault"
            assert call_args.kwargs["operation"] == "index_documents"
            assert len(call_args.kwargs["params"]["paths"]) == 2  # new + modified


@pytest.mark.asyncio
async def test_check_vault_changes_with_deleted(change_monitor, temp_vault_for_monitor):
    """Тест обработки удалённых файлов."""
    mock_change_set = ChangeSet(
        added=[],
        modified=[],
        deleted=["deleted_file.md"],
    )

    with patch.object(change_monitor._change_detector, "detect_changes") as mock_detect:
        mock_detect.return_value = mock_change_set

        from obsidian_kb.service_container import get_service_container
        with patch("obsidian_kb.service_container.get_service_container") as mock_get_services:
            mock_services = MagicMock()
            mock_services.db_manager = MagicMock()
            mock_services.db_manager.delete_file = AsyncMock()
            mock_get_services.return_value = mock_services

            await change_monitor._check_vault_changes("test_vault", temp_vault_for_monitor)

            # Проверяем, что файл был удалён из индекса
            mock_services.db_manager.delete_file.assert_called_once_with(
                "test_vault",
                "deleted_file.md",
            )


@pytest.mark.asyncio
async def test_check_vault_changes_empty(change_monitor, temp_vault_for_monitor):
    """Тест проверки изменений без изменений."""
    mock_change_set = ChangeSet(
        added=[],
        modified=[],
        deleted=[],
    )
    
    with patch.object(change_monitor._change_detector, "detect_changes") as mock_detect:
        mock_detect.return_value = mock_change_set
        
        await change_monitor._check_vault_changes("test_vault", temp_vault_for_monitor)
        
        # Не должно быть обращений к enqueue
        change_monitor._job_queue.enqueue.assert_not_called()


@pytest.mark.asyncio
async def test_polling_loop(change_monitor, temp_vault_for_monitor):
    """Тест периодической проверки изменений."""
    change_monitor._running = True
    change_monitor._polling_interval = 0.1  # Очень короткий интервал для теста
    
    # Мокаем _get_configured_vaults и _check_vault_changes
    with patch.object(change_monitor, "_get_configured_vaults") as mock_get_vaults:
        with patch.object(change_monitor, "_check_vault_changes") as mock_check:
            mock_get_vaults.return_value = {"test_vault": temp_vault_for_monitor}
            mock_check.return_value = None
            
            # Запускаем polling loop
            task = asyncio.create_task(change_monitor._polling_loop())
            
            # Ждём немного
            await asyncio.sleep(0.3)
            
            # Останавливаем
            change_monitor._running = False
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Проверяем, что проверка была вызвана
            assert mock_check.call_count > 0


@pytest.mark.asyncio
async def test_start_with_no_vaults(change_monitor):
    """Тест запуска без настроенных vault'ов."""
    with patch.object(change_monitor, "_get_configured_vaults") as mock_get_vaults:
        mock_get_vaults.return_value = {}
        
        await change_monitor.start()
        
        # Мониторинг устанавливает _running = True, но не запускает watchers и polling
        # Проверяем, что watchers не запущены
        assert len(change_monitor._vault_watchers) == 0
        # Polling task может быть создан, но это нормально

