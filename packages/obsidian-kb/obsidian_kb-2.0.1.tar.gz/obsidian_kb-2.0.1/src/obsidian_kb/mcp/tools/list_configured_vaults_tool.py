"""ListConfiguredVaults MCP Tool implementation."""

import json
import logging
from pathlib import Path
from typing import Any

from obsidian_kb.config import settings
from obsidian_kb.mcp.base import InputSchema, MCPTool
from obsidian_kb.service_container import get_service_container

logger = logging.getLogger(__name__)


class ListConfiguredVaultsTool(MCPTool):
    """Tool to list all configured vaults from config file."""

    @property
    def name(self) -> str:
        return "list_configured_vaults"

    @property
    def description(self) -> str:
        return """Получить список всех vault'ов из конфигурации obsidian-kb.

Returns:
    Список всех настроенных vault'ов с их путями и статусом индексации"""

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        """List all configured vaults."""
        try:
            config_path = settings.vaults_config

            if not config_path.exists():
                return (
                    "## Настроенные vault'ы\n\n"
                    "*Конфигурационный файл не найден. Vault'ы не настроены.*"
                )

            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            vaults = config.get("vaults", [])

            if not vaults:
                return (
                    "## Настроенные vault'ы\n\n"
                    "*Нет настроенных vault'ов.*\n\n"
                    "Используйте `add_vault_to_config` для добавления."
                )

            lines = ["## Настроенные vault'ы\n"]

            for idx, vault in enumerate(vaults, 1):
                vault_name = vault.get("name", "не указано")
                vault_path = vault.get("path", "не указано")

                path_exists = "✅" if Path(vault_path).exists() else "❌"

                lines.append(f"### {idx}. {vault_name} {path_exists}")
                lines.append(f"- **Путь:** {vault_path}")

                try:
                    indexed_files = await get_service_container().db_manager.get_indexed_files(
                        vault_name
                    )
                    if indexed_files:
                        lines.append(
                            f"- **Статус:** Проиндексирован ({len(indexed_files)} файлов)"
                        )
                    else:
                        lines.append("- **Статус:** Не проиндексирован")
                except Exception:
                    lines.append("- **Статус:** Не проиндексирован")

                lines.append("")

            lines.append(f"---\n*Конфигурация: {config_path}*")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error in list_configured_vaults: {e}", exc_info=True)
            return f"Ошибка получения списка vault'ов: {e}"
