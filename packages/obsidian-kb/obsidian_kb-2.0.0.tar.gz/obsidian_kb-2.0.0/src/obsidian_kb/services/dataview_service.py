"""DataviewService для SQL-подобных запросов по frontmatter.

Предоставляет Dataview-подобный синтаксис для запросов по метаданным документов.
"""

import asyncio
import logging
import re
import time
from typing import Any

from obsidian_kb.interfaces import (
    DataviewQuery,
    DataviewResult,
    IDataviewService,
)
from obsidian_kb.query.where_parser import WhereParser
from obsidian_kb.service_container import get_service_container

logger = logging.getLogger(__name__)


class DataviewService(IDataviewService):
    """SQL-подобные запросы по frontmatter."""
    
    def __init__(self) -> None:
        """Инициализация DataviewService."""
        self._services = get_service_container()
    
    async def query(
        self,
        vault_name: str,
        query: DataviewQuery,
    ) -> DataviewResult:
        """Выполнить структурированный запрос."""
        start_time = time.time()
        
        db_manager = self._services.db_manager
        
        try:
            # Получаем таблицы
            documents_table = await db_manager._ensure_table(vault_name, "documents")
            properties_table = await db_manager._ensure_table(vault_name, "document_properties")
            
            def _execute_query() -> list[dict[str, Any]]:
                def _filter_by_type(all_docs: list, all_props: list, from_type: str) -> tuple[list, list]:
                    """Фильтрует документы и свойства по типу в Python."""
                    props_by_doc_temp: dict[str, dict[str, Any]] = {}
                    for prop in all_props:
                        d_id = prop["document_id"]
                        if d_id not in props_by_doc_temp:
                            props_by_doc_temp[d_id] = {}
                        props_by_doc_temp[d_id][prop["property_key"]] = prop.get("property_value")
                    doc_ids_with_type = {d_id for d_id, props in props_by_doc_temp.items()
                                        if props.get("type") == from_type}
                    return (
                        [d for d in all_docs if d["document_id"] in doc_ids_with_type],
                        [p for p in all_props if p["document_id"] in doc_ids_with_type]
                    )

                # Шаг 1 и 2: Получаем документы и свойства
                # Оптимизация: если указан from_type, пробуем фильтровать на уровне БД
                if query.from_type:
                    try:
                        # Сначала получаем document_ids с нужным типом
                        from_type_escaped = query.from_type.replace("'", "''")
                        type_where = f"property_key = 'type' AND property_value = '{from_type_escaped}'"
                        type_docs = properties_table.search().where(type_where).to_arrow().to_pylist()

                        # Проверяем, что результат — это список, а не MagicMock
                        if not isinstance(type_docs, list):
                            raise TypeError("Expected list, got mock")

                        doc_ids_with_type = {d["document_id"] for d in type_docs}

                        if not doc_ids_with_type:
                            all_docs = []
                            all_props = []
                        else:
                            # Получаем только нужные документы
                            doc_ids_list = list(doc_ids_with_type)
                            if len(doc_ids_list) <= 100:
                                placeholders = ", ".join([f"'{d.replace(chr(39), chr(39)+chr(39))}'" for d in doc_ids_list])
                                doc_where = f"document_id IN ({placeholders})"
                                all_docs = documents_table.search().where(doc_where).to_arrow().to_pylist()
                                all_props = properties_table.search().where(doc_where).to_arrow().to_pylist()
                            else:
                                all_docs = [d for d in documents_table.to_arrow().to_pylist()
                                           if d["document_id"] in doc_ids_with_type]
                                all_props = [p for p in properties_table.to_arrow().to_pylist()
                                            if p["document_id"] in doc_ids_with_type]
                    except (AttributeError, TypeError):
                        # Fallback для тестов с моками без .search()
                        all_docs = documents_table.to_arrow().to_pylist()
                        all_props = properties_table.to_arrow().to_pylist()
                        all_docs, all_props = _filter_by_type(all_docs, all_props, query.from_type)
                else:
                    # Без фильтра по типу — загружаем всё
                    all_docs = documents_table.to_arrow().to_pylist()
                    all_props = properties_table.to_arrow().to_pylist()

                props_by_doc: dict[str, dict[str, Any]] = {}

                for prop in all_props:
                    doc_id = prop["document_id"]
                    if doc_id not in props_by_doc:
                        props_by_doc[doc_id] = {}
                    props_by_doc[doc_id][prop["property_key"]] = prop.get("property_value")

                # Шаг 3: Объединяем документы с их свойствами
                enriched_docs = []
                for doc in all_docs:
                    doc_id = doc["document_id"]
                    enriched = {**doc}

                    if doc_id in props_by_doc:
                        enriched.update(props_by_doc[doc_id])

                    enriched_docs.append(enriched)

                # Шаг 4: Фильтрация по FROM (type уже сделан на уровне БД, path - в Python)
                if query.from_path:
                    enriched_docs = [
                        d for d in enriched_docs
                        if d.get("file_path", "").startswith(query.from_path)
                    ]
                
                # Шаг 5: Применяем WHERE условия
                if query.where:
                    enriched_docs = [
                        d for d in enriched_docs
                        if WhereParser.evaluate(query.where, d)
                    ]
                
                # Шаг 6: Сортировка
                if query.sort_by:
                    reverse = query.sort_order.lower() == "desc"
                    enriched_docs.sort(
                        key=lambda d: d.get(query.sort_by) or "",
                        reverse=reverse
                    )
                
                # Шаг 7: Лимит
                enriched_docs = enriched_docs[:query.limit]
                
                # Шаг 8: Выбираем только нужные поля
                if query.select != ["*"]:
                    enriched_docs = [
                        {k: d.get(k) for k in query.select if k in d}
                        for d in enriched_docs
                    ]
                
                return enriched_docs
            
            documents = await asyncio.to_thread(_execute_query)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return DataviewResult(
                documents=documents,
                total_count=len(documents),
                query_time_ms=elapsed_ms,
                query_string=self._query_to_string(query)
            )
        
        except Exception as e:
            logger.error(f"Dataview query error: {e}", exc_info=True)
            return DataviewResult(
                documents=[],
                total_count=0,
                query_time_ms=0,
                query_string=self._query_to_string(query)
            )
    
    async def query_string(
        self,
        vault_name: str,
        query_string: str,
    ) -> DataviewResult:
        """Выполнить запрос из SQL-like строки."""
        query = self.parse_query(query_string)
        return await self.query(vault_name, query)
    
    def parse_query(self, query_string: str) -> DataviewQuery:
        """
        Парсинг SQL-like строки запроса.
        
        Поддерживаемый синтаксис:
            SELECT field1, field2 FROM type:X WHERE condition SORT BY field DESC LIMIT N
        
        Все части опциональны.
        """
        query_string = query_string.strip()
        
        # Значения по умолчанию
        select = ["*"]
        from_type = None
        from_path = None
        where = None
        sort_by = None
        sort_order = "desc"
        limit = 50
        
        # Парсим SELECT
        select_match = re.search(
            r'SELECT\s+(.+?)(?=\s+FROM|\s+WHERE|\s+SORT|\s+LIMIT|$)',
            query_string,
            re.IGNORECASE
        )
        if select_match:
            select_str = select_match.group(1).strip()
            if select_str != "*":
                select = [s.strip() for s in select_str.split(",")]
        
        # Парсим FROM
        from_match = re.search(
            r'FROM\s+(?:type:(\S+)|path:(\S+))',
            query_string,
            re.IGNORECASE
        )
        if from_match:
            from_type = from_match.group(1)
            from_path = from_match.group(2)
        
        # Парсим WHERE
        where_match = re.search(
            r'WHERE\s+(.+?)(?=\s+SORT|\s+LIMIT|$)',
            query_string,
            re.IGNORECASE
        )
        if where_match:
            where_str = where_match.group(1).strip()
            where = WhereParser.parse(where_str)
        
        # Парсим SORT BY
        sort_match = re.search(
            r'SORT\s+BY\s+(\w+)(?:\s+(ASC|DESC))?',
            query_string,
            re.IGNORECASE
        )
        if sort_match:
            sort_by = sort_match.group(1)
            if sort_match.group(2):
                sort_order = sort_match.group(2).lower()
        
        # Парсим LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', query_string, re.IGNORECASE)
        if limit_match:
            limit = int(limit_match.group(1))
        
        return DataviewQuery(
            select=select,
            from_type=from_type,
            from_path=from_path,
            where=where,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit
        )
    
    def _query_to_string(self, query: DataviewQuery) -> str:
        """Преобразование DataviewQuery обратно в строку."""
        parts = []
        
        parts.append(f"SELECT {', '.join(query.select)}")
        
        if query.from_type:
            parts.append(f"FROM type:{query.from_type}")
        elif query.from_path:
            parts.append(f"FROM path:{query.from_path}")
        
        if query.where:
            conditions = []
            for cond in query.where:
                if cond.value is not None:
                    conditions.append(f"{cond.field} {cond.operator} \"{cond.value}\"")
                else:
                    conditions.append(f"{cond.field} {cond.operator}")
            parts.append(f"WHERE {' AND '.join(conditions)}")
        
        if query.sort_by:
            parts.append(f"SORT BY {query.sort_by} {query.sort_order.upper()}")
        
        parts.append(f"LIMIT {query.limit}")
        
        return " ".join(parts)

