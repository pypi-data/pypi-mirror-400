"""Vault commands: list_vaults, delete_vault, delete_all_vaults, enrich, cluster."""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from obsidian_kb.cli.utils import console, get_services, logger
from obsidian_kb.config import settings
from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.service_container import get_service_container
from obsidian_kb.types import VaultNotFoundError


@click.command("list-vaults")
def list_vaults() -> None:
    """Список всех проиндексированных vault'ов."""
    async def list_async() -> None:
        services = get_services()
        db_manager = services.db_manager

        try:
            vaults = await db_manager.list_vaults()
            if not vaults:
                console.print("[yellow]Нет проиндексированных vault'ов[/yellow]")
                return

            table = Table(title="Проиндексированные vault'ы")
            table.add_column("Имя", style="cyan")
            table.add_column("Файлов", style="green")
            table.add_column("Чанков", style="blue")
            table.add_column("Размер", style="yellow")

            for vault_name in vaults:
                try:
                    stats = await db_manager.get_vault_stats(vault_name)
                    table.add_row(
                        vault_name,
                        str(stats.file_count),
                        str(stats.chunk_count),
                        f"{stats.total_size_bytes / 1024:.1f} KB",
                    )
                except Exception as e:
                    logger.warning(f"Error getting stats for vault '{vault_name}': {e}")
                    table.add_row(vault_name, "?", "?", "?")

            console.print(table)

        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            logger.exception("Error listing vaults")
            sys.exit(1)

    asyncio.run(list_async())


@click.command("delete-vault")
@click.option("--vault", required=True, help="Имя vault'а")
@click.option("--force", is_flag=True, help="Удалить без подтверждения")
def delete_vault(vault: str, force: bool) -> None:
    """Удалить vault из индекса."""
    services = get_services()
    db_manager = services.db_manager

    if not force:
        console.print(f"[yellow]Удалить vault '{vault}' из индекса?[/yellow]")
        console.print("[red]Внимание: Это удалит все данные vault'а из базы, но не затронет файлы![/red]")
        if not click.confirm("Продолжить?"):
            console.print("[yellow]Отменено[/yellow]")
            return

    async def delete_async() -> None:
        try:
            await db_manager.delete_vault(vault)
            console.print(f"[green]✓ Vault '{vault}' удалён из индекса[/green]")
        except VaultNotFoundError:
            console.print(f"[yellow]Vault '{vault}' не найден в индексе[/yellow]")
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            logger.exception(f"Error deleting vault {vault}")
            sys.exit(1)

    asyncio.run(delete_async())


@click.command("delete-all-vaults")
@click.option("--force", is_flag=True, help="Удалить все vaults без подтверждения")
def delete_all_vaults(force: bool) -> None:
    """Удалить все vaults из индекса."""
    async def delete_all_async() -> None:
        services = get_services()
        db_manager = services.db_manager

        try:
            vaults = await db_manager.list_vaults()

            if not vaults:
                console.print("[yellow]В базе данных нет проиндексированных vaults[/yellow]")
                return

            console.print(f"[cyan]Найдено vaults в базе данных: {len(vaults)}[/cyan]\n")
            vault_table = Table()
            vault_table.add_column("№", style="cyan")
            vault_table.add_column("Имя vault'а", style="green")
            for idx, vault_name in enumerate(vaults, 1):
                vault_table.add_row(str(idx), vault_name)
            console.print(vault_table)

            if not force:
                console.print(f"\n[red]Внимание: Это удалит все данные всех {len(vaults)} vaults из базы![/red]")
                console.print("[yellow]Файлы в vaults не будут затронуты.[/yellow]")
                if not click.confirm("\nПродолжить?"):
                    console.print("[yellow]Отменено[/yellow]")
                    return

            embedding_cache = EmbeddingCache()
            deleted_count = 0
            errors = []

            for vault_name in vaults:
                try:
                    try:
                        await embedding_cache.clear_vault_cache(vault_name)
                        logger.info(f"Cleared embedding cache for vault '{vault_name}'")
                    except Exception as e:
                        logger.warning(f"Failed to clear cache for vault '{vault_name}': {e}")

                    await db_manager.delete_vault(vault_name)
                    console.print(f"[green]✓ Vault '{vault_name}' удалён[/green]")
                    deleted_count += 1
                except VaultNotFoundError:
                    console.print(f"[yellow]Vault '{vault_name}' не найден (возможно, уже удалён)[/yellow]")
                except Exception as e:
                    error_msg = f"Ошибка при удалении vault '{vault_name}': {e}"
                    console.print(f"[red]✗ {error_msg}[/red]")
                    errors.append(error_msg)
                    logger.exception(f"Error deleting vault {vault_name}")

            console.print(f"\n[cyan]Итого: удалено {deleted_count} из {len(vaults)} vaults[/cyan]")
            if errors:
                console.print(f"[red]Ошибок: {len(errors)}[/red]")
                for error in errors:
                    console.print(f"  - {error}")
            else:
                console.print("[green]Все vaults успешно удалены из индекса[/green]")

        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            logger.exception("Error deleting all vaults")
            sys.exit(1)

    asyncio.run(delete_all_async())


