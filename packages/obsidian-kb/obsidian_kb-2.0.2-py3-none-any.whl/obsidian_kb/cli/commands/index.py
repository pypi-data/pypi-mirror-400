"""Indexing commands: index, index_all, reindex."""

import asyncio
import sys
import time
from pathlib import Path

import click
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from obsidian_kb.batch_processor import BatchProcessor
from obsidian_kb.cli.utils import console, get_services, logger
from obsidian_kb.config import settings
from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.indexing_utils import index_with_cache
from obsidian_kb.validation import validate_vault_config, validate_vault_path
from obsidian_kb.vault_indexer import VaultIndexer


@click.command("index-all")
@click.option("--max-workers", type=int, help="Максимальное количество параллельных файлов (по умолчанию из настроек)")
@click.option("--enable-enrichment/--no-enrichment", default=True, help="Включить/выключить LLM-обогащение при индексации")
@click.option("--enrichment-strategy", type=click.Choice(["full", "fast"]), help="Стратегия обогащения: 'full' (summary+concepts+tags) или 'fast' (только summary)")
@click.option("--enable-clustering/--no-clustering", default=True, help="Включить/выключить кластеризацию документов при индексации")
def index_all(max_workers: int | None, enable_enrichment: bool, enrichment_strategy: str | None, enable_clustering: bool) -> None:
    """Индексировать все vault'ы из конфига."""
    config_path = settings.vaults_config

    try:
        vaults = validate_vault_config(config_path)
    except Exception as e:
        console.print(f"[red]Ошибка валидации конфига: {e}[/red]")
        console.print(f"Проверьте файл: {config_path}")
        sys.exit(1)

    if not vaults:
        console.print("[yellow]Нет валидных vault'ов для индексирования[/yellow]")
        return

    console.print(f"[green]Найдено {len(vaults)} валидных vault'ов для индексирования[/green]")

    async def index_all_async() -> None:
        services = get_services()
        for vault in vaults:
            vault_name = vault.get("name")
            vault_path = vault.get("path")

            if not vault_name or not vault_path:
                console.print(f"[yellow]Пропущен vault с неполными данными: {vault}[/yellow]")
                continue

            console.print(f"\n[cyan]Индексирование: {vault_name}[/cyan]")
            console.print(f"  Путь: {vault_path}")

            try:
                path_obj = Path(vault_path)
                validate_vault_path(path_obj, vault_name)

                recovery_service = services.recovery_service
                embedding_service = services.embedding_service
                db_manager = services.db_manager
                embedding_cache = EmbeddingCache()
                indexer = VaultIndexer(path_obj, vault_name, embedding_cache=embedding_cache)

                if enrichment_strategy:
                    settings.llm_enrichment_strategy = enrichment_strategy
                    console.print(f"  [cyan]Стратегия обогащения: {enrichment_strategy}[/cyan]")

                try:
                    indexed_files = await db_manager.get_indexed_files(vault_name)
                    only_changed = len(indexed_files) > 0
                    if only_changed:
                        console.print(f"  [cyan]Инкрементальное индексирование: найдено {len(indexed_files)} проиндексированных файлов[/cyan]")
                except Exception:
                    indexed_files = None
                    only_changed = False

                try:
                    chunks, embeddings, cache_stats = await recovery_service.retry_with_backoff(
                        index_with_cache,
                        vault_name=vault_name,
                        indexer=indexer,
                        embedding_service=embedding_service,
                        db_manager=db_manager,
                        embedding_cache=embedding_cache,
                        only_changed=only_changed,
                        indexed_files=indexed_files,
                        max_workers=max_workers,
                        enable_enrichment=enable_enrichment,
                        only_new_chunks=False,
                        enable_clustering=enable_clustering,
                        max_retries=3,
                        initial_delay=2.0,
                        operation_name=f"index_{vault_name}",
                    )
                except Exception:
                    console.print("  [yellow]Попытка восстановления подключений...[/yellow]")
                    try:
                        await recovery_service.recover_database_connection(db_manager)
                        await recovery_service.recover_ollama_connection(embedding_service)
                    except Exception:
                        pass
                    raise

                if not chunks:
                    if only_changed:
                        console.print("  [green]✓ Все файлы актуальны, индексирование не требуется[/green]")
                    else:
                        console.print("  [yellow]Нет чанков для индексирования[/yellow]")
                    continue

                await db_manager.upsert_chunks(vault_name, chunks, embeddings)

                file_count = len(set(c.file_path for c in chunks))
                cache_info = ""
                if cache_stats.get("cached", 0) > 0:
                    cache_info = f" (из кэша: {cache_stats['cached']}, вычислено: {cache_stats['computed']})"

                enrichment_info = ""
                if enable_enrichment and "enrichment" in cache_stats:
                    enrichment_stats = cache_stats["enrichment"]
                    if enrichment_stats.get("enriched", 0) > 0:
                        enrichment_info = f" | Обогащено: {enrichment_stats['enriched']}"
                    if enrichment_stats.get("errors", 0) > 0:
                        enrichment_info += f" | Ошибок обогащения: {enrichment_stats['errors']}"

                console.print(f"  [green]✓ Индексировано: {len(chunks)} чанков из {file_count} файлов{cache_info}{enrichment_info}[/green]")

            except Exception as e:
                console.print(f"  [red]Ошибка: {e}[/red]")
                logger.exception(f"Error indexing vault {vault_name}")

        console.print("\n[green]Индексирование завершено[/green]")

        embedding_service = services.embedding_service
        await embedding_service.close()

    asyncio.run(index_all_async())


