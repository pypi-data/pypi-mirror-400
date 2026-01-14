"""Модуль для построения SQL фильтров для поиска.

Обеспечивает типобезопасное построение WHERE условий
для различных типов фильтров.

В v4 поддерживает двухэтапные запросы через таблицу properties
для фильтрации по произвольным свойствам документов.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from obsidian_kb.fuzzy_matching import FuzzyMatcher
from obsidian_kb.normalization import DataNormalizer
from obsidian_kb.relative_date_parser import RelativeDateParser

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IDatabaseManager

logger = logging.getLogger(__name__)


@dataclass
class FilterCondition:
    """Условие фильтра для WHERE clause."""
    sql: str
    params: dict[str, Any] | None = None


class TagFilter:
    """Фильтр по тегам.
    
    ВНИМАНИЕ (v4): Для frontmatter тегов этот метод НЕ должен использоваться напрямую.
    В v4 frontmatter_tags хранятся в таблице metadata, а не в chunks, поэтому для них
    используется двухэтапный запрос через FilterBuilder.build_where_clause().
    
    Этот метод используется только для inline тегов, которые хранятся в таблице chunks.
    """
    
    @staticmethod
    def build_condition(
        tags: list[str],
        tag_type: str = "frontmatter",
        fuzzy: bool = False,
        all_tags: list[str] | None = None,
    ) -> FilterCondition:
        """Построение условия фильтрации по тегам.
        
        ВНИМАНИЕ (v4): Для frontmatter тегов используйте FilterBuilder.build_where_clause()
        с db_manager и vault_name для двухэтапного запроса. Этот метод используется только
        для inline тегов.
        
        Args:
            tags: Список тегов для фильтрации
            tag_type: Тип тегов - "frontmatter" (устарело в v4, используйте FilterBuilder) 
                     или "inline" (inline теги #tag)
            fuzzy: Использовать fuzzy matching (поиск по частичному совпадению)
            all_tags: Список всех доступных тегов для fuzzy matching (опционально)
            
        Returns:
            FilterCondition с SQL условием
            
        Deprecated:
            Для frontmatter тегов в v4 используйте FilterBuilder.build_where_clause()
        """
        if not tags:
            return FilterCondition("")
        
        normalized_tags = DataNormalizer.normalize_tags(tags)
        if not normalized_tags:
            return FilterCondition("")
        
        # Если включен fuzzy matching и есть список всех тегов
        if fuzzy and all_tags:
            # Находим совпадения для каждого частичного тега
            matched_tags = set()
            for partial_tag in normalized_tags:
                matches = FuzzyMatcher.fuzzy_match_tag(
                    partial_tag, all_tags, algorithm="substring", max_results=20
                )
                matched_tags.update(matches)
            
            if not matched_tags:
                # Если ничего не найдено, возвращаем пустое условие
                return FilterCondition("")
            
            # Используем найденные точные совпадения
            normalized_tags = list(matched_tags)
        
        # Выбираем поле в зависимости от типа тегов
        if tag_type == "inline":
            field_name = "inline_tags"
        else:
            field_name = "frontmatter_tags"
        
        conditions = []
        for tag in normalized_tags:
            safe_tag = DataNormalizer.escape_sql_string(tag)
            conditions.append(f"array_contains({field_name}, '{safe_tag}')")
        
        sql = f"({' AND '.join(conditions)})" if len(conditions) > 1 else conditions[0]
        return FilterCondition(sql)


class LinkFilter:
    """Фильтр по wikilinks."""
    
    @staticmethod
    def build_condition(
        links: list[str],
        fuzzy: bool = False,
        all_links: list[str] | None = None,
    ) -> FilterCondition:
        """Построение условия фильтрации по ссылкам.
        
        Args:
            links: Список ссылок для фильтрации
            fuzzy: Использовать fuzzy matching (поиск по частичному совпадению)
            all_links: Список всех доступных ссылок для fuzzy matching (опционально)
            
        Returns:
            FilterCondition с SQL условием
        """
        if not links:
            return FilterCondition("")
        
        normalized_links = DataNormalizer.normalize_links(links)
        if not normalized_links:
            return FilterCondition("")
        
        # Если включен fuzzy matching и есть список всех ссылок
        if fuzzy and all_links:
            # Находим совпадения для каждой частичной ссылки
            matched_links = set()
            for partial_link in normalized_links:
                matches = FuzzyMatcher.fuzzy_match_link(
                    partial_link, all_links, algorithm="substring", max_results=20
                )
                matched_links.update(matches)
            
            if not matched_links:
                # Если ничего не найдено, возвращаем пустое условие
                return FilterCondition("")
            
            # Используем найденные точные совпадения
            normalized_links = list(matched_links)
        
        conditions = []
        for link in normalized_links:
            safe_link = DataNormalizer.escape_sql_string(link)
            conditions.append(f"array_contains(links, '{safe_link}')")
        
        sql = f"({' AND '.join(conditions)})" if len(conditions) > 1 else conditions[0]
        return FilterCondition(sql)


class DocTypeFilter:
    """Фильтр по типу документа (v4).
    
    В v4 использует двухэтапный запрос через таблицу properties для быстрой фильтрации.
    """
    
    @staticmethod
    async def build_condition(
        doc_type: str,
        db_manager: "IDatabaseManager | None" = None,
        vault_name: str | None = None,
    ) -> tuple[set[str], FilterCondition]:
        """Построение условия фильтрации по типу документа (v4).
        
        В v4 использует двухэтапный запрос:
        1. Поиск document_id в таблице properties
        2. Фильтрация чанков по document_id
        
        Args:
            doc_type: Тип документа для фильтрации
            db_manager: Менеджер БД для двухэтапного запроса (опционально)
            vault_name: Имя vault'а для двухэтапного запроса (опционально)
        
        Returns:
            Кортеж (document_ids, FilterCondition):
            - document_ids: Множество document_id для фильтрации (если используется двухэтапный запрос)
            - FilterCondition: Пустое условие для chunks (фильтрация уже выполнена через document_ids)
            
        Note:
            Если db_manager и vault_name не предоставлены, возвращает пустые document_ids
            и FilterCondition для fallback на одноэтапный запрос через metadata.
        """
        if not doc_type:
            return set(), FilterCondition("")
        
        normalized_type = DataNormalizer.normalize_doc_type(doc_type)
        if not normalized_type:
            return set(), FilterCondition("")
        
        safe_type = DataNormalizer.escape_sql_string(normalized_type)
        
        # Двухэтапный запрос (предпочтительно в v4)
        if db_manager and vault_name:
            try:
                document_ids = await db_manager.get_documents_by_property(
                    vault_name=vault_name,
                    property_key="type",
                    property_value=safe_type,
                )
                # Возвращаем document_ids для фильтрации в chunks
                return document_ids, FilterCondition("")
            except Exception as e:
                logger.warning(f"Failed to get documents by property for type '{doc_type}': {e}, falling back to metadata")
                # Fallback на одноэтапный запрос через metadata
                sql = f"metadata_json LIKE '%\"type\":\"{safe_type}\"%'"
                return set(), FilterCondition(sql)
        
        # Fallback на одноэтапный запрос через metadata (для обратной совместимости)
        sql = f"metadata_json LIKE '%\"type\":\"{safe_type}\"%'"
        return set(), FilterCondition(sql)


class DateFilter:
    """Фильтр по датам."""
    
    @staticmethod
    def build_condition(
        field: str,
        operator: str,
        value: str | datetime,
        exclude_null: bool = False,
    ) -> FilterCondition:
        """Построение условия фильтрации по дате.
        
        Args:
            field: Поле (created или modified)
            operator: Оператор (>, <, >=, <=, =)
            value: Значение даты в ISO формате или datetime объект, или относительная дата (например, "last_week")
            exclude_null: Исключать NULL значения
            
        Returns:
            FilterCondition с SQL условием
        """
        sql_op = operator if operator in (">", "<", ">=", "<=", "=") else "="
        field_name = f"{field}_at"
        
        # Если value - строка, проверяем, является ли она относительной датой
        if isinstance(value, str):
            if RelativeDateParser.is_relative_date(value):
                # Парсим относительную дату
                parsed_date = RelativeDateParser.parse_relative_date(value)
                if parsed_date is None:
                    # Не удалось распарсить, возвращаем пустое условие
                    return FilterCondition("")
                value = parsed_date.isoformat()
            else:
                # Пытаемся распарсить как ISO дату
                try:
                    # Если это уже ISO формат, оставляем как есть
                    datetime.fromisoformat(value.replace(' ', 'T'))
                    # value уже в правильном формате
                except (ValueError, AttributeError):
                    # Не удалось распарсить, возвращаем пустое условие
                    logger.warning(f"Could not parse date value: {value}")
                    return FilterCondition("")
        elif isinstance(value, datetime):
            # Если это datetime объект, конвертируем в ISO формат
            value = value.isoformat()
        
        # Экранируем значение для защиты от SQL injection
        # ISO формат дат обычно безопасен, но экранирование не помешает
        safe_value = DataNormalizer.escape_sql_string(str(value))
        
        if exclude_null:
            sql = f"({field_name} IS NOT NULL AND {field_name} {sql_op} '{safe_value}')"
        else:
            sql = f"{field_name} {sql_op} '{safe_value}'"
        
        return FilterCondition(sql)


class FilterBuilder:
    """Построитель комбинированных фильтров (v4).
    
    В v4 поддерживает двухэтапные запросы для фильтров по свойствам документов.
    """
    
    @staticmethod
    async def build_where_clause(
        tags: list[str] | None = None,
        tags_or: list[str] | None = None,
        tags_not: list[str] | None = None,
        inline_tags: list[str] | None = None,
        inline_tags_or: list[str] | None = None,
        inline_tags_not: list[str] | None = None,
        links: list[str] | None = None,
        links_or: list[str] | None = None,
        links_not: list[str] | None = None,
        doc_type: str | None = None,
        doc_type_or: list[str] | None = None,
        doc_type_not: str | None = None,
        date_filters: dict[str, dict[str, Any]] | None = None,
        fuzzy: bool = False,
        all_links: list[str] | None = None,
        all_tags: list[str] | None = None,
        all_inline_tags: list[str] | None = None,
        db_manager: "IDatabaseManager | None" = None,
        vault_name: str | None = None,
    ) -> tuple[str | None, set[str] | None]:
        """Построение полного WHERE условия из всех фильтров (v4).
        
        В v4 поддерживает двухэтапные запросы для фильтров по свойствам.
        
        Args:
            tags: Список тегов из frontmatter (AND)
            tags_or: Список тегов из frontmatter (OR)
            tags_not: Список тегов из frontmatter (NOT)
            inline_tags: Список inline тегов (AND)
            inline_tags_or: Список inline тегов (OR)
            inline_tags_not: Список inline тегов (NOT)
            links: Список ссылок (AND)
            links_or: Список ссылок (OR)
            links_not: Список ссылок (NOT)
            doc_type: Тип документа (AND) - использует двухэтапный запрос в v4
            doc_type_or: Список типов документов (OR) - использует двухэтапный запрос в v4
            doc_type_not: Тип документа (NOT) - использует двухэтапный запрос в v4
            date_filters: Фильтры по датам
            fuzzy: Использовать fuzzy matching для links и tags
            all_links: Список всех ссылок для fuzzy matching (опционально)
            all_tags: Список всех frontmatter тегов для fuzzy matching (опционально)
            all_inline_tags: Список всех inline тегов для fuzzy matching (опционально)
            db_manager: Менеджер БД для двухэтапных запросов (опционально)
            vault_name: Имя vault'а для двухэтапных запросов (опционально)
        
        Returns:
            Кортеж (where_clause, document_ids):
            - where_clause: SQL условие для фильтрации чанков
            - document_ids: Множество document_id для фильтрации (если используется двухэтапный запрос)
        """
        conditions: list[str] = []
        document_ids: set[str] | None = None
        
        # Теги из frontmatter (AND) - двухэтапный запрос в v4
        # В v4 frontmatter_tags хранятся в таблице metadata, а не в chunks
        # Требуется db_manager и vault_name для двухэтапного запроса
        if tags:
            if db_manager and vault_name:
                # Используем двухэтапный запрос через таблицу metadata
                tag_doc_ids = await db_manager.get_documents_by_tags(
                    vault_name=vault_name,
                    tags=tags,
                    match_all=True,  # AND логика
                )
                if document_ids is None:
                    document_ids = tag_doc_ids
                else:
                    # Пересечение множеств (AND)
                    document_ids = document_ids & tag_doc_ids
            else:
                # Без db_manager и vault_name фильтрация по frontmatter тегам невозможна
                # В v4 frontmatter_tags не хранятся в таблице chunks
                logger.warning(
                    "Filtering by frontmatter tags requires db_manager and vault_name. "
                    "Skipping frontmatter tags filter."
                )
        
        # Теги из frontmatter (OR) - двухэтапный запрос в v4
        if tags_or:
            if db_manager and vault_name:
                # Используем двухэтапный запрос через таблицу metadata
                tag_or_doc_ids = await db_manager.get_documents_by_tags(
                    vault_name=vault_name,
                    tags=tags_or,
                    match_all=False,  # OR логика
                )
                if document_ids is None:
                    document_ids = tag_or_doc_ids
                else:
                    # Объединение множеств (OR)
                    document_ids = document_ids | tag_or_doc_ids
            else:
                logger.warning(
                    "Filtering by frontmatter tags (OR) requires db_manager and vault_name. "
                    "Skipping frontmatter tags (OR) filter."
                )
        
        # Теги из frontmatter (NOT) - двухэтапный запрос в v4
        # Для NOT требуется получить все документы и исключить те, что содержат теги
        # Пока не реализовано, пропускаем фильтр с предупреждением
        if tags_not:
            if db_manager and vault_name:
                # TODO: Реализовать двухэтапный запрос для NOT
                # Требует получения всех document_ids и исключения тех, что содержат теги
                logger.warning(
                    "Filtering by frontmatter tags (NOT) is not yet implemented for two-stage queries. "
                    "Skipping frontmatter tags (NOT) filter."
                )
            else:
                logger.warning(
                    "Filtering by frontmatter tags (NOT) requires db_manager and vault_name. "
                    "Skipping frontmatter tags (NOT) filter."
                )
        
        # Inline теги (AND)
        if inline_tags:
            inline_tag_filter = TagFilter.build_condition(
                inline_tags, tag_type="inline", fuzzy=fuzzy, all_tags=all_inline_tags
            )
            if inline_tag_filter.sql:
                conditions.append(inline_tag_filter.sql)
        
        # Inline теги (OR)
        if inline_tags_or:
            inline_tag_or_conditions = []
            for tag in inline_tags_or:
                safe_tag = DataNormalizer.escape_sql_string(DataNormalizer.normalize_tag(tag))
                inline_tag_or_conditions.append(f"array_contains(inline_tags, '{safe_tag}')")
            if inline_tag_or_conditions:
                if inline_tags:
                    or_condition = f"({' OR '.join(inline_tag_or_conditions)})"
                    conditions[-1] = f"({conditions[-1]} OR {or_condition})"
                else:
                    conditions.append(f"({' OR '.join(inline_tag_or_conditions)})")
        
        # Inline теги (NOT)
        if inline_tags_not:
            inline_tag_not_conditions = []
            for tag in inline_tags_not:
                safe_tag = DataNormalizer.escape_sql_string(DataNormalizer.normalize_tag(tag))
                inline_tag_not_conditions.append(f"NOT array_contains(inline_tags, '{safe_tag}')")
            if inline_tag_not_conditions:
                conditions.append(f"({' AND '.join(inline_tag_not_conditions)})")
        
        # Ссылки (AND)
        if links:
            link_filter = LinkFilter.build_condition(links, fuzzy=fuzzy, all_links=all_links)
            if link_filter.sql:
                conditions.append(link_filter.sql)
        
        # Ссылки (OR)
        if links_or:
            link_or_conditions = []
            for link in links_or:
                safe_link = DataNormalizer.escape_sql_string(DataNormalizer.normalize_link(link))
                link_or_conditions.append(f"array_contains(links, '{safe_link}')")
            if link_or_conditions:
                if links:
                    or_condition = f"({' OR '.join(link_or_conditions)})"
                    conditions[-1] = f"({conditions[-1]} OR {or_condition})"
                else:
                    conditions.append(f"({' OR '.join(link_or_conditions)})")
        
        # Ссылки (NOT)
        if links_not:
            link_not_conditions = []
            for link in links_not:
                safe_link = DataNormalizer.escape_sql_string(DataNormalizer.normalize_link(link))
                link_not_conditions.append(f"NOT array_contains(links, '{safe_link}')")
            if link_not_conditions:
                conditions.append(f"({' AND '.join(link_not_conditions)})")
        
        # Тип документа (AND) - двухэтапный запрос в v4
        if doc_type:
            if db_manager and vault_name:
                # Двухэтапный запрос через properties
                doc_ids, type_filter = await DocTypeFilter.build_condition(
                    doc_type, db_manager, vault_name
                )
                if doc_ids:
                    if document_ids is None:
                        document_ids = doc_ids
                    else:
                        document_ids &= doc_ids  # Пересечение
                elif type_filter.sql:
                    # Fallback на одноэтапный запрос через metadata
                    conditions.append(type_filter.sql)
            else:
                # Fallback на одноэтапный запрос через metadata
                _, type_filter = await DocTypeFilter.build_condition(doc_type)
                if type_filter.sql:
                    conditions.append(type_filter.sql)
        
        # Тип документа (OR) - двухэтапный запрос в v4
        if doc_type_or:
            if db_manager and vault_name:
                # Двухэтапный запрос для каждого типа
                or_doc_ids: set[str] = set()
                for doc_t in doc_type_or:
                    doc_ids, _ = await DocTypeFilter.build_condition(doc_t, db_manager, vault_name)
                    or_doc_ids |= doc_ids
                
                if or_doc_ids:
                    if document_ids is None:
                        document_ids = or_doc_ids
                    else:
                        # Объединяем через OR (объединение множеств)
                        document_ids |= or_doc_ids
            else:
                # Fallback на одноэтапный запрос через metadata
                type_or_conditions = []
                for doc_t in doc_type_or:
                    _, type_filter = await DocTypeFilter.build_condition(doc_t)
                    if type_filter.sql:
                        type_or_conditions.append(type_filter.sql)
                if type_or_conditions:
                    if doc_type and conditions:
                        or_condition = f"({' OR '.join(type_or_conditions)})"
                        conditions[-1] = f"({conditions[-1]} OR {or_condition})"
                    else:
                        conditions.append(f"({' OR '.join(type_or_conditions)})")
        
        # Тип документа (NOT) - двухэтапный запрос в v4
        if doc_type_not:
            if db_manager and vault_name:
                # Двухэтапный запрос: получаем документы с типом, затем исключаем их
                not_doc_ids, _ = await DocTypeFilter.build_condition(
                    doc_type_not, db_manager, vault_name
                )
                if document_ids is not None:
                    # Исключаем документы с типом doc_type_not
                    document_ids -= not_doc_ids
                else:
                    # Получаем все документы и исключаем not_doc_ids
                    # Для этого нужно получить все document_ids из documents таблицы
                    # Пока используем fallback на metadata
                    safe_type = DataNormalizer.escape_sql_string(DataNormalizer.normalize_doc_type(doc_type_not))
                    conditions.append(f"metadata_json NOT LIKE '%\"type\":\"{safe_type}\"%'")
            else:
                # Fallback на одноэтапный запрос через metadata
                safe_type = DataNormalizer.escape_sql_string(DataNormalizer.normalize_doc_type(doc_type_not))
                conditions.append(f"metadata_json NOT LIKE '%\"type\":\"{safe_type}\"%'")
        
        # Даты - НЕ добавляем в WHERE clause для chunks!
        # Фильтры дат применяются только через двухэтапный запрос в BaseSearchStrategy._apply_filters()
        # Даты хранятся в таблице documents, а не в chunks, поэтому фильтр в WHERE clause не работает
        # См. ROUND_3_ISSUES_ANALYSIS.md для деталей
        
        where_clause = " AND ".join(conditions) if conditions else None
        return where_clause, document_ids

