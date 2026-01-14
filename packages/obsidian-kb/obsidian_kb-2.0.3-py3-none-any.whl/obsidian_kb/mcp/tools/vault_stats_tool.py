"""VaultStats MCP Tool implementation."""

import logging
from typing import Any

from obsidian_kb.types import MCPVaultError
from obsidian_kb.mcp.base import InputSchema, MCPTool
from obsidian_kb.service_container import get_service_container
from obsidian_kb.types import VaultNotFoundError

logger = logging.getLogger(__name__)


class VaultStatsTool(MCPTool):
    """Tool to get detailed statistics for a specific vault."""

    @property
    def name(self) -> str:
        return "vault_stats"

    @property
    def description(self) -> str:
        return """Детальная статистика vault'а: файлы, чанки, теги, даты.

Args:
    vault_name: Имя vault'а

Returns:
    Детальная статистика в markdown формате:
    - Количество файлов и чанков
    - Размер данных
    - Список тегов
    - Даты старейшего и новейшего файлов"""

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {
                "vault_name": {
                    "type": "string",
                    "description": "Имя vault'а для получения статистики",
                },
            },
            "required": ["vault_name"],
        }

    async def execute(self, vault_name: str, **kwargs: Any) -> str:
        """Get detailed vault statistics."""
        try:
            stats = await get_service_container().db_manager.get_vault_stats(vault_name)

            lines = [f"## Статистика vault: {vault_name}\n"]
            lines.append(f"- **Файлов:** {stats.file_count}")
            lines.append(f"- **Чанков:** {stats.chunk_count}")
            lines.append(f"- **Размер:** {stats.total_size_bytes / 1024:.1f} KB")
            lines.append(f"- **Тегов:** {len(stats.tags)}")

            if stats.tags:
                lines.append(f"\n**Теги:** {', '.join(stats.tags[:20])}")
                if len(stats.tags) > 20:
                    lines.append(f"*... и ещё {len(stats.tags) - 20} тегов*")

            if stats.oldest_file:
                lines.append(
                    f"\n- **Старейший файл:** {stats.oldest_file.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            if stats.newest_file:
                lines.append(
                    f"- **Новейший файл:** {stats.newest_file.strftime('%Y-%m-%d %H:%M:%S')}"
                )

            return "\n".join(lines)

        except VaultNotFoundError:
            raise MCPVaultError(
                tool_name=self.name,
                vault_name=vault_name,
                message=f"Vault '{vault_name}' not found",
                user_message=f"Vault '{vault_name}' не найден. Используйте `index_vault` для индексирования.",
            )
        except Exception as e:
            logger.error(f"Error in vault_stats: {e}")
            return f"Ошибка получения статистики: {e}"