@click.command()
@click.option("--vault", required=True, help="Имя vault'а")
@click.option("--path", required=True, type=click.Path(exists=True, file_okay=False), help="Путь к vault'у")
@click.option("--max-workers", type=int, help="Максимальное количество параллельных файлов (по умолчанию из настроек)")
@click.option("--enable-enrichment/--no-enrichment", default=True, help="Включить/выключить LLM-обогащение при индексации")
@click.option("--enrichment-strategy", type=click.Choice(["full", "fast"]), help="Стратегия обогащения: 'full' (summary+concepts+tags) или 'fast' (только summary)")
def index(vault: str, path: str, max_workers: int | None, enable_enrichment: bool, enrichment_strategy: str | None) -> None:
    """Индексировать конкретный vault."""
    console.print(f"[cyan]Индексирование vault: {vault}[/cyan]")
    console.print(f"  Путь: {path}")

    async def index_async() -> None:
        services = get_services()
        embedding_service = services.embedding_service
        db_manager = services.db_manager

        if enrichment_strategy:
            settings.llm_enrichment_strategy = enrichment_strategy
            console.print(f"[cyan]Стратегия обогащения: {enrichment_strategy}[/cyan]")

        batch_processor: BatchProcessor | None = None
        indexing_stats = {
            "files_processed": 0,
            "chunks_indexed": 0,
            "start_time": time.time(),
            "errors": 0,
        }

        try:
            path_obj = Path(path)
            indexer = VaultIndexer(path_obj, vault)

            try:
                indexed_files = await db_manager.get_indexed_files(vault)
                only_changed = len(indexed_files) > 0
                if only_changed:
                    console.print(f"[cyan]Инкрементальное индексирование: найдено {len(indexed_files)} проиндексированных файлов[/cyan]")
            except Exception:
                indexed_files = None
                only_changed = False

            files_to_scan = indexer._get_files_to_scan(only_changed=only_changed, indexed_files=indexed_files)
            total_files = len(files_to_scan)

            if total_files == 0:
                if only_changed:
                    console.print("[green]✓ Все файлы актуальны, индексирование не требуется[/green]")
                else:
                    console.print("[yellow]Нет файлов для индексирования[/yellow]")
                return

            batch_processor = BatchProcessor(batch_size=32, max_workers=max_workers or settings.max_workers)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total} файлов)"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Индексирование файлов vault '{vault}'...",
                    total=total_files,
                )

                def progress_wrapper(current: int, total: int, percentage: float) -> None:
                    progress.update(task, completed=current)
                    indexing_stats["files_processed"] = current

                chunks = await indexer.scan_all(
                    only_changed=only_changed,
                    indexed_files=indexed_files,
                    max_workers=max_workers,
                    progress_callback=progress_wrapper,
                    batch_processor=batch_processor,
                )

            indexing_stats["chunks_indexed"] = len(chunks)

            if not chunks:
                if only_changed:
                    console.print("[green]✓ Все файлы актуальны, индексирование не требуется[/green]")
                else:
                    console.print("[yellow]Нет чанков для индексирования[/yellow]")
                return

            console.print("[cyan]Генерация embeddings...[/cyan]")
            texts = [chunk.content for chunk in chunks]
            batch_size = settings.batch_size

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                embedding_task = progress.add_task(
                    "[cyan]Генерация embeddings...",
                    total=len(texts),
                )

                if len(texts) > batch_size:
                    all_embeddings: list[list[float]] = []
                    for i in range(0, len(texts), batch_size):
                        batch_texts = texts[i:i + batch_size]
                        batch_embeddings = await embedding_service.get_embeddings_batch(batch_texts)
                        all_embeddings.extend(batch_embeddings)
                        progress.update(embedding_task, completed=min(i + batch_size, len(texts)))
                    embeddings = all_embeddings
                else:
                    embeddings = await embedding_service.get_embeddings_batch(texts)
                    progress.update(embedding_task, completed=len(texts))

            console.print("[cyan]Сохранение в базу данных...[/cyan]")
            await db_manager.upsert_chunks(vault, chunks, embeddings)

            enrichment_info = ""
            if enable_enrichment and chunks:
                try:
                    if settings.enable_llm_enrichment:
                        llm_service = services.llm_enrichment_service
                        if await llm_service.health_check():
                            console.print("[cyan]Обогащение чанков через LLM...[/cyan]")
                            try:
                                enrichments = await llm_service.enrich_chunks_batch(chunks)
                                enrichment_info = f" | Обогащено: {len(enrichments)}"
                                console.print(f"[green]✓ Обогащено {len(enrichments)} чанков[/green]")
                            except Exception as e:
                                logger.error(f"Error during enrichment: {e}", exc_info=True)
                                enrichment_info = " | Ошибка обогащения (продолжено без обогащения)"
                        else:
                            console.print("[yellow]LLM недоступен, пропуск обогащения[/yellow]")
                except Exception as e:
                    logger.error(f"Failed to initialize enrichment service: {e}", exc_info=True)
                    enrichment_info = " | Ошибка инициализации обогащения"

            elapsed_time = time.time() - indexing_stats["start_time"]
            file_count = len(set(c.file_path for c in chunks))
            files_per_sec = indexing_stats["files_processed"] / elapsed_time if elapsed_time > 0 else 0

            console.print("[green]✓ Индексирование завершено![/green]")
            console.print(f"  Файлов обработано: {indexing_stats['files_processed']}")
            console.print(f"  Чанков индексировано: {len(chunks)} из {file_count} файлов{enrichment_info}")
            console.print(f"  Время выполнения: {elapsed_time:.1f} сек")
            console.print(f"  Скорость: {files_per_sec:.1f} файлов/сек")

            await embedding_service.close()

        except KeyboardInterrupt:
            console.print("\n[yellow]Индексирование отменено пользователем[/yellow]")
            if batch_processor:
                batch_processor.cancel()
            try:
                await embedding_service.close()
            except Exception:
                pass
            sys.exit(130)
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            logger.exception(f"Error indexing vault {vault}")
            try:
                await embedding_service.close()
            except Exception:
                pass
            sys.exit(1)

    asyncio.run(index_async())


