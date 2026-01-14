"""IndexVault MCP Tool implementation."""

import logging
from pathlib import Path
from typing import Any

from obsidian_kb.embedding_cache import EmbeddingCache
from obsidian_kb.indexing_utils import index_with_cache
from obsidian_kb.mcp.base import InputSchema, MCPTool
from obsidian_kb.mcp_server import get_job_queue
from obsidian_kb.service_container import get_service_container
from obsidian_kb.vault_indexer import VaultIndexer

logger = logging.getLogger(__name__)


class IndexVaultTool(MCPTool):
    """Tool to index or reindex an Obsidian vault."""

    @property
    def name(self) -> str:
        return "index_vault"

    @property
    def description(self) -> str:
        return """Переиндексировать vault (или создать новый индекс).

Индексация выполняется в фоновом режиме, чтобы не блокировать агента.

Args:
    vault_name: Имя vault'а
    vault_path: Путь к vault'у

Returns:
    Результат запуска индексации (ID задачи для отслеживания)"""

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {
                "vault_name": {
                    "type": "string",
                    "description": "Имя vault'а",
                },
                "vault_path": {
                    "type": "string",
                    "description": "Путь к vault'у",
                },
            },
            "required": ["vault_name", "vault_path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        """Execute vault indexing."""
        vault_name: str = kwargs["vault_name"]
        vault_path: str = kwargs["vault_path"]

        container = get_service_container()

        if container.mcp_rate_limiter:
            await container.mcp_rate_limiter.acquire()

        try:
            vault_path_obj = Path(vault_path)
            if not vault_path_obj.exists():
                return f"Ошибка: Путь '{vault_path}' не существует."

            if not vault_path_obj.is_dir():
                return f"Ошибка: Путь '{vault_path}' не является директорией."

            # Проверяем инкрементальное индексирование
            indexed_files = None
            try:
                indexed_files = await container.db_manager.get_indexed_files(vault_name)
                only_changed = len(indexed_files) > 0
            except Exception as e:
                logger.debug(f"Failed to get indexed files, using full indexing: {e}")
                only_changed = False

            # Запускаем индексацию в фоне
            job_queue = get_job_queue()
            if job_queue:
                from obsidian_kb.indexing.job_queue import JobPriority

                try:
                    job = await job_queue.enqueue(
                        vault_name=vault_name,
                        vault_path=vault_path_obj,
                        operation="index_vault",
                        params={"only_changed": only_changed},
                        priority=JobPriority.NORMAL,
                    )

                    lines = [f"## Индексация vault '{vault_name}' запущена в фоне\n"]
                    lines.append(f"- **ID задачи:** `{job.id}`")
                    lines.append(f"- **Статус:** {job.status.value}")
                    lines.append(
                        f"- **Режим:** {'Инкрементальное' if only_changed else 'Полное'}"
                    )
                    lines.append(f"\nИспользуйте `get_job_status` для проверки прогресса.")
                    return "\n".join(lines)
                except Exception as e:
                    logger.error(f"Ошибка запуска фоновой индексации: {e}", exc_info=True)
                    return f"Ошибка запуска индексации: {e}"
            else:
                # Fallback: синхронная индексация если очередь недоступна
                logger.warning("Job queue недоступна, выполняем синхронную индексацию")
                indexer = VaultIndexer(vault_path_obj, vault_name)
                embedding_cache = EmbeddingCache()
                chunks, embeddings, stats = await index_with_cache(
                    vault_name=vault_name,
                    indexer=indexer,
                    embedding_service=container.embedding_service,
                    db_manager=container.db_manager,
                    embedding_cache=embedding_cache,
                    only_changed=only_changed,
                    indexed_files=indexed_files,
                )

                if not chunks:
                    if only_changed:
                        return f"Vault '{vault_name}': все файлы актуальны, индексирование не требуется."
                    return f"Vault '{vault_name}' просканирован, но не найдено чанков для индексирования."

                # Сохраняем в БД
                await container.db_manager.upsert_chunks(vault_name, chunks, embeddings)

                file_count = len(set(c.file_path for c in chunks))
                cache_info = (
                    f" (кэш: {stats.get('cached', 0)}, вычислено: {stats.get('computed', 0)})"
                    if stats
                    else ""
                )
                return f"Vault '{vault_name}' успешно проиндексирован: {len(chunks)} чанков из {file_count} файлов{cache_info}."

        except Exception as e:
            logger.error(f"Error in index_vault: {e}")
            return f"Ошибка индексирования: {e}"
