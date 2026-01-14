# Extended Query API для obsidian-kb

**Версия документа:** 1.0.0  
**Дата:** 2025-01-02  
**Автор:** Claude + Max Demyanov  
**Статус:** Draft / RFC

---

## Содержание

1. [Мотивация и цели](#1-мотивация-и-цели)
2. [Обзор архитектуры](#2-обзор-архитектуры)
3. [Компонент 1: FrontmatterAPI](#3-компонент-1-frontmatterapi)
4. [Компонент 2: DataviewService](#4-компонент-2-dataviewservice)
5. [Компонент 3: RipgrepService](#5-компонент-3-ripgrepservice)
6. [Компонент 4: GraphQueryService](#6-компонент-4-graphqueryservice)
7. [Компонент 5: TimelineService](#7-компонент-5-timelineservice)
8. [Компонент 6: BatchOperations](#8-компонент-6-batchoperations)
9. [MCP Tools Reference](#9-mcp-tools-reference)
10. [Интеграция с существующей архитектурой](#10-интеграция-с-существующей-архитектурой)
11. [План реализации](#11-план-реализации)
12. [Миграция и обратная совместимость](#12-миграция-и-обратная-совместимость)
13. [Тестирование](#13-тестирование)
14. [Открытые вопросы](#14-открытые-вопросы)

---

## 1. Мотивация и цели

### 1.1 Проблема

Текущая версия obsidian-kb (v5) предоставляет мощные возможности семантического и полнотекстового поиска, но имеет ограничения для структурированных запросов:

| Текущая возможность | Ограничение |
|---------------------|-------------|
| Семантический поиск | Не подходит для точных metadata-запросов |
| Фильтры `type:`, `tags:` | Фиксированный набор, нет кастомных свойств |
| `document_properties` таблица | Есть в БД, но нет удобного API |
| Поиск по тексту | Только через индекс, нет прямого grep |

### 1.2 User Stories

**US-1: Dataview-подобные запросы**
> Как CTO, я хочу получить список всех 1-1 встреч с конкретным человеком, где status != "done", отсортированных по дате, чтобы подготовиться к следующей встрече.

```
dataview_query("naumen-cto", from_type="1-1", where="status != done", sort_by="date")
```

**US-2: Агрегация по свойствам**
> Как менеджер базы знаний, я хочу видеть распределение документов по статусам, чтобы понимать сколько задач в работе.

```
aggregate_by_property("vault", "status")
→ {"done": 80, "in-progress": 15, "pending": 5}
```

**US-3: Прямой текстовый поиск**
> Как разработчик, я хочу найти все TODO комментарии в vault'е, даже если они не проиндексированы.

```
search_text("vault", "TODO:", case_sensitive=True)
```

**US-4: Поиск по связям**
> Как аналитик, я хочу найти все документы, которые ссылаются на конкретного человека, чтобы понять его involvement.

```
find_connected("vault", "People/Иван Иванов.md", direction="incoming")
```

**US-5: Схема данных**
> Как новый пользователь vault'а, я хочу понять какие поля используются в frontmatter, чтобы правильно создавать документы.

```
get_vault_schema("vault", doc_type="person")
```

### 1.3 Цели проекта

1. **Структурированные запросы** — SQL-подобный синтаксис для frontmatter
2. **Полный доступ к метаданным** — любые frontmatter поля, не только фиксированные
3. **Прямой текстовый поиск** — ripgrep/grep без индекса
4. **Граф-запросы** — поиск по связям между документами
5. **Хронология** — timeline-запросы по датам
6. **Агрегации** — статистика и группировки

### 1.4 Non-Goals (Вне скоупа)

- Модификация файлов (write operations) — только read-only
- Real-time синхронизация с файловой системой
- Полная совместимость с Dataview syntax
- GUI для построения запросов

---

## 2. Обзор архитектуры

### 2.1 Высокоуровневая диаграмма

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MCP Server                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Extended Query Tools                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │dataview_ │ │search_   │ │get_vault_│ │find_     │  ...      │   │
│  │  │query     │ │text      │ │schema    │ │connected │           │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │   │
│  └───────┼────────────┼────────────┼────────────┼──────────────────┘   │
│          │            │            │            │                       │
└──────────┼────────────┼────────────┼────────────┼───────────────────────┘
           │            │            │            │
           ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Extended Query Layer (NEW)                            │
│                                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐             │
│  │ DataviewService│  │ RipgrepService │  │ GraphQuery     │             │
│  │                │  │                │  │ Service        │             │
│  │ - query()      │  │ - search_text()│  │ - find_        │             │
│  │ - aggregate()  │  │ - search_regex │  │   connected()  │             │
│  │ - parse_where()│  │ - find_files() │  │ - find_orphans│             │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘             │
│          │                   │                   │                       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐             │
│  │ FrontmatterAPI │  │ TimelineService│  │ BatchOperations│             │
│  │                │  │                │  │                │             │
│  │ - get_schema() │  │ - timeline()   │  │ - export_csv() │             │
│  │ - list_by_prop │  │ - recent_      │  │ - compare_     │             │
│  │ - aggregate()  │  │   changes()    │  │   schemas()    │             │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘             │
│          │                   │                   │                       │
│          └───────────────────┼───────────────────┘                       │
│                              │                                           │
└──────────────────────────────┼───────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Existing v5 Architecture                              │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Search Layer                                │   │
│  │  SearchService │ IntentDetector │ Strategies                     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Storage Layer                               │   │
│  │  ChunkRepository │ DocumentRepository │ LanceDBManager           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    LanceDB Tables (v4 Schema)                    │   │
│  │  documents │ chunks │ document_properties │ metadata             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Принципы проектирования

1. **Минимальные изменения существующего кода** — новые сервисы используют существующие репозитории
2. **Lazy loading** — сервисы создаются через ServiceContainer по требованию
3. **Read-only операции** — никаких записей в файлы vault'а
4. **Graceful degradation** — ripgrep fallback на grep, schema fallback на пустую
5. **Consistent API** — единообразные параметры и форматы ответов

### 2.3 Файловая структура

```
src/obsidian_kb/
├── services/                      # NEW: Extended Query Services
│   ├── __init__.py
│   ├── frontmatter_api.py        # FrontmatterAPI
│   ├── dataview_service.py       # DataviewService
│   ├── ripgrep_service.py        # RipgrepService
│   ├── graph_query_service.py    # GraphQueryService
│   ├── timeline_service.py       # TimelineService
│   └── batch_operations.py       # BatchOperations
│
├── query/                         # NEW: Query parsing utilities
│   ├── __init__.py
│   ├── where_parser.py           # WHERE clause parser
│   ├── select_parser.py          # SELECT fields parser
│   └── dataview_syntax.py        # Dataview-like syntax support
│
├── storage/                       # Existing
│   ├── chunk_repository.py
│   └── document_repository.py    # + new methods
│
├── mcp_server.py                  # + new tools
├── service_container.py           # + new services
└── interfaces.py                  # + new interfaces
```

---

## 3. Компонент 1: FrontmatterAPI

### 3.1 Обзор

FrontmatterAPI предоставляет прямой доступ к frontmatter метаданным документов, включая схему данных vault'а и агрегации.

### 3.2 Интерфейс

```python
# src/obsidian_kb/interfaces.py

from typing import Protocol
from dataclasses import dataclass


@dataclass
class FieldInfo:
    """Информация о поле frontmatter."""
    field_name: str
    field_type: str  # "string" | "list" | "date" | "number" | "boolean"
    unique_values: list[str]  # Топ-N уникальных значений
    unique_count: int  # Общее количество уникальных значений
    document_count: int  # Сколько документов имеют это поле
    nullable_count: int  # Сколько документов имеют пустое значение
    example_documents: list[str]  # Примеры документов с этим полем


@dataclass
class FrontmatterSchema:
    """Схема frontmatter vault'а."""
    vault_name: str
    total_documents: int
    doc_type_filter: str | None  # Если схема для конкретного типа
    fields: dict[str, FieldInfo]
    common_patterns: list[str]  # Часто встречающиеся комбинации полей


@dataclass
class PropertyAggregation:
    """Результат агрегации по свойству."""
    property_key: str
    total_documents: int  # Всего документов с этим свойством
    values: dict[str, int]  # Значение → количество
    null_count: int  # Документы без значения


class IFrontmatterAPI(Protocol):
    """Интерфейс для работы с frontmatter метаданными."""
    
    async def get_frontmatter(
        self,
        vault_name: str,
        file_path: str
    ) -> dict | None:
        """Получить frontmatter конкретного файла."""
        ...
    
    async def get_schema(
        self,
        vault_name: str,
        doc_type: str | None = None,
        top_values: int = 20
    ) -> FrontmatterSchema:
        """Получить схему frontmatter vault'а."""
        ...
    
    async def list_by_property(
        self,
        vault_name: str,
        property_key: str,
        property_value: str | None = None,
        limit: int = 50
    ) -> list[dict]:
        """Получить документы по значению свойства."""
        ...
    
    async def aggregate_by_property(
        self,
        vault_name: str,
        property_key: str,
        doc_type: str | None = None
    ) -> PropertyAggregation:
        """Агрегация по свойству."""
        ...
    
    async def get_property_values(
        self,
        vault_name: str,
        property_key: str,
        limit: int = 100
    ) -> list[tuple[str, int]]:
        """Получить уникальные значения свойства с количеством."""
        ...
```

### 3.3 Реализация

```python
# src/obsidian_kb/services/frontmatter_api.py

import asyncio
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from obsidian_kb.interfaces import (
    FieldInfo,
    FrontmatterSchema,
    IFrontmatterAPI,
    PropertyAggregation,
)
from obsidian_kb.service_container import get_service_container

logger = logging.getLogger(__name__)


class FrontmatterAPI(IFrontmatterAPI):
    """Реализация API для работы с frontmatter."""
    
    def __init__(self):
        self._services = get_service_container()
    
    async def get_frontmatter(
        self,
        vault_name: str,
        file_path: str
    ) -> dict | None:
        """Получить frontmatter конкретного файла."""
        # Используем таблицу metadata для получения полного frontmatter
        db_manager = self._services.db_manager
        
        try:
            metadata_table = await db_manager._ensure_table(vault_name, "metadata")
            
            def _get_metadata() -> dict | None:
                import json
                result = metadata_table.search().where(
                    f"file_path = '{file_path}'"
                ).limit(1).to_list()
                
                if result:
                    metadata_json = result[0].get("metadata_json")
                    if metadata_json:
                        return json.loads(metadata_json)
                return None
            
            return await asyncio.to_thread(_get_metadata)
        
        except Exception as e:
            logger.error(f"Error getting frontmatter for {file_path}: {e}")
            return None
    
    async def get_schema(
        self,
        vault_name: str,
        doc_type: str | None = None,
        top_values: int = 20
    ) -> FrontmatterSchema:
        """
        Получить схему frontmatter vault'а.
        
        Анализирует все документы (или документы определённого типа)
        и возвращает информацию о всех используемых полях.
        """
        db_manager = self._services.db_manager
        
        try:
            properties_table = await db_manager._ensure_table(vault_name, "document_properties")
            documents_table = await db_manager._ensure_table(vault_name, "documents")
            
            def _analyze_schema() -> FrontmatterSchema:
                import json
                
                # Получаем все документы
                if doc_type:
                    # Сначала находим document_ids для типа
                    type_results = properties_table.search().where(
                        f"property_key = 'type' AND property_value = '{doc_type}'"
                    ).to_list()
                    doc_ids = {r["document_id"] for r in type_results}
                    
                    # Затем получаем свойства только этих документов
                    all_properties = properties_table.to_arrow().to_pylist()
                    all_properties = [p for p in all_properties if p["document_id"] in doc_ids]
                else:
                    all_properties = properties_table.to_arrow().to_pylist()
                    doc_ids = {p["document_id"] for p in all_properties}
                
                # Группируем по полям
                field_data: dict[str, list[Any]] = {}
                field_docs: dict[str, set[str]] = {}
                
                for prop in all_properties:
                    key = prop["property_key"]
                    value = prop.get("property_value") or prop.get("property_value_raw")
                    doc_id = prop["document_id"]
                    
                    if key not in field_data:
                        field_data[key] = []
                        field_docs[key] = set()
                    
                    field_data[key].append(value)
                    field_docs[key].add(doc_id)
                
                # Анализируем каждое поле
                fields: dict[str, FieldInfo] = {}
                
                for field_name, values in field_data.items():
                    # Определяем тип
                    field_type = _infer_field_type(values)
                    
                    # Считаем уникальные значения
                    value_counts = Counter(v for v in values if v is not None and v != "")
                    top_values_list = [v for v, _ in value_counts.most_common(top_values)]
                    
                    # Считаем nullable
                    nullable_count = sum(1 for v in values if v is None or v == "")
                    
                    fields[field_name] = FieldInfo(
                        field_name=field_name,
                        field_type=field_type,
                        unique_values=top_values_list,
                        unique_count=len(value_counts),
                        document_count=len(field_docs[field_name]),
                        nullable_count=nullable_count,
                        example_documents=list(field_docs[field_name])[:3]
                    )
                
                return FrontmatterSchema(
                    vault_name=vault_name,
                    total_documents=len(doc_ids),
                    doc_type_filter=doc_type,
                    fields=fields,
                    common_patterns=_find_common_patterns(field_docs)
                )
            
            return await asyncio.to_thread(_analyze_schema)
        
        except Exception as e:
            logger.error(f"Error getting schema for {vault_name}: {e}")
            return FrontmatterSchema(
                vault_name=vault_name,
                total_documents=0,
                doc_type_filter=doc_type,
                fields={},
                common_patterns=[]
            )
    
    async def list_by_property(
        self,
        vault_name: str,
        property_key: str,
        property_value: str | None = None,
        limit: int = 50
    ) -> list[dict]:
        """Получить документы по значению свойства."""
        db_manager = self._services.db_manager
        
        try:
            properties_table = await db_manager._ensure_table(vault_name, "document_properties")
            documents_table = await db_manager._ensure_table(vault_name, "documents")
            
            def _list_documents() -> list[dict]:
                # Строим WHERE условие
                if property_value is not None:
                    where = f"property_key = '{property_key}' AND property_value = '{property_value}'"
                else:
                    where = f"property_key = '{property_key}'"
                
                # Находим document_ids
                props = properties_table.search().where(where).limit(limit).to_list()
                doc_ids = list({p["document_id"] for p in props})
                
                if not doc_ids:
                    return []
                
                # Получаем информацию о документах
                results = []
                docs = documents_table.to_arrow().to_pylist()
                doc_map = {d["document_id"]: d for d in docs}
                
                for doc_id in doc_ids[:limit]:
                    if doc_id in doc_map:
                        doc = doc_map[doc_id]
                        results.append({
                            "document_id": doc_id,
                            "file_path": doc.get("file_path"),
                            "title": doc.get("title"),
                            "created_at": doc.get("created_at"),
                            "modified_at": doc.get("modified_at"),
                        })
                
                return results
            
            return await asyncio.to_thread(_list_documents)
        
        except Exception as e:
            logger.error(f"Error listing by property {property_key}: {e}")
            return []
    
    async def aggregate_by_property(
        self,
        vault_name: str,
        property_key: str,
        doc_type: str | None = None
    ) -> PropertyAggregation:
        """Агрегация по свойству."""
        db_manager = self._services.db_manager
        
        try:
            properties_table = await db_manager._ensure_table(vault_name, "document_properties")
            
            def _aggregate() -> PropertyAggregation:
                # Получаем все значения свойства
                props = properties_table.search().where(
                    f"property_key = '{property_key}'"
                ).to_list()
                
                # Если нужна фильтрация по типу
                if doc_type:
                    type_props = properties_table.search().where(
                        f"property_key = 'type' AND property_value = '{doc_type}'"
                    ).to_list()
                    type_doc_ids = {p["document_id"] for p in type_props}
                    props = [p for p in props if p["document_id"] in type_doc_ids]
                
                # Считаем значения
                values_counter = Counter()
                null_count = 0
                
                for prop in props:
                    value = prop.get("property_value")
                    if value is None or value == "":
                        null_count += 1
                    else:
                        values_counter[value] += 1
                
                return PropertyAggregation(
                    property_key=property_key,
                    total_documents=len(props),
                    values=dict(values_counter),
                    null_count=null_count
                )
            
            return await asyncio.to_thread(_aggregate)
        
        except Exception as e:
            logger.error(f"Error aggregating by {property_key}: {e}")
            return PropertyAggregation(
                property_key=property_key,
                total_documents=0,
                values={},
                null_count=0
            )
    
    async def get_property_values(
        self,
        vault_name: str,
        property_key: str,
        limit: int = 100
    ) -> list[tuple[str, int]]:
        """Получить уникальные значения свойства с количеством."""
        aggregation = await self.aggregate_by_property(vault_name, property_key)
        
        # Сортируем по количеству и ограничиваем
        sorted_values = sorted(
            aggregation.values.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_values[:limit]


def _infer_field_type(values: list[Any]) -> str:
    """Определить тип поля по значениям."""
    non_null_values = [v for v in values if v is not None and v != ""]
    
    if not non_null_values:
        return "string"
    
    sample = non_null_values[:100]  # Анализируем первые 100
    
    # Проверяем списки
    if any(isinstance(v, list) for v in sample):
        return "list"
    
    # Проверяем boolean
    bool_values = {"true", "false", "yes", "no", "да", "нет"}
    if all(str(v).lower() in bool_values for v in sample):
        return "boolean"
    
    # Проверяем числа
    try:
        for v in sample:
            float(v)
        return "number"
    except (ValueError, TypeError):
        pass
    
    # Проверяем даты
    date_patterns = [
        r"^\d{4}-\d{2}-\d{2}",  # ISO date
        r"^\d{2}\.\d{2}\.\d{4}",  # DD.MM.YYYY
    ]
    import re
    if all(any(re.match(p, str(v)) for p in date_patterns) for v in sample if v):
        return "date"
    
    return "string"


def _find_common_patterns(field_docs: dict[str, set[str]]) -> list[str]:
    """Найти часто встречающиеся комбинации полей."""
    # Простая эвристика: находим поля, которые всегда встречаются вместе
    patterns = []
    
    field_names = list(field_docs.keys())
    for i, f1 in enumerate(field_names):
        for f2 in field_names[i+1:]:
            docs1 = field_docs[f1]
            docs2 = field_docs[f2]
            
            # Если пересечение > 80% от меньшего множества
            intersection = len(docs1 & docs2)
            min_size = min(len(docs1), len(docs2))
            
            if min_size > 0 and intersection / min_size > 0.8:
                patterns.append(f"{f1} + {f2}")
    
    return patterns[:10]
```

### 3.4 MCP Tools

```python
# Добавить в mcp_server.py

@mcp.tool()
async def get_frontmatter(vault_name: str, file_path: str) -> str:
    """
    Получить frontmatter конкретного файла.
    
    Args:
        vault_name: Имя vault'а
        file_path: Путь к файлу (относительный от корня vault)
    
    Returns:
        YAML frontmatter файла или сообщение об ошибке
    
    Examples:
        get_frontmatter("naumen-cto", "People/Иван Иванов.md")
    """
    api = services.frontmatter_api
    result = await api.get_frontmatter(vault_name, file_path)
    
    if result is None:
        return f"Файл '{file_path}' не найден в vault '{vault_name}'"
    
    import yaml
    lines = [f"## Frontmatter: {file_path}\n"]
    lines.append("```yaml")
    lines.append(yaml.dump(result, allow_unicode=True, default_flow_style=False))
    lines.append("```")
    
    return "\n".join(lines)


@mcp.tool()
async def get_vault_schema(
    vault_name: str,
    doc_type: str | None = None,
    top_values: int = 10
) -> str:
    """
    Получить схему frontmatter vault'а — все поля, их типы и значения.
    
    Полезно для понимания структуры данных vault'а и доступных полей
    для фильтрации.
    
    Args:
        vault_name: Имя vault'а
        doc_type: Опционально — ограничить типом документа
        top_values: Количество примеров значений для каждого поля (default: 10)
    
    Returns:
        Структурированная схема полей с примерами значений
    
    Examples:
        get_vault_schema("naumen-cto")  # Все поля vault'а
        get_vault_schema("naumen-cto", "person")  # Только для type:person
        get_vault_schema("naumen-cto", "1-1", top_values=5)
    """
    api = services.frontmatter_api
    schema = await api.get_schema(vault_name, doc_type, top_values)
    
    type_filter = f" (type: {doc_type})" if doc_type else ""
    lines = [f"## Схема vault: {vault_name}{type_filter}\n"]
    lines.append(f"**Всего документов:** {schema.total_documents}\n")
    
    if not schema.fields:
        lines.append("*Поля не найдены*")
        return "\n".join(lines)
    
    lines.append("### Поля frontmatter\n")
    lines.append("| Поле | Тип | Документов | Уникальных | Примеры значений |")
    lines.append("|------|-----|------------|------------|------------------|")
    
    for field_name, info in sorted(schema.fields.items()):
        examples = ", ".join(f"`{v}`" for v in info.unique_values[:5])
        if info.unique_count > 5:
            examples += f" ... (+{info.unique_count - 5})"
        
        lines.append(
            f"| {field_name} | {info.field_type} | {info.document_count} | "
            f"{info.unique_count} | {examples} |"
        )
    
    if schema.common_patterns:
        lines.append("\n### Частые комбинации полей\n")
        for pattern in schema.common_patterns:
            lines.append(f"- {pattern}")
    
    return "\n".join(lines)


@mcp.tool()
async def list_by_property(
    vault_name: str,
    property_key: str,
    property_value: str | None = None,
    limit: int = 50
) -> str:
    """
    Получить документы по значению свойства frontmatter.
    
    Позволяет искать по любому полю frontmatter, не только по стандартным
    (type, tags). Если property_value не указан, возвращает все документы
    с этим полем.
    
    Args:
        vault_name: Имя vault'а
        property_key: Имя свойства (например "status", "role", "project", "priority")
        property_value: Значение свойства (если None — все документы с этим полем)
        limit: Максимум результатов (default: 50)
    
    Returns:
        Список документов с запрошенным свойством
    
    Examples:
        list_by_property("vault", "status", "in-progress")  # Документы со статусом
        list_by_property("vault", "role")  # Все документы с полем role
        list_by_property("vault", "priority", "high", limit=10)
    """
    api = services.frontmatter_api
    results = await api.list_by_property(vault_name, property_key, property_value, limit)
    
    value_filter = f" = {property_value}" if property_value else ""
    lines = [f"## Документы: {property_key}{value_filter}\n"]
    lines.append(f"**Найдено:** {len(results)} документов\n")
    
    if not results:
        lines.append("*Документы не найдены*")
        return "\n".join(lines)
    
    for doc in results:
        title = doc.get("title") or doc.get("file_path", "Без названия")
        file_path = doc.get("file_path", "")
        modified = doc.get("modified_at")
        modified_str = modified.strftime("%Y-%m-%d") if modified else "—"
        
        lines.append(f"- **{title}**")
        lines.append(f"  - Путь: `{file_path}`")
        lines.append(f"  - Изменён: {modified_str}")
    
    return "\n".join(lines)


@mcp.tool()
async def aggregate_by_property(
    vault_name: str,
    property_key: str,
    doc_type: str | None = None
) -> str:
    """
    Агрегация по свойству — количество документов для каждого значения.
    
    Полезно для получения статистики по vault'у: распределение по статусам,
    приоритетам, ролям и т.д.
    
    Args:
        vault_name: Имя vault'а
        property_key: Имя свойства для группировки (status, priority, role, etc.)
        doc_type: Опционально — ограничить типом документа
    
    Returns:
        Таблица: значение → количество документов
    
    Examples:
        aggregate_by_property("vault", "status")  # Распределение по статусам
        aggregate_by_property("vault", "priority", "task")  # Приоритеты задач
        aggregate_by_property("vault", "role", "person")  # Роли людей
    """
    api = services.frontmatter_api
    result = await api.aggregate_by_property(vault_name, property_key, doc_type)
    
    type_filter = f" (type: {doc_type})" if doc_type else ""
    lines = [f"## Агрегация: {property_key}{type_filter}\n"]
    lines.append(f"**Всего документов:** {result.total_documents}\n")
    
    if not result.values:
        lines.append("*Значения не найдены*")
        return "\n".join(lines)
    
    lines.append("| Значение | Количество | % |")
    lines.append("|----------|------------|---|")
    
    total = result.total_documents
    for value, count in sorted(result.values.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        lines.append(f"| {value} | {count} | {percentage:.1f}% |")
    
    if result.null_count > 0:
        percentage = (result.null_count / total * 100) if total > 0 else 0
        lines.append(f"| *(пусто)* | {result.null_count} | {percentage:.1f}% |")
    
    return "\n".join(lines)
```

---

## 4. Компонент 2: DataviewService

### 4.1 Обзор

DataviewService предоставляет SQL-подобный синтаксис для запросов по frontmatter, вдохновлённый плагином Dataview для Obsidian.

### 4.2 Синтаксис запросов

```
SELECT [fields]
FROM [type:X | path:Y]
WHERE [conditions]
SORT BY [field] [ASC|DESC]
LIMIT N
```

**Примеры:**

```sql
-- Все незавершённые 1-1 с Иваном
SELECT title, date, status
FROM type:1-1
WHERE status != "done" AND links CONTAINS "Иван Иванов"
SORT BY date DESC
LIMIT 10

-- Все люди с ролью manager
SELECT title, role, team
FROM type:person
WHERE role = "manager"

-- Документы, изменённые за последнюю неделю
SELECT *
FROM path:Projects
WHERE modified > "last_week"
SORT BY modified DESC
```

### 4.3 Интерфейс

```python
# src/obsidian_kb/interfaces.py

@dataclass
class DataviewQuery:
    """Структурированный Dataview запрос."""
    select: list[str]  # Поля или ["*"]
    from_type: str | None = None  # type:X
    from_path: str | None = None  # path:Y
    where: list[WhereCondition] | None = None
    sort_by: str | None = None
    sort_order: str = "desc"  # "asc" | "desc"
    limit: int = 50


@dataclass
class WhereCondition:
    """Условие WHERE."""
    field: str
    operator: str  # "=", "!=", ">", "<", ">=", "<=", "CONTAINS", "NOT CONTAINS"
    value: Any
    connector: str = "AND"  # "AND" | "OR"


@dataclass
class DataviewResult:
    """Результат Dataview запроса."""
    documents: list[dict]  # Документы с запрошенными полями
    total_count: int
    query_time_ms: float
    query_string: str  # Исходный запрос для отладки


class IDataviewService(Protocol):
    """Интерфейс Dataview-подобных запросов."""
    
    async def query(
        self,
        vault_name: str,
        query: DataviewQuery
    ) -> DataviewResult:
        """Выполнить структурированный запрос."""
        ...
    
    async def query_string(
        self,
        vault_name: str,
        query_string: str
    ) -> DataviewResult:
        """Выполнить запрос из строки SQL-like синтаксиса."""
        ...
    
    def parse_query(self, query_string: str) -> DataviewQuery:
        """Распарсить строку запроса."""
        ...
```

### 4.4 Реализация парсера WHERE

```python
# src/obsidian_kb/query/where_parser.py

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class WhereCondition:
    """Условие WHERE."""
    field: str
    operator: str
    value: Any
    connector: str = "AND"


class WhereParser:
    """Парсер WHERE условий."""
    
    # Поддерживаемые операторы
    OPERATORS = {
        "=": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        "CONTAINS": lambda a, b: b in a if isinstance(a, (list, str)) else False,
        "NOT CONTAINS": lambda a, b: b not in a if isinstance(a, (list, str)) else True,
        "STARTS WITH": lambda a, b: str(a).startswith(str(b)),
        "ENDS WITH": lambda a, b: str(a).endswith(str(b)),
        "IS NULL": lambda a, b: a is None or a == "",
        "IS NOT NULL": lambda a, b: a is not None and a != "",
    }
    
    # Паттерн для парсинга условий
    CONDITION_PATTERN = re.compile(
        r'(\w+)\s*'  # Имя поля
        r'(=|!=|>=|<=|>|<|CONTAINS|NOT CONTAINS|STARTS WITH|ENDS WITH|IS NULL|IS NOT NULL)\s*'  # Оператор
        r'(?:"([^"]+)"|\'([^\']+)\'|(\S+))?',  # Значение (в кавычках или без)
        re.IGNORECASE
    )
    
    # Относительные даты
    RELATIVE_DATES = {
        "today": lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        "yesterday": lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1),
        "last_week": lambda: datetime.now() - timedelta(weeks=1),
        "last_month": lambda: datetime.now() - timedelta(days=30),
        "last_year": lambda: datetime.now() - timedelta(days=365),
    }
    
    @classmethod
    def parse(cls, where_string: str) -> list[WhereCondition]:
        """
        Парсинг WHERE строки.
        
        Args:
            where_string: Строка условий, например:
                "status != done AND priority > 2"
                "role = manager OR role = director"
                "created > last_week"
        
        Returns:
            Список WhereCondition
        """
        conditions = []
        
        # Разбиваем по AND/OR
        parts = re.split(r'\s+(AND|OR)\s+', where_string, flags=re.IGNORECASE)
        
        connector = "AND"
        for part in parts:
            part = part.strip()
            
            if part.upper() in ("AND", "OR"):
                connector = part.upper()
                continue
            
            match = cls.CONDITION_PATTERN.match(part)
            if match:
                field = match.group(1)
                operator = match.group(2).upper()
                # Значение может быть в разных группах
                value = match.group(3) or match.group(4) or match.group(5)
                
                # Обработка относительных дат
                if value and value.lower() in cls.RELATIVE_DATES:
                    value = cls.RELATIVE_DATES[value.lower()]()
                
                conditions.append(WhereCondition(
                    field=field,
                    operator=operator,
                    value=value,
                    connector=connector
                ))
                
                connector = "AND"  # Reset
        
        return conditions
    
    @classmethod
    def evaluate(cls, conditions: list[WhereCondition], document: dict) -> bool:
        """
        Проверка документа на соответствие условиям.
        
        Args:
            conditions: Список условий
            document: Документ для проверки
        
        Returns:
            True если документ соответствует всем условиям
        """
        if not conditions:
            return True
        
        result = True
        prev_connector = "AND"
        
        for condition in conditions:
            doc_value = document.get(condition.field)
            
            # Получаем функцию оператора
            op_func = cls.OPERATORS.get(condition.operator)
            if not op_func:
                continue
            
            # Вычисляем результат условия
            try:
                condition_result = op_func(doc_value, condition.value)
            except (TypeError, ValueError):
                condition_result = False
            
            # Комбинируем с предыдущим результатом
            if prev_connector == "AND":
                result = result and condition_result
            else:  # OR
                result = result or condition_result
            
            prev_connector = condition.connector
        
        return result
```

### 4.5 Реализация DataviewService

```python
# src/obsidian_kb/services/dataview_service.py

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

from obsidian_kb.interfaces import (
    DataviewQuery,
    DataviewResult,
    IDataviewService,
    WhereCondition,
)
from obsidian_kb.query.where_parser import WhereParser
from obsidian_kb.service_container import get_service_container

logger = logging.getLogger(__name__)


class DataviewService(IDataviewService):
    """SQL-подобные запросы по frontmatter."""
    
    def __init__(self):
        self._services = get_service_container()
    
    async def query(
        self,
        vault_name: str,
        query: DataviewQuery
    ) -> DataviewResult:
        """Выполнить структурированный запрос."""
        start_time = time.time()
        
        db_manager = self._services.db_manager
        
        try:
            # Получаем таблицы
            documents_table = await db_manager._ensure_table(vault_name, "documents")
            properties_table = await db_manager._ensure_table(vault_name, "document_properties")
            
            def _execute_query() -> list[dict]:
                # Шаг 1: Получаем все документы
                all_docs = documents_table.to_arrow().to_pylist()
                
                # Шаг 2: Получаем все свойства и группируем по document_id
                all_props = properties_table.to_arrow().to_pylist()
                props_by_doc: dict[str, dict] = {}
                
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
                
                # Шаг 4: Фильтрация по FROM (type или path)
                if query.from_type:
                    enriched_docs = [
                        d for d in enriched_docs 
                        if d.get("type") == query.from_type
                    ]
                
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
            logger.error(f"Dataview query error: {e}")
            return DataviewResult(
                documents=[],
                total_count=0,
                query_time_ms=0,
                query_string=self._query_to_string(query)
            )
    
    async def query_string(
        self,
        vault_name: str,
        query_string: str
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
        select_match = re.search(r'SELECT\s+(.+?)(?=\s+FROM|\s+WHERE|\s+SORT|\s+LIMIT|$)', query_string, re.IGNORECASE)
        if select_match:
            select_str = select_match.group(1).strip()
            if select_str != "*":
                select = [s.strip() for s in select_str.split(",")]
        
        # Парсим FROM
        from_match = re.search(r'FROM\s+(?:type:(\S+)|path:(\S+))', query_string, re.IGNORECASE)
        if from_match:
            from_type = from_match.group(1)
            from_path = from_match.group(2)
        
        # Парсим WHERE
        where_match = re.search(r'WHERE\s+(.+?)(?=\s+SORT|\s+LIMIT|$)', query_string, re.IGNORECASE)
        if where_match:
            where_str = where_match.group(1).strip()
            where = WhereParser.parse(where_str)
        
        # Парсим SORT BY
        sort_match = re.search(r'SORT\s+BY\s+(\w+)(?:\s+(ASC|DESC))?', query_string, re.IGNORECASE)
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
```

### 4.6 MCP Tool

```python
# Добавить в mcp_server.py

@mcp.tool()
async def dataview_query(
    vault_name: str,
    query: str | None = None,
    select: str = "*",
    from_type: str | None = None,
    from_path: str | None = None,
    where: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "desc",
    limit: int = 50
) -> str:
    """
    SQL-подобный запрос по документам vault'а (Dataview-style).
    
    Можно использовать либо полный SQL-like синтаксис в параметре `query`,
    либо отдельные параметры.
    
    Args:
        vault_name: Имя vault'а
        query: Полный SQL-like запрос (если указан, остальные параметры игнорируются)
               Пример: "SELECT title, status FROM type:task WHERE status != done SORT BY priority DESC"
        select: Поля через запятую (по умолчанию "*")
        from_type: Фильтр по типу документа
        from_path: Фильтр по пути (например "Projects/Alpha")
        where: Условия фильтрации (status != done, priority > 2)
        sort_by: Поле для сортировки
        sort_order: Порядок сортировки (asc/desc)
        limit: Максимум результатов (default: 50)
    
    Returns:
        Таблица результатов в markdown формате
    
    Examples:
        # Полный SQL-like синтаксис
        dataview_query("vault", query="SELECT * FROM type:1-1 WHERE status != done SORT BY date DESC")
        
        # Отдельные параметры
        dataview_query("vault", from_type="person", where="role = manager", sort_by="name")
        
        # Комбинация
        dataview_query("vault", select="title,status", from_path="Projects", where="status = active")
    """
    service = services.dataview_service
    
    if query:
        # Используем полный SQL-like синтаксис
        result = await service.query_string(vault_name, query)
    else:
        # Собираем DataviewQuery из параметров
        from obsidian_kb.interfaces import DataviewQuery
        from obsidian_kb.query.where_parser import WhereParser
        
        select_fields = [s.strip() for s in select.split(",")] if select != "*" else ["*"]
        where_conditions = WhereParser.parse(where) if where else None
        
        dv_query = DataviewQuery(
            select=select_fields,
            from_type=from_type,
            from_path=from_path,
            where=where_conditions,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit
        )
        result = await service.query(vault_name, dv_query)
    
    # Форматируем результат
    lines = [f"## Dataview Query Results\n"]
    lines.append(f"**Запрос:** `{result.query_string}`")
    lines.append(f"**Найдено:** {result.total_count} документов")
    lines.append(f"**Время:** {result.query_time_ms:.1f} мс\n")
    
    if not result.documents:
        lines.append("*Документы не найдены*")
        return "\n".join(lines)
    
    # Определяем колонки для таблицы
    if result.documents:
        columns = list(result.documents[0].keys())
        # Убираем служебные поля
        columns = [c for c in columns if not c.startswith("_") and c != "document_id"]
        
        # Формируем таблицу
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        
        for doc in result.documents:
            values = []
            for col in columns:
                val = doc.get(col, "")
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                elif val is None:
                    val = "—"
                else:
                    val = str(val)[:50]  # Обрезаем длинные значения
                values.append(val)
            lines.append("| " + " | ".join(values) + " |")
    
    return "\n".join(lines)
```

---

## 5. Компонент 3: RipgrepService

### 5.1 Обзор

RipgrepService предоставляет прямой текстовый поиск по файлам vault'а без использования индекса. Использует ripgrep если установлен, иначе fallback на grep.

### 5.2 Интерфейс

```python
# src/obsidian_kb/interfaces.py

@dataclass
class RipgrepMatch:
    """Результат поиска ripgrep."""
    file_path: str
    line_number: int
    line_content: str
    match_text: str
    match_start: int
    match_end: int
    context_before: list[str]
    context_after: list[str]


@dataclass
class RipgrepResult:
    """Результат ripgrep поиска."""
    matches: list[RipgrepMatch]
    total_matches: int
    files_searched: int
    search_time_ms: float


class IRipgrepService(Protocol):
    """Интерфейс для ripgrep поиска."""
    
    async def search_text(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
        context_lines: int = 2,
        file_pattern: str = "*.md",
        max_results: int = 100
    ) -> RipgrepResult:
        """Поиск текста в файлах."""
        ...
    
    async def search_regex(
        self,
        vault_path: str,
        pattern: str,
        context_lines: int = 2,
        file_pattern: str = "*.md",
        max_results: int = 100
    ) -> RipgrepResult:
        """Поиск по regex паттерну."""
        ...
    
    async def find_files(
        self,
        vault_path: str,
        name_pattern: str,
        content_contains: str | None = None
    ) -> list[str]:
        """Поиск файлов по имени и/или содержимому."""
        ...
    
    def is_ripgrep_available(self) -> bool:
        """Проверка доступности ripgrep."""
        ...
```

### 5.3 Реализация

```python
# src/obsidian_kb/services/ripgrep_service.py

import asyncio
import json
import logging
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from obsidian_kb.interfaces import IRipgrepService, RipgrepMatch, RipgrepResult

logger = logging.getLogger(__name__)


class RipgrepService(IRipgrepService):
    """Прямой текстовый поиск по файлам vault'а."""
    
    def __init__(self):
        self._ripgrep_path = shutil.which("rg")
        self._grep_path = shutil.which("grep")
    
    def is_ripgrep_available(self) -> bool:
        """Проверка доступности ripgrep."""
        return self._ripgrep_path is not None
    
    async def search_text(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
        context_lines: int = 2,
        file_pattern: str = "*.md",
        max_results: int = 100
    ) -> RipgrepResult:
        """Поиск текста в файлах vault'а."""
        start_time = time.time()
        
        if self._ripgrep_path:
            result = await self._search_with_ripgrep(
                vault_path, query, case_sensitive, whole_word,
                context_lines, file_pattern, max_results, is_regex=False
            )
        elif self._grep_path:
            result = await self._search_with_grep(
                vault_path, query, case_sensitive, whole_word,
                context_lines, file_pattern, max_results
            )
        else:
            result = await self._search_with_python(
                vault_path, query, case_sensitive, whole_word,
                context_lines, file_pattern, max_results
            )
        
        result.search_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def search_regex(
        self,
        vault_path: str,
        pattern: str,
        context_lines: int = 2,
        file_pattern: str = "*.md",
        max_results: int = 100
    ) -> RipgrepResult:
        """Поиск по regex паттерну."""
        start_time = time.time()
        
        if self._ripgrep_path:
            result = await self._search_with_ripgrep(
                vault_path, pattern, case_sensitive=True, whole_word=False,
                context_lines=context_lines, file_pattern=file_pattern,
                max_results=max_results, is_regex=True
            )
        else:
            result = await self._search_regex_python(
                vault_path, pattern, context_lines, file_pattern, max_results
            )
        
        result.search_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def find_files(
        self,
        vault_path: str,
        name_pattern: str,
        content_contains: str | None = None
    ) -> list[str]:
        """Поиск файлов по имени и/или содержимому."""
        vault = Path(vault_path)
        
        # Находим файлы по паттерну имени
        matching_files = list(vault.glob(f"**/{name_pattern}"))
        
        # Фильтруем по содержимому если нужно
        if content_contains:
            filtered = []
            for file_path in matching_files:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if content_contains.lower() in content.lower():
                        filtered.append(str(file_path.relative_to(vault)))
                except Exception:
                    continue
            return filtered
        
        return [str(f.relative_to(vault)) for f in matching_files]
    
    async def _search_with_ripgrep(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool,
        whole_word: bool,
        context_lines: int,
        file_pattern: str,
        max_results: int,
        is_regex: bool
    ) -> RipgrepResult:
        """Поиск с использованием ripgrep."""
        args = [
            self._ripgrep_path,
            "--json",  # JSON output
            f"--context={context_lines}",
            f"--glob={file_pattern}",
            f"--max-count={max_results}",
        ]
        
        if not case_sensitive:
            args.append("--ignore-case")
        
        if whole_word:
            args.append("--word-regexp")
        
        if not is_regex:
            args.append("--fixed-strings")
        
        args.extend([query, vault_path])
        
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if stderr:
            logger.warning(f"ripgrep stderr: {stderr.decode()}")
        
        # Парсим JSON output
        matches = []
        files_searched = set()
        context_buffer: dict[str, list[str]] = {}
        
        for line in stdout.decode().strip().split("\n"):
            if not line:
                continue
            
            try:
                data = json.loads(line)
                msg_type = data.get("type")
                
                if msg_type == "match":
                    match_data = data["data"]
                    file_path = match_data["path"]["text"]
                    files_searched.add(file_path)
                    
                    for submatch in match_data.get("submatches", []):
                        matches.append(RipgrepMatch(
                            file_path=Path(file_path).relative_to(vault_path).as_posix(),
                            line_number=match_data["line_number"],
                            line_content=match_data["lines"]["text"].strip(),
                            match_text=submatch["match"]["text"],
                            match_start=submatch["start"],
                            match_end=submatch["end"],
                            context_before=[],  # Заполняется ниже
                            context_after=[]
                        ))
                
                elif msg_type == "context":
                    # Контекст обрабатывается ripgrep автоматически
                    pass
                
            except json.JSONDecodeError:
                continue
        
        return RipgrepResult(
            matches=matches[:max_results],
            total_matches=len(matches),
            files_searched=len(files_searched),
            search_time_ms=0  # Будет заполнено в вызывающем методе
        )
    
    async def _search_with_grep(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool,
        whole_word: bool,
        context_lines: int,
        file_pattern: str,
        max_results: int
    ) -> RipgrepResult:
        """Fallback поиск с grep."""
        args = [
            self._grep_path,
            "-r",  # Recursive
            f"--include={file_pattern}",
            "-n",  # Line numbers
            f"-C{context_lines}",  # Context
        ]
        
        if not case_sensitive:
            args.append("-i")
        
        if whole_word:
            args.append("-w")
        
        args.extend([query, vault_path])
        
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await proc.communicate()
        
        # Парсим grep output
        matches = []
        current_file = None
        
        for line in stdout.decode().strip().split("\n"):
            if not line:
                continue
            
            # Формат: file:line_number:content
            parts = line.split(":", 2)
            if len(parts) >= 3:
                file_path = parts[0]
                try:
                    line_number = int(parts[1])
                    content = parts[2]
                    
                    matches.append(RipgrepMatch(
                        file_path=Path(file_path).relative_to(vault_path).as_posix(),
                        line_number=line_number,
                        line_content=content.strip(),
                        match_text=query,
                        match_start=content.lower().find(query.lower()),
                        match_end=content.lower().find(query.lower()) + len(query),
                        context_before=[],
                        context_after=[]
                    ))
                except ValueError:
                    continue
        
        files_searched = len(set(m.file_path for m in matches))
        
        return RipgrepResult(
            matches=matches[:max_results],
            total_matches=len(matches),
            files_searched=files_searched,
            search_time_ms=0
        )
    
    async def _search_with_python(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool,
        whole_word: bool,
        context_lines: int,
        file_pattern: str,
        max_results: int
    ) -> RipgrepResult:
        """Pure Python fallback поиск."""
        vault = Path(vault_path)
        matches = []
        files_searched = 0
        
        search_query = query if case_sensitive else query.lower()
        
        for file_path in vault.glob(f"**/{file_pattern}"):
            files_searched += 1
            
            try:
                lines = file_path.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            
            for i, line in enumerate(lines):
                search_line = line if case_sensitive else line.lower()
                
                if search_query in search_line:
                    # Проверка whole_word
                    if whole_word:
                        pattern = rf'\b{re.escape(search_query)}\b'
                        if not re.search(pattern, search_line, re.IGNORECASE if not case_sensitive else 0):
                            continue
                    
                    # Контекст
                    context_before = lines[max(0, i - context_lines):i]
                    context_after = lines[i + 1:i + 1 + context_lines]
                    
                    match_start = search_line.find(search_query)
                    
                    matches.append(RipgrepMatch(
                        file_path=file_path.relative_to(vault).as_posix(),
                        line_number=i + 1,
                        line_content=line.strip(),
                        match_text=query,
                        match_start=match_start,
                        match_end=match_start + len(query),
                        context_before=context_before,
                        context_after=context_after
                    ))
                    
                    if len(matches) >= max_results:
                        break
            
            if len(matches) >= max_results:
                break
        
        return RipgrepResult(
            matches=matches,
            total_matches=len(matches),
            files_searched=files_searched,
            search_time_ms=0
        )
    
    async def _search_regex_python(
        self,
        vault_path: str,
        pattern: str,
        context_lines: int,
        file_pattern: str,
        max_results: int
    ) -> RipgrepResult:
        """Pure Python regex поиск."""
        vault = Path(vault_path)
        matches = []
        files_searched = 0
        
        try:
            regex = re.compile(pattern)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {e}")
            return RipgrepResult(
                matches=[],
                total_matches=0,
                files_searched=0,
                search_time_ms=0
            )
        
        for file_path in vault.glob(f"**/{file_pattern}"):
            files_searched += 1
            
            try:
                lines = file_path.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            
            for i, line in enumerate(lines):
                match = regex.search(line)
                if match:
                    context_before = lines[max(0, i - context_lines):i]
                    context_after = lines[i + 1:i + 1 + context_lines]
                    
                    matches.append(RipgrepMatch(
                        file_path=file_path.relative_to(vault).as_posix(),
                        line_number=i + 1,
                        line_content=line.strip(),
                        match_text=match.group(),
                        match_start=match.start(),
                        match_end=match.end(),
                        context_before=context_before,
                        context_after=context_after
                    ))
                    
                    if len(matches) >= max_results:
                        break
            
            if len(matches) >= max_results:
                break
        
        return RipgrepResult(
            matches=matches,
            total_matches=len(matches),
            files_searched=files_searched,
            search_time_ms=0
        )
```

### 5.4 MCP Tools

```python
# Добавить в mcp_server.py

@mcp.tool()
async def search_text(
    vault_name: str,
    query: str,
    case_sensitive: bool = False,
    whole_word: bool = False,
    context_lines: int = 2,
    file_pattern: str = "*.md",
    limit: int = 50
) -> str:
    """
    Прямой текстовый поиск по файлам vault'а (ripgrep).
    
    В отличие от search_vault, работает без индекса и ищет точные совпадения
    в исходных файлах. Полезно для поиска TODO, FIXME, конкретных фраз.
    
    Args:
        vault_name: Имя vault'а
        query: Текст для поиска
        case_sensitive: Учитывать регистр (default: False)
        whole_word: Искать только целые слова (default: False)
        context_lines: Строк контекста до/после совпадения (default: 2)
        file_pattern: Паттерн файлов для поиска (default: "*.md")
        limit: Максимум результатов (default: 50)
    
    Returns:
        Найденные строки с контекстом
    
    Examples:
        search_text("vault", "TODO:")  # Все TODO комментарии
        search_text("vault", "[[Иван Иванов]]")  # Все упоминания человека
        search_text("vault", "ВАЖНО", case_sensitive=True)
        search_text("vault", "error", file_pattern="*.log")
    """
    # Получаем путь к vault'у
    vault_path = await _get_vault_path(vault_name)
    if not vault_path:
        return f"Vault '{vault_name}' не найден в конфигурации."
    
    service = services.ripgrep_service
    result = await service.search_text(
        vault_path, query, case_sensitive, whole_word,
        context_lines, file_pattern, limit
    )
    
    # Форматируем результат
    backend = "ripgrep" if service.is_ripgrep_available() else "grep/python"
    lines = [f"## Текстовый поиск: `{query}`\n"]
    lines.append(f"**Backend:** {backend}")
    lines.append(f"**Найдено:** {result.total_matches} совпадений в {result.files_searched} файлах")
    lines.append(f"**Время:** {result.search_time_ms:.1f} мс\n")
    
    if not result.matches:
        lines.append("*Совпадения не найдены*")
        return "\n".join(lines)
    
    # Группируем по файлам
    by_file: dict[str, list[RipgrepMatch]] = {}
    for match in result.matches:
        if match.file_path not in by_file:
            by_file[match.file_path] = []
        by_file[match.file_path].append(match)
    
    for file_path, matches in by_file.items():
        lines.append(f"### {file_path}\n")
        
        for match in matches:
            lines.append(f"**Строка {match.line_number}:**")
            
            # Контекст до
            if match.context_before:
                for ctx in match.context_before:
                    lines.append(f"  {ctx}")
            
            # Строка с совпадением (выделяем match)
            line = match.line_content
            lines.append(f"> {line}")
            
            # Контекст после
            if match.context_after:
                for ctx in match.context_after:
                    lines.append(f"  {ctx}")
            
            lines.append("")
    
    return "\n".join(lines)


@mcp.tool()
async def search_regex(
    vault_name: str,
    pattern: str,
    context_lines: int = 2,
    file_pattern: str = "*.md",
    limit: int = 50
) -> str:
    """
    Поиск по регулярному выражению в файлах vault'а.
    
    Мощный инструмент для поиска паттернов: wikilinks, теги, задачи и т.д.
    
    Args:
        vault_name: Имя vault'а
        pattern: Regex паттерн (Python/ripgrep синтаксис)
        context_lines: Строк контекста (default: 2)
        file_pattern: Паттерн файлов (default: "*.md")
        limit: Максимум результатов (default: 50)
    
    Returns:
        Найденные совпадения с контекстом
    
    Examples:
        search_regex("vault", r"\\[\\[.+?\\]\\]")  # Все wikilinks
        search_regex("vault", r"#\\w+")  # Все inline теги
        search_regex("vault", r"^\\s*-\\s*\\[ \\]")  # Незавершённые задачи
        search_regex("vault", r"https?://\\S+")  # Все URL
        search_regex("vault", r"\\d{4}-\\d{2}-\\d{2}")  # Все даты ISO формата
    """
    vault_path = await _get_vault_path(vault_name)
    if not vault_path:
        return f"Vault '{vault_name}' не найден в конфигурации."
    
    service = services.ripgrep_service
    result = await service.search_regex(
        vault_path, pattern, context_lines, file_pattern, limit
    )
    
    # Форматирование аналогично search_text
    lines = [f"## Regex поиск: `{pattern}`\n"]
    lines.append(f"**Найдено:** {result.total_matches} совпадений")
    lines.append(f"**Время:** {result.search_time_ms:.1f} мс\n")
    
    if not result.matches:
        lines.append("*Совпадения не найдены*")
        return "\n".join(lines)
    
    # Группируем и форматируем (аналогично search_text)
    by_file: dict[str, list] = {}
    for match in result.matches:
        if match.file_path not in by_file:
            by_file[match.file_path] = []
        by_file[match.file_path].append(match)
    
    for file_path, matches in by_file.items():
        lines.append(f"### {file_path}\n")
        for match in matches:
            lines.append(f"**Строка {match.line_number}:** `{match.match_text}`")
            lines.append(f"> {match.line_content}\n")
    
    return "\n".join(lines)


@mcp.tool()
async def find_files(
    vault_name: str,
    name_pattern: str,
    content_contains: str | None = None
) -> str:
    """
    Поиск файлов по имени и/или содержимому.
    
    Args:
        vault_name: Имя vault'а
        name_pattern: Glob паттерн имени файла (например "*.md", "README*", "2024-*")
        content_contains: Опционально — текст, который должен содержаться в файле
    
    Returns:
        Список найденных файлов
    
    Examples:
        find_files("vault", "*.md")  # Все markdown файлы
        find_files("vault", "README*")  # Все README файлы
        find_files("vault", "*.md", "TODO")  # Markdown с TODO
    """
    vault_path = await _get_vault_path(vault_name)
    if not vault_path:
        return f"Vault '{vault_name}' не найден в конфигурации."
    
    service = services.ripgrep_service
    files = await service.find_files(vault_path, name_pattern, content_contains)
    
    content_filter = f" содержащие '{content_contains}'" if content_contains else ""
    lines = [f"## Найденные файлы: `{name_pattern}`{content_filter}\n"]
    lines.append(f"**Найдено:** {len(files)} файлов\n")
    
    if not files:
        lines.append("*Файлы не найдены*")
        return "\n".join(lines)
    
    for file_path in files[:100]:  # Ограничиваем вывод
        lines.append(f"- `{file_path}`")
    
    if len(files) > 100:
        lines.append(f"\n*... и ещё {len(files) - 100} файлов*")
    
    return "\n".join(lines)


# Вспомогательная функция для получения пути к vault'у
async def _get_vault_path(vault_name: str) -> str | None:
    """Получить путь к vault'у из конфигурации."""
    config_path = settings.vaults_config
    
    if not config_path.exists():
        return None
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        for vault in config.get("vaults", []):
            if vault.get("name") == vault_name:
                return vault.get("path")
    except Exception:
        pass
    
    return None
```

---

## 6. Компонент 4: GraphQueryService

### 6.1 Обзор

GraphQueryService предоставляет запросы по связям между документами (wikilinks), включая поиск связанных документов, orphans и broken links.

### 6.2 Интерфейс

```python
# src/obsidian_kb/interfaces.py

@dataclass
class ConnectedDocument:
    """Связанный документ."""
    file_path: str
    title: str
    direction: str  # "incoming" | "outgoing"
    link_text: str  # Текст ссылки
    link_context: str | None  # Контекст вокруг ссылки


@dataclass
class GraphQueryResult:
    """Результат граф-запроса."""
    center_document: str
    connected: list[ConnectedDocument]
    depth: int
    total_incoming: int
    total_outgoing: int


class IGraphQueryService(Protocol):
    """Интерфейс для граф-запросов."""
    
    async def find_connected(
        self,
        vault_name: str,
        document_path: str,
        direction: str = "both",  # "incoming" | "outgoing" | "both"
        depth: int = 1,
        limit: int = 50
    ) -> GraphQueryResult:
        """Найти связанные документы."""
        ...
    
    async def find_orphans(
        self,
        vault_name: str,
        doc_type: str | None = None
    ) -> list[str]:
        """Найти документы без входящих ссылок."""
        ...
    
    async def find_broken_links(
        self,
        vault_name: str
    ) -> list[tuple[str, str]]:
        """Найти битые ссылки (файл, ссылка)."""
        ...
    
    async def get_backlinks(
        self,
        vault_name: str,
        document_path: str
    ) -> list[ConnectedDocument]:
        """Получить все backlinks для документа."""
        ...
```

### 6.3 MCP Tools (краткое описание)

```python
@mcp.tool()
async def find_connected(
    vault_name: str,
    document_path: str,
    direction: str = "both",
    depth: int = 1,
    limit: int = 50
) -> str:
    """
    Найти документы, связанные с указанным через wikilinks.
    
    Args:
        vault_name: Имя vault'а
        document_path: Путь к документу
        direction: "incoming" (кто ссылается), "outgoing" (на кого ссылается), "both"
        depth: Глубина поиска (1 = прямые связи, 2 = связи связей)
        limit: Максимум результатов
    
    Examples:
        find_connected("vault", "People/Иван.md")  # Все связи
        find_connected("vault", "Projects/Alpha.md", "incoming")  # Кто ссылается на проект
    """


@mcp.tool()
async def find_orphans(
    vault_name: str,
    doc_type: str | None = None
) -> str:
    """
    Найти документы без входящих ссылок (orphans).
    
    Полезно для аудита базы знаний — orphans могут быть забытыми
    или требовать интеграции.
    
    Args:
        vault_name: Имя vault'а
        doc_type: Опционально — ограничить типом документа
    """


@mcp.tool()
async def find_broken_links(
    vault_name: str
) -> str:
    """
    Найти битые wikilinks — ссылки на несуществующие документы.
    
    Returns:
        Список битых ссылок: файл → несуществующая ссылка
    """


@mcp.tool()
async def get_backlinks(
    vault_name: str,
    document_path: str
) -> str:
    """
    Получить все backlinks (входящие ссылки) для документа.
    
    Аналог панели Backlinks в Obsidian.
    """
```

---

## 7. Компонент 5: TimelineService

### 7.1 Обзор

TimelineService предоставляет хронологические запросы — timeline документов, recent changes и т.д.

### 7.2 MCP Tools

```python
@mcp.tool()
async def timeline(
    vault_name: str,
    doc_type: str | None = None,
    date_field: str = "created",
    after: str | None = None,
    before: str | None = None,
    limit: int = 50
) -> str:
    """
    Хронологическая лента документов.
    
    Args:
        vault_name: Имя vault'а
        doc_type: Опционально — фильтр по типу
        date_field: Поле для сортировки ("created", "modified" или кастомное)
        after: Документы после даты (ISO или "last_week", "last_month")
        before: Документы до даты
        limit: Максимум результатов
    
    Examples:
        timeline("vault", "meeting", date_field="date", after="2024-12-01")
        timeline("vault", after="last_week")  # Созданные за неделю
    """


@mcp.tool()
async def recent_changes(
    vault_name: str,
    days: int = 7,
    doc_type: str | None = None
) -> str:
    """
    Документы, изменённые за последние N дней.
    
    Разделяет на созданные и изменённые.
    
    Args:
        vault_name: Имя vault'а
        days: Количество дней (default: 7)
        doc_type: Опционально — фильтр по типу
    
    Examples:
        recent_changes("vault")  # Изменения за неделю
        recent_changes("vault", 30, "task")  # Задачи за месяц
    """
```

---

## 8. Компонент 6: BatchOperations

### 8.1 Обзор

BatchOperations предоставляет массовые операции — экспорт в CSV, сравнение схем vault'ов и т.д.

### 8.2 MCP Tools

```python
@mcp.tool()
async def export_to_csv(
    vault_name: str,
    output_path: str | None = None,
    doc_type: str | None = None,
    fields: str | None = None,
    where: str | None = None
) -> str:
    """
    Экспорт данных vault'а в CSV файл.
    
    Args:
        vault_name: Имя vault'а
        output_path: Путь для сохранения (если не указан — временный файл)
        doc_type: Опционально — фильтр по типу
        fields: Поля через запятую (если не указано — все поля)
        where: Условия фильтрации
    
    Returns:
        Путь к созданному CSV файлу
    
    Examples:
        export_to_csv("vault", doc_type="person", fields="title,role,team")
        export_to_csv("vault", where="status = active")
    """


@mcp.tool()
async def compare_schemas(
    vault_names: list[str]
) -> str:
    """
    Сравнить схемы frontmatter нескольких vault'ов.
    
    Показывает общие поля, уникальные поля и различия в значениях.
    
    Args:
        vault_names: Список имён vault'ов для сравнения
    
    Examples:
        compare_schemas(["vault1", "vault2"])
    """
```

---

## 9. MCP Tools Reference

### 9.1 Полный список новых инструментов

| Инструмент | Категория | Описание |
|------------|-----------|----------|
| `get_frontmatter` | FrontmatterAPI | Получить frontmatter файла |
| `get_vault_schema` | FrontmatterAPI | Схема frontmatter vault'а |
| `list_by_property` | FrontmatterAPI | Документы по свойству |
| `aggregate_by_property` | FrontmatterAPI | Агрегация по свойству |
| `dataview_query` | DataviewService | SQL-подобный запрос |
| `search_text` | RipgrepService | Текстовый поиск (ripgrep) |
| `search_regex` | RipgrepService | Regex поиск |
| `find_files` | RipgrepService | Поиск файлов |
| `find_connected` | GraphQueryService | Связанные документы |
| `find_orphans` | GraphQueryService | Orphan документы |
| `find_broken_links` | GraphQueryService | Битые ссылки |
| `get_backlinks` | GraphQueryService | Backlinks документа |
| `timeline` | TimelineService | Хронология документов |
| `recent_changes` | TimelineService | Недавние изменения |
| `export_to_csv` | BatchOperations | Экспорт в CSV |
| `compare_schemas` | BatchOperations | Сравнение vault'ов |

### 9.2 Сравнение с существующими инструментами

| Существующий | Новый | Отличие |
|--------------|-------|---------|
| `search_vault` | `dataview_query` | Структурированные запросы vs семантический поиск |
| `search_vault` | `search_text` | Прямой поиск vs индекс |
| `list_tags` | `get_vault_schema` | Полная схема vs только теги |
| — | `aggregate_by_property` | Новая функциональность |
| — | `find_connected` | Граф-запросы |

---

## 10. Интеграция с существующей архитектурой

### 10.1 Изменения в ServiceContainer

```python
# src/obsidian_kb/service_container.py

from obsidian_kb.services.frontmatter_api import FrontmatterAPI
from obsidian_kb.services.dataview_service import DataviewService
from obsidian_kb.services.ripgrep_service import RipgrepService
from obsidian_kb.services.graph_query_service import GraphQueryService
from obsidian_kb.services.timeline_service import TimelineService
from obsidian_kb.services.batch_operations import BatchOperations


class ServiceContainer:
    """Контейнер зависимостей с новыми сервисами."""
    
    # Existing services...
    
    @property
    def frontmatter_api(self) -> FrontmatterAPI:
        """FrontmatterAPI для работы с метаданными."""
        if self._frontmatter_api is None:
            self._frontmatter_api = FrontmatterAPI()
        return self._frontmatter_api
    
    @property
    def dataview_service(self) -> DataviewService:
        """DataviewService для SQL-подобных запросов."""
        if self._dataview_service is None:
            self._dataview_service = DataviewService()
        return self._dataview_service
    
    @property
    def ripgrep_service(self) -> RipgrepService:
        """RipgrepService для прямого текстового поиска."""
        if self._ripgrep_service is None:
            self._ripgrep_service = RipgrepService()
        return self._ripgrep_service
    
    @property
    def graph_query_service(self) -> GraphQueryService:
        """GraphQueryService для граф-запросов."""
        if self._graph_query_service is None:
            self._graph_query_service = GraphQueryService()
        return self._graph_query_service
    
    @property
    def timeline_service(self) -> TimelineService:
        """TimelineService для хронологических запросов."""
        if self._timeline_service is None:
            self._timeline_service = TimelineService()
        return self._timeline_service
    
    @property
    def batch_operations(self) -> BatchOperations:
        """BatchOperations для массовых операций."""
        if self._batch_operations is None:
            self._batch_operations = BatchOperations()
        return self._batch_operations
```

### 10.2 Изменения в interfaces.py

Добавить все новые интерфейсы (Protocol классы) из разделов выше.

### 10.3 Зависимости

Новые сервисы используют существующие компоненты:

```
FrontmatterAPI
  └── LanceDBManager (через ServiceContainer)
       └── document_properties table
       └── metadata table

DataviewService
  └── LanceDBManager
       └── documents table
       └── document_properties table
  └── WhereParser (новый)

RipgrepService
  └── Внешний ripgrep/grep (опционально)
  └── Filesystem (fallback)

GraphQueryService
  └── LanceDBManager
       └── chunks table (links field)
       └── documents table

TimelineService
  └── LanceDBManager
       └── documents table
       └── document_properties table

BatchOperations
  └── FrontmatterAPI
  └── DataviewService
```

---

## 11. План реализации

### Phase 1: Foundation (Неделя 1-2)

**Задачи:**
1. Создать структуру директорий `services/` и `query/`
2. Добавить интерфейсы в `interfaces.py`
3. Реализовать `FrontmatterAPI`:
   - `get_frontmatter()`
   - `get_schema()`
   - `list_by_property()`
   - `aggregate_by_property()`
4. Добавить MCP tools для FrontmatterAPI
5. Написать тесты

**Definition of Done:**
- [ ] Все методы FrontmatterAPI работают
- [ ] MCP tools доступны и документированы
- [ ] Тесты покрывают основные сценарии
- [ ] Обновлён CHANGELOG.md

### Phase 2: Dataview (Неделя 3-4)

**Задачи:**
1. Реализовать `WhereParser`
2. Реализовать `DataviewService`:
   - `query()`
   - `query_string()`
   - `parse_query()`
3. Добавить MCP tool `dataview_query`
4. Написать тесты для парсера и сервиса

**Definition of Done:**
- [ ] SQL-like синтаксис парсится корректно
- [ ] Запросы выполняются за < 500ms на 1000 документов
- [ ] Тесты покрывают edge cases парсера

### Phase 3: Ripgrep (Неделя 5)

**Задачи:**
1. Реализовать `RipgrepService`:
   - `search_text()` с ripgrep
   - `search_regex()`
   - Fallback на grep/python
   - `find_files()`
2. Добавить MCP tools
3. Написать тесты

**Definition of Done:**
- [ ] Ripgrep интеграция работает
- [ ] Fallback корректно работает без ripgrep
- [ ] Контекст отображается правильно

### Phase 4: Graph & Timeline (Неделя 6-7)

**Задачи:**
1. Реализовать `GraphQueryService`:
   - `find_connected()`
   - `find_orphans()`
   - `find_broken_links()`
   - `get_backlinks()`
2. Реализовать `TimelineService`:
   - `timeline()`
   - `recent_changes()`
3. Добавить MCP tools
4. Написать тесты

**Definition of Done:**
- [ ] Граф-запросы работают с depth > 1
- [ ] Timeline поддерживает кастомные date fields
- [ ] Orphans и broken links находятся корректно

### Phase 5: Batch & Polish (Неделя 8)

**Задачи:**
1. Реализовать `BatchOperations`:
   - `export_to_csv()`
   - `compare_schemas()`
2. Интеграционное тестирование
3. Обновить документацию
4. Performance оптимизация

**Definition of Done:**
- [ ] CSV экспорт работает
- [ ] Все компоненты интегрированы
- [ ] Документация обновлена
- [ ] Релиз версии с Extended Query API

---

## 12. Миграция и обратная совместимость

### 12.1 Обратная совместимость

**Гарантии:**
- Все существующие MCP tools (`search_vault`, `list_vaults`, etc.) работают без изменений
- Схема БД не изменяется
- Конфигурация не изменяется

**Потенциальные конфликты:**
- Нет — новые tools не пересекаются с существующими

### 12.2 Миграция

Миграция не требуется — новые сервисы используют существующую схему БД v4.

---

## 13. Тестирование

### 13.1 Unit Tests

```python
# tests/test_where_parser.py

import pytest
from obsidian_kb.query.where_parser import WhereParser, WhereCondition


class TestWhereParser:
    def test_simple_equality(self):
        conditions = WhereParser.parse("status = done")
        assert len(conditions) == 1
        assert conditions[0].field == "status"
        assert conditions[0].operator == "="
        assert conditions[0].value == "done"
    
    def test_not_equal(self):
        conditions = WhereParser.parse("status != done")
        assert conditions[0].operator == "!="
    
    def test_and_connector(self):
        conditions = WhereParser.parse("status = done AND priority > 2")
        assert len(conditions) == 2
        assert conditions[1].connector == "AND"
    
    def test_or_connector(self):
        conditions = WhereParser.parse("role = manager OR role = director")
        assert len(conditions) == 2
        assert conditions[1].connector == "OR"
    
    def test_quoted_value(self):
        conditions = WhereParser.parse('title = "Hello World"')
        assert conditions[0].value == "Hello World"
    
    def test_contains_operator(self):
        conditions = WhereParser.parse("tags CONTAINS python")
        assert conditions[0].operator == "CONTAINS"
    
    def test_relative_date(self):
        conditions = WhereParser.parse("created > last_week")
        assert conditions[0].value is not None
        assert isinstance(conditions[0].value, datetime)


class TestWhereEvaluate:
    def test_evaluate_equality(self):
        conditions = [WhereCondition("status", "=", "done", "AND")]
        assert WhereParser.evaluate(conditions, {"status": "done"}) == True
        assert WhereParser.evaluate(conditions, {"status": "pending"}) == False
    
    def test_evaluate_contains(self):
        conditions = [WhereCondition("tags", "CONTAINS", "python", "AND")]
        assert WhereParser.evaluate(conditions, {"tags": ["python", "async"]}) == True
        assert WhereParser.evaluate(conditions, {"tags": ["java"]}) == False
```

### 13.2 Integration Tests

```python
# tests/test_dataview_service.py

import pytest
from obsidian_kb.services.dataview_service import DataviewService
from obsidian_kb.interfaces import DataviewQuery


@pytest.mark.asyncio
class TestDataviewService:
    async def test_simple_query(self, indexed_vault):
        service = DataviewService()
        
        query = DataviewQuery(
            select=["title", "status"],
            from_type="task",
            limit=10
        )
        
        result = await service.query("test_vault", query)
        
        assert result.total_count > 0
        assert all("title" in doc for doc in result.documents)
    
    async def test_where_filter(self, indexed_vault):
        service = DataviewService()
        
        result = await service.query_string(
            "test_vault",
            "SELECT * FROM type:task WHERE status != done"
        )
        
        assert all(doc.get("status") != "done" for doc in result.documents)
    
    async def test_sort_by(self, indexed_vault):
        service = DataviewService()
        
        result = await service.query_string(
            "test_vault",
            "SELECT * FROM type:task SORT BY priority DESC"
        )
        
        priorities = [doc.get("priority", 0) for doc in result.documents]
        assert priorities == sorted(priorities, reverse=True)
```

### 13.3 Performance Tests

```python
# tests/test_performance.py

import pytest
import time


@pytest.mark.performance
class TestPerformance:
    async def test_dataview_query_performance(self, large_vault):
        """Dataview query должен выполняться < 500ms на 1000 документов."""
        service = DataviewService()
        
        start = time.time()
        result = await service.query_string(
            "large_vault",
            "SELECT * FROM type:note WHERE status != archived LIMIT 100"
        )
        elapsed = time.time() - start
        
        assert elapsed < 0.5, f"Query took {elapsed:.2f}s, expected < 0.5s"
    
    async def test_ripgrep_performance(self, large_vault):
        """Ripgrep поиск должен выполняться < 1s на 1000 файлов."""
        service = RipgrepService()
        
        start = time.time()
        result = await service.search_text(
            "/path/to/large_vault",
            "TODO",
            max_results=100
        )
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Search took {elapsed:.2f}s, expected < 1.0s"
```

---

## 14. Открытые вопросы

### 14.1 Требующие решения

| # | Вопрос | Варианты | Рекомендация |
|---|--------|----------|--------------|
| 1 | Синтаксис Dataview | Полная совместимость vs упрощённый | Упрощённый SQL-like |
| 2 | Ripgrep обязателен? | Да / Fallback / Опционально | Fallback на grep/python |
| 3 | Кэширование результатов | Да / Нет | Нет (данные динамичны) |
| 4 | Формат дат в WHERE | ISO only / Relative / Both | Both |
| 5 | Лимит по умолчанию | 20 / 50 / 100 | 50 |

### 14.2 Для обсуждения

1. **Приоритет реализации** — с какого компонента начать?
   - Рекомендация: FrontmatterAPI (основа для остальных)

2. **Расширение схемы БД** — нужны ли дополнительные индексы?
   - Рекомендация: Пока нет, измерить производительность сначала

3. **MCP Tools naming** — `dataview_query` vs `query_documents`?
   - Рекомендация: `dataview_query` (узнаваемо для пользователей Obsidian)

4. **Error handling** — как обрабатывать ошибки парсинга запросов?
   - Рекомендация: Возвращать понятное сообщение + пример правильного синтаксиса

---

## Приложения

### A. Примеры использования

```python
# Пример 1: Подготовка к 1-1
dataview_query(
    "naumen-cto",
    query="""
    SELECT title, date, status, topics
    FROM type:1-1
    WHERE links CONTAINS "Иван Иванов" AND status != "done"
    SORT BY date DESC
    LIMIT 5
    """
)

# Пример 2: Аудит базы знаний
find_orphans("naumen-cto")
find_broken_links("naumen-cto")

# Пример 3: Статистика по проектам
aggregate_by_property("naumen-cto", "status", doc_type="project")

# Пример 4: Поиск всех упоминаний
search_text("naumen-cto", "[[Production]]")
find_connected("naumen-cto", "Projects/Production.md", direction="incoming")

# Пример 5: Экспорт для отчёта
export_to_csv(
    "naumen-cto",
    doc_type="person",
    fields="title,role,team,hire_date"
)
```

### B. Глоссарий

| Термин | Определение |
|--------|-------------|
| Frontmatter | YAML метаданные в начале markdown файла |
| Wikilink | Ссылка в формате `[[Note Name]]` |
| Backlink | Входящая ссылка на документ |
| Orphan | Документ без входящих ссылок |
| Dataview | Плагин Obsidian для SQL-подобных запросов |
| Ripgrep | Быстрый grep на Rust (команда `rg`) |

---

*Документ создан: 2025-01-02*  
*Последнее обновление: 2025-01-02*