@click.command()
@click.option("--vault", required=True, help="Имя vault'а")
@click.option("--force", is_flag=True, help="Переиндексировать без подтверждения")
@click.option("--max-workers", type=int, help="Максимальное количество параллельных файлов (по умолчанию из настроек)")
@click.option("--enable-enrichment/--no-enrichment", default=True, help="Включить/выключить LLM-обогащение при индексации")
@click.option("--enrichment-strategy", type=click.Choice(["full", "fast"]), help="Стратегия обогащения: 'full' (summary+concepts+tags) или 'fast' (только summary)")
@click.option("--enable-clustering/--no-clustering", default=True, help="Включить/выключить кластеризацию документов при индексации")
def reindex(vault: str, force: bool, max_workers: int | None, enable_enrichment: bool, enrichment_strategy: str | None, enable_clustering: bool) -> None:
    """Переиндексировать vault из конфига."""
    import json

    from obsidian_kb.types import VaultNotFoundError

    services = get_services()
    db_manager = services.db_manager
    config_path = settings.vaults_config

    if not config_path.exists():
        console.print(f"[red]Ошибка: Конфиг не найден: {config_path}[/red]")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            vaults = config.get("vaults", [])
    except Exception as e:
        console.print(f"[red]Ошибка чтения конфига: {e}[/red]")
        sys.exit(1)

    vault_config = None
    for v in vaults:
        if v.get("name") == vault:
            vault_config = v
            break

    if not vault_config:
        async def check_vault_in_db() -> bool:
            try:
                await db_manager.get_vault_stats(vault)
                return True
            except VaultNotFoundError:
                return False
            except Exception:
                return False

        vault_exists_in_db = asyncio.run(check_vault_in_db())

        console.print(f"[red]Vault '{vault}' не найден в конфиге[/red]")
        console.print(f"Доступные vault'ы в конфиге: {', '.join(v.get('name', '?') for v in vaults)}")

        if vault_exists_in_db:
            console.print(f"\n[yellow]⚠️  Vault '{vault}' найден в базе данных, но отсутствует в конфиге[/yellow]")
            console.print("\n[cyan]Варианты решения:[/cyan]")
            console.print("1. Добавить vault в конфиг и переиндексировать:")
            console.print(f"   [green]obsidian-kb config add-vault --name \"{vault}\" --path \"/path/to/vault\"[/green]")
            console.print("2. Переиндексировать напрямую (если знаете путь):")
            console.print(f"   [green]obsidian-kb index --vault \"{vault}\" --path \"/path/to/vault\"[/green]")
        else:
            console.print(f"\n[yellow]Vault '{vault}' не найден ни в конфиге, ни в базе данных[/yellow]")
            console.print("\n[cyan]Для добавления нового vault используйте:[/cyan]")
            console.print(f"   [green]obsidian-kb config add-vault --name \"{vault}\" --path \"/path/to/vault\"[/green]")

        sys.exit(1)

    vault_path = vault_config.get("path")
    if not vault_path:
        console.print(f"[red]Путь не указан для vault '{vault}'[/red]")
        sys.exit(1)

    if not force:
        console.print(f"[yellow]Переиндексировать vault '{vault}'?[/yellow]")
        if not click.confirm("Продолжить?"):
            console.print("[yellow]Отменено[/yellow]")
            return

    console.print(f"[cyan]Переиндексирование vault: {vault}[/cyan]")
    console.print(f"  Путь: {vault_path}")

    async def reindex_async() -> None:
        services = get_services()
        embedding_service = services.embedding_service
        db_manager = services.db_manager

        if enrichment_strategy:
            settings.llm_enrichment_strategy = enrichment_strategy
            console.print(f"[cyan]Стратегия обогащения: {enrichment_strategy}[/cyan]")

        try:
            path_obj = Path(vault_path)
            if not path_obj.exists():
                console.print("[red]Ошибка: Путь не существует[/red]")
                sys.exit(1)

            embedding_cache = EmbeddingCache()
            indexer = VaultIndexer(path_obj, vault, embedding_cache=embedding_cache)

            chunks, embeddings, cache_stats = await index_with_cache(
                vault_name=vault,
                indexer=indexer,
                embedding_service=embedding_service,
                db_manager=db_manager,
                embedding_cache=embedding_cache,
                only_changed=False,
                indexed_files=None,
                max_workers=max_workers,
                enable_enrichment=enable_enrichment,
                only_new_chunks=False,
                enable_clustering=enable_clustering,
            )

            if not chunks:
                console.print("[yellow]Нет чанков для индексирования[/yellow]")
                await embedding_service.close()
                return

            await db_manager.upsert_chunks(vault, chunks, embeddings)

            file_count = len(set(c.file_path for c in chunks))
            cache_info = ""
            if cache_stats.get("cached", 0) > 0:
                cache_info = f" (из кэша: {cache_stats['cached']}, вычислено: {cache_stats['computed']})"

            enrichment_info = ""
            if enable_enrichment and "enrichment" in cache_stats:
                enrichment_stats = cache_stats["enrichment"]
                if enrichment_stats.get("enriched", 0) > 0:
                    enrichment_info = f" | Обогащено: {enrichment_stats['enriched']}"
                if enrichment_stats.get("errors", 0) > 0:
                    enrichment_info += f" | Ошибок обогащения: {enrichment_stats['errors']}"

            console.print(f"[green]✓ Переиндексировано: {len(chunks)} чанков из {file_count} файлов{cache_info}{enrichment_info}[/green]")

            await embedding_service.close()

        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            logger.exception(f"Error reindexing vault {vault}")
            try:
                await embedding_service.close()
            except Exception:
                pass
            sys.exit(1)

    asyncio.run(reindex_async())
