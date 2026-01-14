"""Watch command for automatic incremental index updates."""

import asyncio
import signal
import sys
import threading
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from time import time as get_time
from typing import Any

import click

from obsidian_kb.cli.utils import console, get_services, logger
from obsidian_kb.config import settings
from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.validation import validate_vault_config, validate_vault_path
from obsidian_kb.vault_indexer import VaultIndexer


@click.command()
@click.option("--vault", help="Имя конкретного vault'а для отслеживания (по умолчанию отслеживаются все vault'ы из конфига)")
@click.option("--debounce", default=2.0, help="Задержка в секундах перед индексированием изменённого файла (default: 2.0)")
def watch(vault: str | None, debounce: float) -> None:
    """Автоматическое инкрементальное обновление индекса при изменении файлов."""
    config_path = settings.vaults_config

    try:
        vaults = validate_vault_config(config_path)
    except Exception as e:
        console.print(f"[red]Ошибка валидации конфига: {e}[/red]")
        console.print(f"Проверьте файл: {config_path}")
        sys.exit(1)

    if not vaults:
        console.print("[yellow]Нет валидных vault'ов для отслеживания[/yellow]")
        return

    if vault:
        vaults = [v for v in vaults if v.get("name") == vault]
        if not vaults:
            console.print(f"[red]Vault '{vault}' не найден в конфиге[/red]")
            sys.exit(1)
        console.print("[cyan]Запуск автоматического отслеживания изменений[/cyan]")
        console.print(f"  Vault: {vault}")
    else:
        console.print("[cyan]Запуск автоматического отслеживания изменений[/cyan]")
        console.print("  [green]Отслеживаются все vault'ы из конфига[/green]")
        console.print(f"  Vault'ов: {len(vaults)}")
        vault_names = [v.get("name", "?") for v in vaults]
        console.print(f"  Vault'ы: {', '.join(vault_names)}")

    console.print(f"  Задержка (debounce): {debounce} сек")
    console.print("\n[yellow]Нажмите Ctrl+C для остановки[/yellow]\n")

    pending_changes: dict[str, dict[str, float]] = defaultdict(dict)
    changes_lock = threading.Lock()
    stop_flag = threading.Event()
    indexers: list[VaultIndexer] = []

    services = get_services()
    embedding_service = services.embedding_service
    db_manager = services.db_manager

    async def index_file(vault_name: str, file_path: Path, relative_path_str: str | None = None) -> None:
        """Index a single file."""
        try:
            indexer = next((idx for idx in indexers if idx.vault_name == vault_name), None)
            if not indexer:
                logger.error(f"Indexer not found for vault {vault_name}")
                return

            if not file_path.exists():
                try:
                    if relative_path_str:
                        await db_manager.delete_file(vault_name, relative_path_str)
                        console.print(f"  [yellow]Удалён из индекса: {relative_path_str}[/yellow]")
                    else:
                        try:
                            relative_path = file_path.relative_to(indexer.vault_path)
                            await db_manager.delete_file(vault_name, str(relative_path))
                            console.print(f"  [yellow]Удалён из индекса: {relative_path}[/yellow]")
                        except ValueError:
                            await db_manager.delete_file(vault_name, file_path.name)
                            console.print(f"  [yellow]Удалён из индекса: {file_path.name}[/yellow]")
                except Exception as e:
                    logger.error(f"Error deleting file from index: {e}")
                return

            from obsidian_kb.file_parsers import is_supported_file
            if not is_supported_file(file_path):
                return

            chunks = await indexer.scan_file(file_path)

            if not chunks:
                logger.warning(f"No chunks extracted from {file_path}")
                return

            texts = [chunk.content for chunk in chunks]
            embeddings = await embedding_service.get_embeddings_batch(texts)

            await db_manager.upsert_chunks(vault_name, chunks, embeddings)

            relative_path = file_path.relative_to(indexer.vault_path)
            console.print(f"  [green]✓ Обновлён: {relative_path} ({len(chunks)} чанков)[/green]")

        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
            console.print(f"  [red]Ошибка индексирования {file_path}: {e}[/red]")

    def on_file_change(vault_name: str, file_path: Path) -> None:
        """Callback on file change."""
        if stop_flag.is_set():
            return

        try:
            relative_path = file_path.relative_to(
                next((idx.vault_path for idx in indexers if idx.vault_name == vault_name), file_path.parent)
            )
            relative_path_str = str(relative_path)
        except ValueError:
            relative_path_str = file_path.name

        current_time = get_time()

        with changes_lock:
            pending_changes[vault_name][relative_path_str] = current_time

        logger.debug(f"File changed: {vault_name}::{relative_path_str}")

    async def process_pending_changes() -> None:
        """Process changes with debouncing."""
        while not stop_flag.is_set():
            try:
                await asyncio.sleep(0.5)

                current_time = get_time()
                files_to_index: list[tuple[str, Path, str]] = []

                with changes_lock:
                    for vault_name, vault_changes in list(pending_changes.items()):
                        for file_path_str, change_time in list(vault_changes.items()):
                            if current_time - change_time >= debounce:
                                indexer = next((idx for idx in indexers if idx.vault_name == vault_name), None)
                                if indexer:
                                    try:
                                        full_path = indexer.vault_path / file_path_str
                                        files_to_index.append((vault_name, full_path, file_path_str))
                                    except Exception as e:
                                        logger.debug(f"Error constructing path for {file_path_str}: {e}")

                                del vault_changes[file_path_str]

                        if not vault_changes:
                            del pending_changes[vault_name]

                for vault_name, file_path, relative_path_str in files_to_index:
                    await index_file(vault_name, file_path, relative_path_str)

            except Exception as e:
                logger.error(f"Error in process_pending_changes: {e}")

    async def watch_async() -> None:
        """Async watch function."""
        try:
            for vault_config in vaults:
                vault_name = vault_config.get("name")
                vault_path = vault_config.get("path")

                if not vault_name or not vault_path:
                    continue

                try:
                    path_obj = Path(vault_path)
                    validate_vault_path(path_obj, vault_name)

                    embedding_cache = EmbeddingCache()
                    indexer = VaultIndexer(path_obj, vault_name, embedding_cache=embedding_cache)
                    indexers.append(indexer)

                    def make_callback(vn: str) -> Callable[[Path], None]:
                        def callback(path: Path) -> None:
                            on_file_change(vn, path)
                        return callback

                    indexer.start_watcher(make_callback(vault_name))
                    console.print(f"[green]✓ Отслеживание: {vault_name}[/green]")

                except Exception as e:
                    console.print(f"[red]Ошибка инициализации {vault_name}: {e}[/red]")
                    logger.exception(f"Error initializing watcher for {vault_name}")

            if not indexers:
                console.print("[red]Не удалось инициализировать ни одного watcher'а[/red]")
                return

            console.print(f"\n[green]Отслеживание запущено для {len(indexers)} vault'ов[/green]")
            console.print("[cyan]Ожидание изменений файлов...[/cyan]\n")

            await process_pending_changes()

        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            logger.exception("Error in watch")
        finally:
            for indexer in indexers:
                try:
                    indexer.stop_watcher()
                except Exception as e:
                    logger.debug(f"Error stopping watcher for {indexer.vault_name}: {e}")
            await embedding_service.close()

    def signal_handler(signum: int, frame: Any) -> None:
        """Signal handler for graceful shutdown."""
        console.print("\n[yellow]Остановка отслеживания...[/yellow]")
        stop_flag.set()
        for indexer in indexers:
            try:
                indexer.stop_watcher()
            except Exception as e:
                logger.debug(f"Error stopping watcher during signal handling: {e}")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(watch_async())
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        console.print(f"[red]Критическая ошибка: {e}[/red]")
        logger.exception("Critical error in watch")
        sys.exit(1)
