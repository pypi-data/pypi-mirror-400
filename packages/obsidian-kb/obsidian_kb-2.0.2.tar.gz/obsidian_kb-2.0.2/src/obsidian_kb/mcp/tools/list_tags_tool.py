"""ListTags MCP Tool implementation."""

import logging
from typing import Any

from obsidian_kb.types import MCPVaultError
from obsidian_kb.mcp.base import InputSchema, MCPTool
from obsidian_kb.service_container import get_service_container
from obsidian_kb.types import VaultNotFoundError

logger = logging.getLogger(__name__)


class ListTagsTool(MCPTool):
    """Tool to list all tags in a vault."""

    @property
    def name(self) -> str:
        return "list_tags"

    @property
    def description(self) -> str:
        return """Получить список всех тегов в vault'е для автодополнения.

Args:
    vault_name: Имя vault'а
    limit: Максимум тегов для возврата (default: 100)

Returns:
    Список тегов в markdown формате"""

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {
                "vault_name": {
                    "type": "string",
                    "description": "Имя vault'а",
                },
                "limit": {
                    "type": "integer",
                    "description": "Максимум тегов для возврата (default: 100)",
                },
            },
            "required": ["vault_name"],
        }

    async def execute(self, vault_name: str, limit: int = 100, **kwargs: Any) -> str:
        """List all tags in the vault."""
        try:
            db_manager = get_service_container().db_manager
            stats = await db_manager.get_vault_stats(vault_name)

            if not stats.tags:
                return f"## Теги в vault: {vault_name}\n\n*Теги не найдены*"

            sorted_tags = sorted(stats.tags)[:limit]

            lines = [f"## Теги в vault: {vault_name}\n"]
            lines.append(f"*Найдено {len(stats.tags)} уникальных тегов*\n")

            for tag in sorted_tags:
                lines.append(f"- `{tag}`")

            if len(stats.tags) > limit:
                lines.append(f"\n*... и ещё {len(stats.tags) - limit} тегов*")

            return "\n".join(lines)

        except VaultNotFoundError:
            raise MCPVaultError(
                tool_name=self.name,
                vault_name=vault_name,
                message=f"Vault '{vault_name}' not found",
                user_message=f"Vault '{vault_name}' не найден.",
            )
        except Exception as e:
            logger.error(f"Error in list_tags: {e}", exc_info=True)
            return f"Ошибка получения тегов: {e}"
