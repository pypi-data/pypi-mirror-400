"""Config commands: config group (show, add_vault, remove_vault)."""

import asyncio
import json
import sys
from pathlib import Path

import click
from rich.table import Table

from obsidian_kb.cli.utils import console, get_services, logger
from obsidian_kb.config import settings
from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.indexing_utils import index_with_cache
from obsidian_kb.vault_indexer import VaultIndexer


@click.group()
def config() -> None:
    """Управление конфигурацией."""
    pass


@config.command()
def show() -> None:
    """Показать текущую конфигурацию."""
    console.print("[cyan]Текущая конфигурация:[/cyan]\n")

    table = Table()
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("База данных", str(settings.db_path))
    table.add_row("Конфиг vault'ов", str(settings.vaults_config))
    table.add_row("Ollama URL", settings.ollama_url)
    table.add_row("Модель embeddings", settings.embedding_model)
    table.add_row("Размерность", str(settings.embedding_dimensions))
    table.add_row("Размер чанка", str(settings.chunk_size))
    table.add_row("Перекрытие чанков", str(settings.chunk_overlap))
    table.add_row("Размер батча", str(settings.batch_size))
    table.add_row("Макс. параллельных файлов", str(settings.max_workers))
    table.add_row("Тип поиска", settings.default_search_type)
    table.add_row("Hybrid alpha", str(settings.hybrid_alpha))

    console.print(table)

    config_path = settings.vaults_config
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                vaults = config_data.get("vaults", [])
                if vaults:
                    console.print(f"\n[cyan]Vault'ы в конфиге ({len(vaults)}):[/cyan]")
                    vault_table = Table()
                    vault_table.add_column("Имя", style="cyan")
                    vault_table.add_column("Путь", style="green")
                    for v in vaults:
                        vault_table.add_row(v.get("name", "?"), v.get("path", "?"))
                    console.print(vault_table)
        except Exception as e:
            console.print(f"[yellow]Ошибка чтения конфига vault'ов: {e}[/yellow]")


@config.command("add-vault")
@click.option("--name", required=True, help="Имя vault'а")
@click.option("--path", required=True, type=click.Path(exists=True, file_okay=False), help="Путь к vault'у")
@click.option("--no-index", is_flag=True, help="Не индексировать vault после добавления")
def add_vault(name: str, path: str, no_index: bool) -> None:
    """Добавить vault в конфигурацию."""
    config_path = settings.vaults_config
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            console.print(f"[yellow]Ошибка чтения конфига: {e}, создаём новый[/yellow]")
            config_data = {"vaults": []}
    else:
        config_data = {"vaults": []}

    vaults = config_data.get("vaults", [])
    is_new_vault = True

    for v in vaults:
        if v.get("name") == name:
            console.print(f"[yellow]Vault '{name}' уже существует[/yellow]")
            if click.confirm("Обновить путь?"):
                v["path"] = path
                console.print("[green]✓ Путь обновлён[/green]")
                is_new_vault = False
            else:
                return
            break
        if v.get("path") == path:
            console.print(f"[yellow]Vault с путём '{path}' уже существует (имя: {v.get('name')})[/yellow]")
            return
    else:
        vaults.append({"name": name, "path": path})
        console.print(f"[green]✓ Vault '{name}' добавлен[/green]")

    config_data["vaults"] = vaults

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    console.print(f"  Имя: {name}")
    console.print(f"  Путь: {path}")
    console.print(f"  Конфиг: {config_path}")

    if not no_index and is_new_vault:
        console.print(f"\n[cyan]Начинаю индексацию vault '{name}'...[/cyan]")

        async def index_new_vault() -> None:
            services = get_services()
            embedding_service = services.embedding_service
            db_manager = services.db_manager

            try:
                path_obj = Path(path)
                embedding_cache = EmbeddingCache()
                indexer = VaultIndexer(path_obj, name, embedding_cache=embedding_cache)

                chunks, embeddings, cache_stats = await index_with_cache(
                    vault_name=name,
                    indexer=indexer,
                    embedding_service=embedding_service,
                    db_manager=db_manager,
                    embedding_cache=embedding_cache,
                    only_changed=False,
                    indexed_files=None,
                    max_workers=None,
                    enable_clustering=True,
                )

                if not chunks:
                    console.print("[yellow]Нет чанков для индексирования[/yellow]")
                    await embedding_service.close()
                    return

                await db_manager.upsert_chunks(name, chunks, embeddings)

                file_count = len(set(c.file_path for c in chunks))
                cache_info = ""
                if cache_stats["cached"] > 0:
                    cache_info = f" (из кэша: {cache_stats['cached']}, вычислено: {cache_stats['computed']})"
                console.print(f"[green]✓ Индексировано: {len(chunks)} чанков из {file_count} файлов{cache_info}[/green]")

                await embedding_service.close()

            except Exception as e:
                console.print(f"[red]Ошибка индексирования: {e}[/red]")
                logger.exception(f"Error indexing vault {name}")
                try:
                    await embedding_service.close()
                except Exception:
                    pass

        asyncio.run(index_new_vault())


@config.command("remove-vault")
@click.option("--name", required=True, help="Имя vault'а")
def remove_vault(name: str) -> None:
    """Удалить vault из конфигурации."""
    config_path = settings.vaults_config

    if not config_path.exists():
        console.print(f"[yellow]Конфиг не найден: {config_path}[/yellow]")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            vaults = config_data.get("vaults", [])
    except Exception as e:
        console.print(f"[red]Ошибка чтения конфига: {e}[/red]")
        sys.exit(1)

    original_count = len(vaults)
    vaults = [v for v in vaults if v.get("name") != name]

    if len(vaults) == original_count:
        console.print(f"[yellow]Vault '{name}' не найден в конфиге[/yellow]")
        return

    config_data["vaults"] = vaults

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    console.print(f"[green]✓ Vault '{name}' удалён из конфига[/green]")
