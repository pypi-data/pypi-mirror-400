"""Extended Query Services для obsidian-kb.

Предоставляет расширенные возможности для структурированных запросов,
прямого текстового поиска, граф-запросов и агрегаций.
"""

from obsidian_kb.services.dataview_service import DataviewService
from obsidian_kb.services.frontmatter_api import FrontmatterAPI

__all__: list[str] = ["FrontmatterAPI", "DataviewService"]

