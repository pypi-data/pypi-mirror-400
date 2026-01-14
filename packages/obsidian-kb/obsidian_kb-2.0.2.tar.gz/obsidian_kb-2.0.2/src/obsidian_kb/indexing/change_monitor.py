"""Служба автоматического мониторинга изменений в vault'ах."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from obsidian_kb.config import settings
from obsidian_kb.config.manager import ConfigManager
from obsidian_kb.storage.change_detector import ChangeDetector, ChangeSet
from obsidian_kb.indexing.job_queue import BackgroundJobQueue, JobPriority
from obsidian_kb.vault_indexer import VaultIndexer

logger = logging.getLogger(__name__)


class ChangeMonitorService:
    """Служба автоматического мониторинга изменений в vault'ах.
    
    Отслеживает изменения файлов в реальном времени через watchdog и периодически
    проверяет изменения через ChangeDetector. При обнаружении изменений автоматически
    ставит задачи в BackgroundJobQueue.
    """
    
    def __init__(
        self,
        job_queue: BackgroundJobQueue,
        config_manager: ConfigManager,
        enabled: bool = True,
        polling_interval: int = 300,
        debounce_seconds: float = 10.0,
    ) -> None:
        """Инициализация службы мониторинга.
        
        Args:
            job_queue: Очередь фоновых задач
            config_manager: Менеджер конфигурации для получения списка vault'ов
            enabled: Включен ли автоматический мониторинг (по умолчанию True)
            polling_interval: Интервал периодической проверки в секундах (по умолчанию 60)
            debounce_seconds: Время debounce для избежания множественных индексаций (по умолчанию 2.0)
        """
        self._job_queue = job_queue
        self._config_manager = config_manager
        self._enabled = enabled
        self._polling_interval = polling_interval
        self._debounce_seconds = debounce_seconds
        
        # Словарь vault'ов с их watchers
        self._vault_watchers: dict[str, tuple[VaultIndexer, Observer]] = {}
        
        # Debounce словарь: {vault_name: {file_path: last_change_time}}
        self._debounce_timers: dict[str, dict[str, float]] = {}
        
        # Флаг работы
        self._running = False
        self._polling_task: asyncio.Task | None = None
        
        # ChangeDetector для периодической проверки
        from obsidian_kb.service_container import get_service_container
        services = get_service_container()
        self._change_detector = ChangeDetector(
            document_repository=services.document_repository,
        )
    
    async def start(self) -> None:
        """Запуск мониторинга изменений."""
        if self._running:
            logger.warning("ChangeMonitorService already started")
            return
        
        if not self._enabled:
            logger.info("ChangeMonitorService disabled, skipping start")
            return
        
        self._running = True
        
        # Получаем список настроенных vault'ов
        vaults = await self._get_configured_vaults()
        
        if not vaults:
            logger.info("No configured vaults found, ChangeMonitorService will not start")
            return
        
        # Запускаем watchers для каждого vault'а
        for vault_name, vault_path in vaults.items():
            try:
                await self._start_vault_watcher(vault_name, vault_path)
            except Exception as e:
                logger.error(f"Failed to start watcher for vault '{vault_name}': {e}")
        
        # Запускаем периодическую проверку изменений
        self._polling_task = asyncio.create_task(self._polling_loop())
        
        logger.info(
            f"ChangeMonitorService started: monitoring {len(vaults)} vault(s), "
            f"polling interval={self._polling_interval}s, debounce={self._debounce_seconds}s"
        )
    
    async def stop(self) -> None:
        """Остановка мониторинга изменений."""
        if not self._running:
            return
        
        self._running = False
        
        # Останавливаем polling task
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None
        
        # Останавливаем все watchers
        for vault_name, (indexer, observer) in list(self._vault_watchers.items()):
            try:
                indexer.stop_watcher()
                logger.info(f"Stopped watcher for vault '{vault_name}'")
            except Exception as e:
                logger.error(f"Error stopping watcher for vault '{vault_name}': {e}")
        
        self._vault_watchers.clear()
        self._debounce_timers.clear()
        
        logger.info("ChangeMonitorService stopped")
    
    async def _get_configured_vaults(self) -> dict[str, Path]:
        """Получение списка настроенных vault'ов из конфигурации.
        
        Returns:
            Словарь {vault_name: vault_path}
        """
        vaults = {}
        
        try:
            config_path = settings.vaults_config
            if not config_path.exists():
                return vaults
            
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            vaults_list = config.get("vaults", [])
            for vault_config in vaults_list:
                vault_name = vault_config.get("name")
                vault_path_str = vault_config.get("path")
                
                if vault_name and vault_path_str:
                    vault_path = Path(vault_path_str)
                    if vault_path.exists() and vault_path.is_dir():
                        vaults[vault_name] = vault_path
                    else:
                        logger.warning(
                            f"Vault path does not exist or is not a directory: {vault_path_str}"
                        )
        except Exception as e:
            logger.error(f"Error loading configured vaults: {e}")
        
        return vaults
    
    async def _start_vault_watcher(self, vault_name: str, vault_path: Path) -> None:
        """Запуск watcher для vault'а.
        
        Args:
            vault_name: Имя vault'а
            vault_path: Путь к vault'у
        """
        if vault_name in self._vault_watchers:
            logger.warning(f"Watcher for vault '{vault_name}' already started")
            return
        
        # Создаём VaultIndexer для watcher'а
        indexer = VaultIndexer(vault_path, vault_name)
        
        # Создаём callback для обработки изменений
        def on_change(file_path: Path) -> None:
            """Callback для обработки изменений файла."""
            asyncio.create_task(self._handle_file_change(vault_name, vault_path, file_path))
        
        # Запускаем watcher
        indexer.start_watcher(on_change)
        
        self._vault_watchers[vault_name] = (indexer, indexer.observer)
        self._debounce_timers[vault_name] = {}
        
        logger.info(f"Started watcher for vault '{vault_name}' at {vault_path}")
    
    async def _handle_file_change(
        self,
        vault_name: str,
        vault_path: Path,
        file_path: Path,
    ) -> None:
        """Обработка изменения файла.
        
        Args:
            vault_name: Имя vault'а
            vault_path: Путь к vault'у
            file_path: Путь к изменённому файлу
        """
        # Проверяем debounce
        relative_path = str(file_path.relative_to(vault_path)) if file_path.is_relative_to(vault_path) else str(file_path)
        current_time = asyncio.get_event_loop().time()
        
        if vault_name in self._debounce_timers:
            last_change = self._debounce_timers[vault_name].get(relative_path, 0)
            if current_time - last_change < self._debounce_seconds:
                # Слишком рано, игнорируем
                return
            
            self._debounce_timers[vault_name][relative_path] = current_time
        
        logger.info(
            f"File change detected in vault '{vault_name}': {relative_path}"
        )
        
        # Ставим задачу в очередь
        try:
            await self._job_queue.enqueue(
                vault_name=vault_name,
                vault_path=vault_path,
                operation="index_documents",
                params={
                    "paths": [relative_path],
                    "force": False,
                    "enrichment": "contextual",
                },
                priority=JobPriority.NORMAL,
            )
            logger.info(f"Enqueued indexing job for '{relative_path}' in vault '{vault_name}'")
        except Exception as e:
            logger.error(f"Failed to enqueue indexing job for '{relative_path}': {e}")
    
    async def _polling_loop(self) -> None:
        """Периодическая проверка изменений через ChangeDetector."""
        while self._running:
            try:
                await asyncio.sleep(self._polling_interval)
                
                if not self._running:
                    break
                
                # Получаем список vault'ов
                vaults = await self._get_configured_vaults()
                
                # Проверяем изменения для каждого vault'а
                for vault_name, vault_path in vaults.items():
                    try:
                        await self._check_vault_changes(vault_name, vault_path)
                    except Exception as e:
                        logger.error(f"Error checking changes for vault '{vault_name}': {e}")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
    
    async def _check_vault_changes(self, vault_name: str, vault_path: Path) -> None:
        """Проверка изменений в vault'е через ChangeDetector.
        
        Args:
            vault_name: Имя vault'а
            vault_path: Путь к vault'у
        """
        try:
            # Используем ChangeDetector для обнаружения изменений
            change_set = await self._change_detector.detect_changes(
                vault_path=vault_path,
                vault_name=vault_name,
            )
            
            if change_set.is_empty():
                return
            
            # Обрабатываем новые и изменённые файлы
            files_to_index = change_set.new_files + change_set.modified_files
            
            if files_to_index:
                # Преобразуем в относительные пути
                relative_paths = [
                    str(f.relative_to(vault_path)) if f.is_relative_to(vault_path) else str(f)
                    for f in files_to_index
                ]
                
                # Ставим задачу в очередь
                await self._job_queue.enqueue(
                    vault_name=vault_name,
                    vault_path=vault_path,
                    operation="index_documents",
                    params={
                        "paths": relative_paths,
                        "force": False,
                        "enrichment": "contextual",
                    },
                    priority=JobPriority.NORMAL,
                )
                
                logger.info(
                    f"Polling detected changes in vault '{vault_name}': "
                    f"{len(change_set.new_files)} new, {len(change_set.modified_files)} modified, "
                    f"{len(change_set.deleted_files)} deleted"
                )
            
            # Обрабатываем удалённые файлы
            if change_set.deleted_files:
                # Удаляем из индекса
                from obsidian_kb.service_container import get_service_container
                services = get_service_container()
                
                for file_path in change_set.deleted_files:
                    try:
                        await services.db_manager.delete_file(vault_name, file_path)
                        logger.info(f"Deleted file '{file_path}' from index for vault '{vault_name}'")
                    except Exception as e:
                        logger.error(f"Failed to delete file '{file_path}' from index: {e}")
        
        except Exception as e:
            logger.error(f"Error checking changes for vault '{vault_name}': {e}")

