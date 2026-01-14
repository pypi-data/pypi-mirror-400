"""Search commands: search, search_links."""

import asyncio
import json
import sys
from pathlib import Path

import click
from rich.table import Table

from obsidian_kb.cli.utils import console, get_services, logger
from obsidian_kb.metrics import MetricsCollector
from obsidian_kb.types import VaultNotFoundError
from obsidian_kb.validation import validate_search_params


@click.command()
@click.option("--vault", required=True, help="Имя vault'а")
@click.option("--query", required=True, help="Поисковый запрос")
@click.option("--limit", default=10, help="Максимум результатов")
@click.option("--type", "search_type", default="hybrid", type=click.Choice(["vector", "fts", "hybrid"]), help="Тип поиска")
@click.option("--export", "export_path", type=click.Path(), help="Путь для экспорта результатов")
@click.option("--format", "export_format", type=click.Choice(["json", "markdown", "csv"]), default="json", help="Формат экспорта")
def search(vault: str, query: str, limit: int, search_type: str, export_path: str | None, export_format: str) -> None:
    """Тестовый поиск."""
    validate_search_params(query=query, vault_name=vault, limit=limit, search_type=search_type)

    async def search_async() -> None:
        services = get_services()
        try:
            from obsidian_kb.types import RetrievalGranularity, SearchRequest

            request = SearchRequest(
                vault_name=vault,
                query=query,
                limit=limit,
                search_type=search_type,
                granularity=RetrievalGranularity.AUTO,
                include_content=True,
            )

            response = await services.search_service.search(request)

            if not response.results:
                console.print("[yellow]Результаты не найдены[/yellow]")
                return

            if export_path:
                export_file = Path(export_path)
                if export_format == "json":
                    json_data = services.formatter.format_json(response)
                    export_file.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
                elif export_format == "markdown":
                    markdown_text = services.formatter.format_markdown(response)
                    export_file.write_text(markdown_text, encoding="utf-8")
                elif export_format == "csv":
                    import csv
                    with open(export_file, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Rank", "Title", "File", "Score", "Tags", "Snippet"])
                        for idx, r in enumerate(response.results, 1):
                            writer.writerow([
                                idx,
                                r.document.title,
                                r.document.file_path,
                                f"{r.score.value:.2f}",
                                ", ".join(r.document.tags),
                                r.snippet[:500] if r.snippet else "",
                            ])
                console.print(f"[green]✓ Результаты экспортированы в {export_file}[/green]")
                return

            table = Table(title=f"Результаты поиска: {query}")
            table.add_column("№", style="cyan")
            table.add_column("Заголовок", style="green")
            table.add_column("Файл", style="blue")
            table.add_column("Релевантность", style="yellow")
            table.add_column("Превью", style="white")

            for idx, result in enumerate(response.results, 1):
                preview = result.snippet[:100] + "..." if result.snippet and len(result.snippet) > 100 else (result.snippet or "")
                table.add_row(
                    str(idx),
                    result.document.title,
                    result.document.file_path,
                    f"{result.score.value:.2f} ({result.score.label})",
                    preview,
                )

            console.print(table)
            console.print(f"\n[dim]Найдено: {response.total_found} документов | Время: {response.execution_time_ms:.0f} мс | Intent: {response.detected_intent.value}[/dim]")

            try:
                metrics_collector = MetricsCollector()
                await metrics_collector.record_search(
                    vault_name=vault,
                    query=query,
                    search_type=search_type,
                    result_count=response.total_found,
                    execution_time_ms=response.execution_time_ms,
                )
            except Exception as e:
                logger.warning(f"Failed to record search metric: {e}")

        except VaultNotFoundError:
            console.print(f"[red]Vault '{vault}' не найден[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Ошибка поиска: {e}[/red]")
            logger.exception("Error in search")
            sys.exit(1)

    asyncio.run(search_async())


@click.command("search-links")
@click.argument("vault")
@click.argument("link_name")
@click.option("--limit", default=10, help="Максимум результатов")
def search_links(vault: str, link_name: str, limit: int) -> None:
    """Поиск заметок, связанных с указанной заметкой через wikilinks."""
    async def search_links_async() -> None:
        services = get_services()
        db_manager = services.db_manager

        try:
            results = await db_manager.search_by_links(vault, link_name, limit=limit)

            if not results:
                console.print(f"[yellow]Заметки, связанные с '{link_name}', не найдены[/yellow]")
                return

            table = Table(title=f"Заметки, связанные с '{link_name}'")
            table.add_column("№", style="cyan")
            table.add_column("Заголовок", style="green")
            table.add_column("Файл", style="blue")
            table.add_column("Превью", style="white")

            for idx, result in enumerate(results, 1):
                preview = result.content[:100] + "..." if len(result.content) > 100 else result.content
                table.add_row(
                    str(idx),
                    result.title,
                    result.file_path,
                    preview,
                )

            console.print(table)

            try:
                metrics_collector = MetricsCollector()
                await metrics_collector.record_search(
                    vault_name=vault,
                    query=f"links:{link_name}",
                    search_type="links",
                    result_count=len(results),
                    execution_time_ms=0.0,
                )
            except Exception as e:
                logger.warning(f"Failed to record search metric: {e}")

        except VaultNotFoundError:
            console.print(f"[red]Vault '{vault}' не найден[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Ошибка поиска: {e}[/red]")
            logger.exception("Error in search_links")
            sys.exit(1)

    asyncio.run(search_links_async())