@click.command()
@click.option("--vault", required=True, help="Имя vault'а")
@click.option("--enrichment-strategy", type=click.Choice(["full", "fast"]), help="Стратегия обогащения: 'full' (summary+concepts+tags) или 'fast' (только summary)")
@click.option("--force", is_flag=True, help="Принудительно обогащать все чанки, даже если они уже обогащены")
def enrich(vault: str, enrichment_strategy: str | None, force: bool) -> None:
    """Принудительно обогатить все чанки vault'а через LLM."""
    console.print(f"[cyan]Обогащение чанков vault: {vault}[/cyan]")

    async def enrich_async() -> None:
        from obsidian_kb.types import DocumentChunk

        services = get_service_container()
        db_manager = services.db_manager
        llm_service = services.llm_enrichment_service

        if enrichment_strategy:
            settings.llm_enrichment_strategy = enrichment_strategy
            console.print(f"[cyan]Стратегия обогащения: {enrichment_strategy}[/cyan]")

        if not await llm_service.health_check():
            console.print("[red]❌ LLM недоступен. Проверьте, что Ollama запущен и модель доступна.[/red]")
            return

        try:
            console.print("[cyan]Получение чанков из базы данных...[/cyan]")
            chunks_table = await db_manager._ensure_table(vault, "chunks")
            documents_table = await db_manager._ensure_table(vault, "documents")

            def _get_all_chunks() -> list[dict[str, Any]]:
                try:
                    arrow_table = chunks_table.to_arrow()
                    if arrow_table.num_rows == 0:
                        return []
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    return arrow_table.to_pylist()
                except Exception as e:
                    logger.error(f"Error getting chunks: {e}")
                    return []

            chunk_rows = await asyncio.to_thread(_get_all_chunks)

            if not chunk_rows:
                console.print("[yellow]Нет чанков для обогащения[/yellow]")
                return

            console.print(f"[green]Найдено чанков: {len(chunk_rows)}[/green]")

            def _get_documents() -> dict[str, dict[str, Any]]:
                try:
                    arrow_table = documents_table.to_arrow()
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    rows = arrow_table.to_pylist()
                    return {row.get("document_id", ""): row for row in rows}
                except Exception:
                    return {}

            documents = await asyncio.to_thread(_get_documents)

            document_chunks: list[DocumentChunk] = []
            for row in chunk_rows:
                chunk_id = row.get("chunk_id", "")
                document_id = row.get("document_id", "")

                if "::" in document_id:
                    _, file_path = document_id.split("::", 1)
                elif "::" in chunk_id:
                    parts = chunk_id.split("::")
                    if len(parts) >= 2:
                        file_path = parts[1]
                    else:
                        file_path = chunk_id
                else:
                    file_path = document_id

                doc_info = documents.get(document_id, {})
                title = doc_info.get("title", file_path)

                chunk_index = 0
                if "::" in chunk_id:
                    parts = chunk_id.split("::")
                    if len(parts) >= 3:
                        try:
                            chunk_index = int(parts[-1])
                        except ValueError:
                            pass

                created_at = None
                modified_at = datetime.now()
                if doc_info:
                    created_at_str = doc_info.get("created_at")
                    modified_at_str = doc_info.get("modified_at")
                    if created_at_str:
                        try:
                            if isinstance(created_at_str, str):
                                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                            else:
                                created_at = created_at_str
                        except Exception:
                            pass
                    if modified_at_str:
                        try:
                            if isinstance(modified_at_str, str):
                                modified_at = datetime.fromisoformat(modified_at_str.replace("Z", "+00:00"))
                            else:
                                modified_at = modified_at_str
                        except Exception:
                            pass

                inline_tags = row.get("inline_tags", []) or []
                tags = inline_tags.copy()

                chunk = DocumentChunk(
                    id=chunk_id,
                    vault_name=vault,
                    file_path=file_path,
                    title=title,
                    section=row.get("section", ""),
                    content=row.get("content", ""),
                    tags=tags,
                    frontmatter_tags=[],
                    inline_tags=inline_tags,
                    links=row.get("links", []) or [],
                    created_at=created_at,
                    modified_at=modified_at,
                    metadata={},
                )
                document_chunks.append(chunk)

            console.print(f"[cyan]Подготовлено чанков для обогащения: {len(document_chunks)}[/cyan]")

            if not force:
                console.print("[cyan]Проверка уже обогащенных чанков...[/cyan]")
                enrichment_repo = services.chunk_enrichment_repository

                chunks_to_enrich = []
                for chunk in document_chunks:
                    existing = await enrichment_repo.get(vault, chunk.id)
                    if not existing:
                        chunks_to_enrich.append(chunk)

                skipped = len(document_chunks) - len(chunks_to_enrich)
                if skipped > 0:
                    console.print(f"[yellow]Пропущено уже обогащенных чанков: {skipped}[/yellow]")

                document_chunks = chunks_to_enrich

            if not document_chunks:
                console.print("[green]✓ Все чанки уже обогащены. Используйте --force для принудительного обогащения.[/green]")
                return

            console.print(f"[cyan]Обогащение {len(document_chunks)} чанков через LLM...[/cyan]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total} чанков)"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "[cyan]Обогащение чанков...",
                    total=len(document_chunks),
                )

                batch_size = 5
                enriched_count = 0
                error_count = 0

                for i in range(0, len(document_chunks), batch_size):
                    batch = document_chunks[i:i + batch_size]
                    try:
                        recovery_service = services.recovery_service
                        circuit_breaker = recovery_service.get_circuit_breaker("llm_enrichment")

                        if not circuit_breaker.can_proceed():
                            console.print(f"[yellow]⚠️  Circuit Breaker открыт, пропускаем батч {i//batch_size + 1}[/yellow]")
                            console.print("[cyan]Используйте 'obsidian-kb reset-circuit-breaker' для сброса[/cyan]")
                            error_count += len(batch)
                            await asyncio.sleep(5)
                            continue

                        enrichments = await llm_service.enrich_chunks_batch(batch)
                        enriched_count += len(enrichments)

                        if i + batch_size < len(document_chunks):
                            await asyncio.sleep(0.2)

                    except Exception as e:
                        logger.error(f"Error enriching batch {i//batch_size + 1}: {e}")
                        error_count += len(batch)
                        await asyncio.sleep(2)
                    finally:
                        progress.update(task, completed=min(i + batch_size, len(document_chunks)))

            console.print()
            console.print("[green]✓ Обогащение завершено![/green]")
            console.print(f"  Обогащено: {enriched_count}")
            if error_count > 0:
                console.print(f"  Ошибок: {error_count}")

        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            logger.exception(f"Error enriching vault {vault}")
            sys.exit(1)

    asyncio.run(enrich_async())


