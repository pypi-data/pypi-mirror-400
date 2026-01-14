"""SystemHealth MCP Tool implementation."""

import logging
from typing import Any

from obsidian_kb.mcp.base import InputSchema, MCPTool
from obsidian_kb.service_container import get_service_container
from obsidian_kb.types import HealthStatus

logger = logging.getLogger(__name__)


class SystemHealthTool(MCPTool):
    """Tool to perform system diagnostics."""

    @property
    def name(self) -> str:
        return "system_health"

    @property
    def description(self) -> str:
        return """Диагностика системы obsidian-kb.

Проверяет:
- Ollama: доступность, наличие модели embeddings
- LanceDB: состояние базы данных
- Vaults: доступность директорий
- Disk: свободное место

Returns:
    Отчёт о состоянии системы с рекомендациями"""

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        """Perform system health check."""
        try:
            health = await get_service_container().diagnostics_service.full_check()

            status_emoji = {
                HealthStatus.OK: "✅",
                HealthStatus.WARNING: "⚠️",
                HealthStatus.ERROR: "❌",
            }

            overall_emoji = status_emoji[health.overall]

            lines = ["## 🔍 Диагностика obsidian-kb\n"]
            lines.append(f"**Общий статус:** {overall_emoji} {health.overall.value.upper()}\n")

            lines.append("| Компонент | Статус | Сообщение |")
            lines.append("|-----------|--------|-----------|")

            for check in health.checks:
                emoji = status_emoji[check.status]
                lines.append(
                    f"| {check.component} | {emoji} {check.status.value.upper()} | {check.message} |"
                )

            lines.append("")

            errors = [c for c in health.checks if c.status == HealthStatus.ERROR]
            warnings = [c for c in health.checks if c.status == HealthStatus.WARNING]

            if errors:
                lines.append("### Обнаруженные проблемы\n")
                for check in errors:
                    lines.append(f"1. **{check.component}**: {check.message}")
                    if check.details:
                        for key, value in check.details.items():
                            if isinstance(value, list) and value:
                                lines.append(
                                    f"   - {key}: {', '.join(str(v) for v in value[:5])}"
                                )
                            else:
                                lines.append(f"   - {key}: {value}")
                lines.append("")

            if warnings:
                lines.append("### Предупреждения\n")
                for check in warnings:
                    lines.append(f"- **{check.component}**: {check.message}")
                lines.append("")

            if errors or warnings:
                lines.append("### Рекомендации\n")
                if any(
                    c.component == "ollama" and c.status == HealthStatus.ERROR
                    for c in health.checks
                ):
                    lines.append("- Запустите Ollama: `ollama serve`")
                if any(
                    c.component == "vaults" and c.status == HealthStatus.WARNING
                    for c in health.checks
                ):
                    lines.append("- Проверьте пути vault'ов в `~/.obsidian-kb/vaults.json`")
                    lines.append("- Переиндексируйте vault'ы: `uv run obsidian-kb index-all`")
                lines.append("")

            lines.append(
                f"---\n*Проверка выполнена: {health.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*"
            )

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error in system_health: {e}")
            return f"Ошибка диагностики: {e}"
