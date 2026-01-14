"""Базовый класс для стратегий поиска."""

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from obsidian_kb.types import DocumentSearchResult

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IDocumentRepository


class BaseSearchStrategy(ABC):
    """Базовый класс для стратегий поиска.
    
    Предоставляет общие утилиты для работы с фильтрами и документами.
    """

    def __init__(
        self,
        document_repo: "IDocumentRepository",
    ) -> None:
        """Инициализация базовой стратегии.
        
        Args:
            document_repo: Репозиторий документов для работы с метаданными
        """
        self._documents = document_repo

    @property
    @abstractmethod
    def name(self) -> str:
        """Имя стратегии для логирования."""
        ...

    @abstractmethod
    async def search(
        self,
        vault_name: str,
        query: str,
        parsed_filters: dict[str, Any],
        limit: int = 10,
        options: dict[str, Any] | None = None,
    ) -> list[DocumentSearchResult]:
        """Выполнение поиска согласно стратегии.
        
        Args:
            vault_name: Имя vault'а
            query: Текстовый запрос (может быть пустым)
            parsed_filters: Извлечённые фильтры (может быть ParsedQuery или dict)
            limit: Максимум результатов
            options: Дополнительные опции (include_content, max_content_length, search_type)
        """
        ...

    async def _apply_filters(
        self,
        vault_name: str,
        parsed_filters: dict[str, Any],
    ) -> set[str]:
        """Применение фильтров для получения document_ids.
        
        Args:
            vault_name: Имя vault'а
            parsed_filters: Извлечённые фильтры (может быть ParsedQuery или dict)
            
        Returns:
            Множество document_ids, соответствующих фильтрам
        """
        all_ids: set[str] | None = None
        
        # Конвертируем ParsedQuery в dict если нужно
        filters = self._normalize_filters(parsed_filters)
        
        # Фильтр по типу документа
        if doc_type := filters.get("doc_type"):
            ids = await self._documents.find_by_property(vault_name, "type", doc_type)
            all_ids = ids if all_ids is None else all_ids & ids
        
        # Фильтр по типам документов (OR)
        # ОПТИМИЗАЦИЯ: Параллельные запросы для разных типов
        if doc_type_or := filters.get("doc_type_or"):
            # Параллельно получаем document_ids для всех типов
            tasks = [
                self._documents.find_by_property(vault_name, "type", doc_type)
                for doc_type in doc_type_or
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            ids = set()
            for result in results:
                if isinstance(result, Exception):
                    # Логируем ошибку, но продолжаем обработку других типов
                    continue
                ids.update(result)
            all_ids = ids if all_ids is None else all_ids & ids
        
        # Фильтр по тегам (AND)
        if tags := filters.get("tags"):
            ids = await self._documents.find_by_tags(vault_name, tags, match_all=True)
            all_ids = ids if all_ids is None else all_ids & ids
        
        # Фильтр по тегам (OR)
        if tags_or := filters.get("tags_or"):
            ids = await self._documents.find_by_tags(vault_name, tags_or, match_all=False)
            all_ids = ids if all_ids is None else all_ids & ids
        
        # Фильтр по датам
        if date_filters := filters.get("date_filters"):
            for field, conditions in date_filters.items():
                if isinstance(conditions, dict):
                    # Поддержка формата с after/before (нормализованный формат из парсера)
                    after = conditions.get("after")
                    before = conditions.get("before")
                    after_exclusive = conditions.get("after_exclusive", False)  # True для оператора >
                    before_exclusive = conditions.get("before_exclusive", False)  # True для оператора <
                    
                    if after or before:
                        # Используем поле created_at или modified_at
                        field_name = f"{field}_at" if not field.endswith("_at") else field
                        ids = await self._documents.find_by_date_range(
                            vault_name, field_name, after=after, before=before,
                            after_exclusive=after_exclusive, before_exclusive=before_exclusive
                        )
                        all_ids = ids if all_ids is None else all_ids & ids
        
        # Фильтр по ссылкам (AND) - двухэтапный запрос через chunks
        if links := filters.get("links"):
            ids = await self._documents.find_by_links(vault_name, links, match_all=True)
            all_ids = ids if all_ids is None else all_ids & ids
        
        # Фильтр по ссылкам (OR) - двухэтапный запрос через chunks
        if links_or := filters.get("links_or"):
            ids = await self._documents.find_by_links(vault_name, links_or, match_all=False)
            all_ids = ids if all_ids is None else all_ids & ids
        
        # Фильтр по ссылкам (NOT) - двухэтапный запрос через chunks
        if links_not := filters.get("links_not"):
            # Получаем документы с указанными ссылками и исключаем их
            ids_to_exclude = await self._documents.find_by_links(vault_name, links_not, match_all=False)
            if all_ids is not None:
                all_ids -= ids_to_exclude
            # Если all_ids is None, то фильтр NOT не имеет смысла без других фильтров
            # В этом случае пропускаем фильтр (все документы уже включены)
        
        return all_ids or set()

    def _normalize_filters(self, parsed_filters: dict[str, Any]) -> dict[str, Any]:
        """Нормализация фильтров из ParsedQuery или dict в единый формат.
        
        Args:
            parsed_filters: ParsedQuery объект или dict
            
        Returns:
            Нормализованный словарь фильтров
        """
        # Если это уже dict, возвращаем как есть
        if isinstance(parsed_filters, dict) and not hasattr(parsed_filters, 'text_query'):
            return parsed_filters
        
        # Если это ParsedQuery, конвертируем в dict
        if hasattr(parsed_filters, 'text_query'):
            return {
                'tags': parsed_filters.tags,
                'tags_or': parsed_filters.tags_or,
                'tags_not': parsed_filters.tags_not,
                'inline_tags': parsed_filters.inline_tags,
                'inline_tags_or': parsed_filters.inline_tags_or,
                'inline_tags_not': parsed_filters.inline_tags_not,
                'date_filters': parsed_filters.date_filters,
                'doc_type': parsed_filters.doc_type,
                'doc_type_or': parsed_filters.doc_type_or,
                'doc_type_not': parsed_filters.doc_type_not,
                'links': parsed_filters.links,
                'links_or': parsed_filters.links_or,
                'links_not': parsed_filters.links_not,
            }
        
        return parsed_filters if isinstance(parsed_filters, dict) else {}