@click.command()
@click.option("--vault", required=True, help="Имя vault'а")
@click.option("--method", type=click.Choice(["kmeans", "dbscan"]), default="kmeans", help="Метод кластеризации")
@click.option("--n-clusters", type=int, help="Количество кластеров (только для kmeans, None для автоопределения)")
@click.option("--force", is_flag=True, help="Пересоздать кластеры даже если они уже существуют")
def cluster(vault: str, method: str, n_clusters: int | None, force: bool) -> None:
    """Кластеризация документов vault'а."""
    console.print(f"[cyan]Кластеризация документов vault: {vault}[/cyan]")

    async def cluster_async() -> None:
        try:
            services = get_service_container()
            cluster_service = services.knowledge_cluster_service

            if not force:
                cluster_repo = services.knowledge_cluster_repository
                existing_clusters = await cluster_repo.get_all(vault)
                if existing_clusters:
                    console.print(f"[yellow]Найдено {len(existing_clusters)} существующих кластеров[/yellow]")
                    if not click.confirm("Пересоздать кластеры?"):
                        console.print("[yellow]Отменено[/yellow]")
                        return

            console.print(f"[cyan]Метод кластеризации: {method}[/cyan]")
            if n_clusters:
                console.print(f"[cyan]Количество кластеров: {n_clusters}[/cyan]")
            else:
                console.print("[cyan]Количество кластеров: автоматическое определение[/cyan]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Кластеризация документов vault '{vault}'...",
                    total=None,
                )

                clusters = await cluster_service.cluster_documents(
                    vault_name=vault,
                    n_clusters=n_clusters,
                    method=method,
                )

                progress.update(task, completed=100)

            if not clusters:
                console.print("[yellow]Не удалось создать кластеры[/yellow]")
                return

            cluster_repo = services.knowledge_cluster_repository
            await cluster_repo.upsert(vault, clusters)

            console.print(f"[green]✓ Создано {len(clusters)} кластеров[/green]")
            for idx, cluster_item in enumerate(clusters[:10], 1):
                console.print(f"  {idx}. {cluster_item.cluster_name} ({len(cluster_item.document_ids)} документов)")
            if len(clusters) > 10:
                console.print(f"  ... и ещё {len(clusters) - 10} кластеров")

        except VaultNotFoundError as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Ошибка кластеризации: {e}[/red]")
            logger.exception(f"Error clustering vault {vault}")
            sys.exit(1)

    asyncio.run(cluster_async())
