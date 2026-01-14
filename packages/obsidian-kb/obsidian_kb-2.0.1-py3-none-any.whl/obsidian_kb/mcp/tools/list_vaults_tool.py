"""ListVaults MCP Tool implementation."""

import logging
from typing import Any

from obsidian_kb.mcp.base import InputSchema, MCPTool
from obsidian_kb.service_container import get_service_container

logger = logging.getLogger(__name__)


class ListVaultsTool(MCPTool):
    """Tool to list all indexed vaults with statistics."""

    @property
    def name(self) -> str:
        return "list_vaults"

    @property
    def description(self) -> str:
        return """Список всех проиндексированных vault'ов со статистикой.

Returns:
    Форматированный список vault'ов с информацией о:
    - Количестве файлов
    - Количестве чанков
    - Размере
    - Тегах
    - Датах старейшего и новейшего файлов"""

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        """List all indexed vaults."""
        try:
            vault_names = await get_service_container().db_manager.list_vaults()

            if not vault_names:
                return (
                    "## Список vault'ов\n\n"
                    "*Нет проиндексированных vault'ов*\n\n"
                    "Используйте `index_vault` для индексирования."
                )

            lines = ["## Список vault'ов\n"]

            for vault_name in vault_names:
                try:
                    stats = await get_service_container().db_manager.get_vault_stats(
                        vault_name
                    )
                    lines.append(f"### {vault_name}")
                    lines.append(f"- **Файлов:** {stats.file_count}")
                    lines.append(f"- **Чанков:** {stats.chunk_count}")
                    lines.append(f"- **Размер:** {stats.total_size_bytes / 1024:.1f} KB")
                    lines.append(f"- **Тегов:** {len(stats.tags)}")
                    if stats.oldest_file:
                        lines.append(
                            f"- **Старейший файл:** {stats.oldest_file.strftime('%Y-%m-%d')}"
                        )
                    if stats.newest_file:
                        lines.append(
                            f"- **Новейший файл:** {stats.newest_file.strftime('%Y-%m-%d')}"
                        )
                    lines.append("")
                except Exception as e:
                    logger.warning(f"Error getting stats for vault '{vault_name}': {e}")
                    lines.append(f"### {vault_name}")
                    lines.append(f"- *Ошибка получения статистики: {e}*")
                    lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error in list_vaults: {e}")
            return f"Ошибка получения списка vault'ов: {e}"
