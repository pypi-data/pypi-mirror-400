# obsidian-kb Database Schema v2.1

## Архитектура хранения

```
┌─────────────────────────────────────────────────────────────────┐
│                         SQLITE                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐│
│  │   VAULTS    │ │  DOCUMENTS  │ │    DOCUMENT_PROPERTIES      ││
│  │             │ │             │ │  (нормализованный frontmatter)│
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐│
│  │    LINKS    │ │    TAGS     │ │     PROPERTY_SCHEMAS        ││
│  │   (граф)    │ │             │ │   (схема vault'а)           ││
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐│
│  │  ENTITIES   │ │   CACHE     │ │     SEARCH_HISTORY          ││
│  │   (NER)     │ │ (embeddings)│ │      (аналитика)            ││
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        LANCEDB                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                        CHUNKS                                ││
│  │  id | document_id | content | context | embedding | ...      ││
│  │  (векторный поиск + FTS + filtered search)                   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## SQLite Schema

### 1. VAULTS — Хранилища

```sql
CREATE TABLE vaults (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    config JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_indexed_at TIMESTAMP,
    doc_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0
);
```

**Config JSON:**
```json
{
  "embedding_model": "bge-m3",
  "embedding_dim": 1024,
  "chunk_size": 512,
  "chunk_overlap": 50,
  "excluded_paths": ["templates/", ".obsidian/"],
  "index_content": true,
  "extract_entities": true
}
```

---

### 2. DOCUMENTS — Документы

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    vault_id TEXT NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    
    -- Идентификация
    path TEXT NOT NULL,                    -- относительный путь от vault
    doc_id TEXT,                           -- семантический ID (vshadrin, psb)
    
    -- Метаданные
    title TEXT,
    doc_type TEXT,                         -- person, project, 1-1, adr, meeting
    
    -- Change detection
    content_hash TEXT NOT NULL,            -- MD5 для incremental indexing
    
    -- Контент (опционально, для full-text backup)
    content TEXT,
    
    -- Временные метки
    file_created_at TIMESTAMP,
    file_modified_at TIMESTAMP,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Денормализация для быстрых запросов
    chunk_count INTEGER DEFAULT 0,
    link_count INTEGER DEFAULT 0,
    backlink_count INTEGER DEFAULT 0,
    
    UNIQUE(vault_id, path)
);

-- Индексы
CREATE INDEX idx_documents_vault_type ON documents(vault_id, doc_type);
CREATE INDEX idx_documents_doc_id ON documents(vault_id, doc_id);
CREATE INDEX idx_documents_hash ON documents(content_hash);
CREATE INDEX idx_documents_modified ON documents(vault_id, file_modified_at DESC);
```

**Логика doc_id:**
| Тип | Паттерн | Пример |
|-----|---------|--------|
| person | {первая_буква}{фамилия} | vshadrin |
| project | короткое_имя | psb, smrm |
| 1-1 | {дата} | 2025-01-08 |
| adr | ADR-{номер} | ADR-001 |
| meeting | {дата}_{тема} | 2025-01-08_standup |

---

### 3. PROPERTY_SCHEMAS — Схема свойств vault'а

```sql
CREATE TABLE property_schemas (
    id TEXT PRIMARY KEY,
    vault_id TEXT NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    
    -- Определение свойства
    key TEXT NOT NULL,                     -- status, role, priority, participant
    value_type TEXT NOT NULL,              -- string, number, date, boolean, list, link
    
    -- Описание
    description TEXT,
    
    -- Ограничения
    allowed_values JSON,                   -- ["active", "done", "blocked"] для enum
    is_required BOOLEAN DEFAULT FALSE,
    is_list BOOLEAN DEFAULT FALSE,         -- tags: [a, b] vs tag: a
    
    -- Статистика
    doc_count INTEGER DEFAULT 0,           -- сколько документов имеют это свойство
    
    UNIQUE(vault_id, key)
);

CREATE INDEX idx_property_schemas_vault ON property_schemas(vault_id);
```

**Примеры схем для Naumen_CTO vault:**

| key | value_type | is_list | allowed_values | doc_count |
|-----|------------|---------|----------------|-----------|
| type | string | false | ["person","project","1-1","adr","meeting"] | 847 |
| status | string | false | ["active","done","blocked","archived"] | 234 |
| role | string | false | null | 45 |
| participant | link | true | null | 156 |
| priority | number | false | null | 89 |
| date | date | false | null | 312 |
| tags | string | true | null | 523 |

---

### 4. DOCUMENT_PROPERTIES — Значения свойств (нормализованный frontmatter)

```sql
CREATE TABLE document_properties (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    schema_id TEXT REFERENCES property_schemas(id),
    
    -- Ключ (дублируем для удобства запросов без JOIN)
    key TEXT NOT NULL,
    
    -- Типизированные значения (только одно заполнено)
    value_type TEXT NOT NULL,              -- string, number, date, boolean, link
    value_string TEXT,                     -- для string, enum
    value_number REAL,                     -- для number
    value_date TEXT,                       -- ISO format YYYY-MM-DD
    value_boolean INTEGER,                 -- 0/1
    value_link_target TEXT,                -- doc_id целевого документа
    value_link_raw TEXT,                   -- оригинальный [[...]] текст
    
    -- Для списков (tags: [a, b, c])
    list_index INTEGER DEFAULT 0,          -- 0 для скаляров, 0,1,2... для списков
    
    -- Источник
    source TEXT DEFAULT 'frontmatter'      -- frontmatter, inline, computed
);

-- Индексы для быстрого поиска по свойствам
CREATE INDEX idx_props_document ON document_properties(document_id);
CREATE INDEX idx_props_key ON document_properties(key);
CREATE INDEX idx_props_key_string ON document_properties(key, value_string);
CREATE INDEX idx_props_key_number ON document_properties(key, value_number);
CREATE INDEX idx_props_key_date ON document_properties(key, value_date);
CREATE INDEX idx_props_link_target ON document_properties(value_link_target);
```

**Пример хранения frontmatter:**

Исходный frontmatter:
```yaml
---
type: 1-1
participant: "[[07_PEOPLE/vshadrin/vshadrin|Шадрин]]"
date: 2025-01-08
status: active
tags:
  - meeting
  - q1-planning
priority: 1
---
```

Записи в DOCUMENT_PROPERTIES:

| document_id | key | value_type | value_string | value_number | value_date | value_link_target | list_index |
|-------------|-----|------------|--------------|--------------|------------|-------------------|------------|
| doc_003 | type | string | 1-1 | | | | 0 |
| doc_003 | participant | link | | | | vshadrin | 0 |
| doc_003 | date | date | | | 2025-01-08 | | 0 |
| doc_003 | status | string | active | | | | 0 |
| doc_003 | tags | string | meeting | | | | 0 |
| doc_003 | tags | string | q1-planning | | | | 1 |
| doc_003 | priority | number | | 1 | | | 0 |

---

### 5. TAGS — Теги

```sql
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    vault_id TEXT NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    
    name TEXT NOT NULL,                    -- оригинальное написание
    normalized TEXT NOT NULL,              -- lowercase, trimmed
    
    -- Иерархия тегов (projects/active → parent: projects)
    parent_tag_id TEXT REFERENCES tags(id),
    
    -- Статистика
    doc_count INTEGER DEFAULT 0,
    
    UNIQUE(vault_id, normalized)
);

CREATE TABLE document_tags (
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tag_id TEXT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    source TEXT DEFAULT 'frontmatter',     -- frontmatter, inline (#tag в тексте)
    
    PRIMARY KEY(document_id, tag_id)
);

CREATE INDEX idx_tags_vault ON tags(vault_id);
CREATE INDEX idx_tags_normalized ON tags(vault_id, normalized);
CREATE INDEX idx_document_tags_tag ON document_tags(tag_id);
```

---

### 6. LINKS — Граф связей

```sql
CREATE TABLE links (
    id TEXT PRIMARY KEY,
    
    -- Участники связи
    source_doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    target_doc_id TEXT REFERENCES documents(id) ON DELETE SET NULL,
    target_raw TEXT NOT NULL,              -- оригинальный текст [[...]]
    
    -- Тип связи
    link_type TEXT NOT NULL,               -- wikilink, embed, property, external
    
    -- Контекст
    anchor_text TEXT,                      -- [[vshadrin|Сева]] → "Сева"
    context_type TEXT,                     -- frontmatter_field, heading, paragraph
    context_value TEXT,                    -- имя поля или заголовок секции
    position INTEGER,                      -- offset в документе
    
    CHECK(link_type IN ('wikilink', 'embed', 'property', 'external'))
);

CREATE INDEX idx_links_source ON links(source_doc_id);
CREATE INDEX idx_links_target ON links(target_doc_id);
CREATE INDEX idx_links_type ON links(link_type);
CREATE INDEX idx_links_target_raw ON links(target_raw);
```

**Link types:**
| Тип | Описание | Пример |
|-----|----------|--------|
| wikilink | Ссылка в тексте | `[[vshadrin]]` |
| embed | Встраивание | `![[diagram.png]]` |
| property | Ссылка в frontmatter | `participant: [[vshadrin]]` |
| external | Внешняя ссылка | `[link](https://...)` |

---

### 7. ENTITIES — Извлечённые сущности (NER)

```sql
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    vault_id TEXT NOT NULL REFERENCES vaults(id) ON DELETE CASCADE,
    
    -- Идентификация
    name TEXT NOT NULL,                    -- "Всеволод Шадрин"
    normalized_id TEXT,                    -- "vshadrin"
    entity_type TEXT NOT NULL,             -- person, project, org, tech, date
    
    -- Связь с каноническим документом (если есть)
    canonical_doc_id TEXT REFERENCES documents(id) ON DELETE SET NULL,
    
    -- Альтернативные написания
    aliases JSON DEFAULT '[]',             -- ["Сева", "Шадрин", "В.Шадрин"]
    
    -- Статистика
    mention_count INTEGER DEFAULT 0,
    
    UNIQUE(vault_id, normalized_id)
);

CREATE TABLE document_entities (
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    
    mention_count INTEGER DEFAULT 1,
    positions JSON,                        -- [{"start": 100, "end": 115, "text": "Шадрин"}]
    confidence REAL DEFAULT 1.0,           -- NER confidence score
    
    PRIMARY KEY(document_id, entity_id)
);

CREATE INDEX idx_entities_vault ON entities(vault_id);
CREATE INDEX idx_entities_type ON entities(vault_id, entity_type);
CREATE INDEX idx_entities_canonical ON entities(canonical_doc_id);
CREATE INDEX idx_document_entities_entity ON document_entities(entity_id);
```

---

### 8. EMBEDDING_CACHE — Кэш эмбеддингов

```sql
CREATE TABLE embedding_cache (
    content_hash TEXT PRIMARY KEY,         -- MD5(content)
    model_name TEXT NOT NULL,              -- "bge-m3"
    embedding BLOB NOT NULL,               -- numpy array as bytes
    embedding_dim INTEGER NOT NULL,        -- 1024
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cache_model ON embedding_cache(model_name);
```

**Использование:**
1. `hash = MD5(chunk_content)`
2. `SELECT embedding FROM embedding_cache WHERE content_hash = ? AND model_name = ?`
3. Cache hit → использовать, Cache miss → генерировать и сохранить

---

### 9. SEARCH_HISTORY — Аналитика поиска

```sql
CREATE TABLE search_history (
    id TEXT PRIMARY KEY,
    vault_id TEXT REFERENCES vaults(id),
    
    -- Запрос
    query TEXT NOT NULL,
    intent TEXT,                           -- document, chunk, graph, hybrid
    filters JSON,                          -- {"type": "person", "status": "active"}
    
    -- Результат
    results_count INTEGER,
    top_doc_ids JSON,                      -- ["doc_001", "doc_002", ...]
    
    -- Производительность
    latency_ms REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_vault ON search_history(vault_id);
CREATE INDEX idx_search_date ON search_history(created_at DESC);
```

---

## LanceDB Schema

### CHUNKS — Векторное хранилище

```python
import pyarrow as pa

chunks_schema = pa.schema([
    # Идентификация
    pa.field("id", pa.string()),
    pa.field("document_id", pa.string()),
    pa.field("vault_id", pa.string()),
    pa.field("chunk_index", pa.int32()),
    
    # Контент
    pa.field("content", pa.string()),
    pa.field("context", pa.string()),          # Contextual Retrieval prefix
    
    # Вектор
    pa.field("embedding", pa.list_(pa.float32(), 1024)),
    
    # Позиция в документе
    pa.field("start_offset", pa.int32()),
    pa.field("end_offset", pa.int32()),
    pa.field("heading", pa.string()),          # текущий заголовок секции
    
    # Денормализация для filtered search (из SQLite)
    pa.field("doc_type", pa.string()),
    pa.field("doc_id", pa.string()),
    pa.field("tags", pa.list_(pa.string())),
    
    # Временные метки для сортировки
    pa.field("file_modified_at", pa.timestamp("us")),
])
```

**Пример chunk с Contextual Retrieval:**

```json
{
  "id": "chunk_001_2",
  "document_id": "doc_001",
  "vault_id": "vault_001",
  "chunk_index": 2,
  "content": "## Текущие задачи\n\n1. Ревью архитектуры PSB\n2. Подготовка Q1 roadmap\n3. Найм senior разработчика",
  "context": "This chunk is from the profile document of Vsevolod Shadrin (vshadrin), a person in the Naumen CTO knowledge base. The document describes his role as Technical Lead. This section covers his current tasks and priorities.",
  "embedding": [0.023, -0.045, ...],
  "start_offset": 1250,
  "end_offset": 1456,
  "heading": "Текущие задачи",
  "doc_type": "person",
  "doc_id": "vshadrin",
  "tags": ["lead", "architecture"],
  "file_modified_at": "2025-01-08T10:30:00"
}
```

---

## Типичные запросы

### SQLite: Поиск по свойствам

**Найти все документы со статусом "active":**
```sql
SELECT d.* FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND p.key = 'status' 
  AND p.value_string = 'active';
```

**Найти все 1-1 с конкретным участником:**
```sql
SELECT d.* FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND d.doc_type = '1-1'
  AND p.key = 'participant'
  AND p.value_link_target = 'vshadrin'
ORDER BY d.file_modified_at DESC;
```

**Агрегация по свойству:**
```sql
SELECT p.value_string as status, COUNT(*) as count
FROM document_properties p
JOIN documents d ON p.document_id = d.id
WHERE d.vault_id = 'vault_001'
  AND d.doc_type = 'project'
  AND p.key = 'status'
GROUP BY p.value_string;
```

**Получить схему vault'а:**
```sql
SELECT key, value_type, is_list, allowed_values, doc_count
FROM property_schemas
WHERE vault_id = 'vault_001'
ORDER BY doc_count DESC;
```

### SQLite: Граф запросы

**Backlinks (кто ссылается на документ):**
```sql
SELECT d.*, l.link_type, l.anchor_text, l.context_type
FROM documents d
JOIN links l ON d.id = l.source_doc_id
WHERE l.target_doc_id = (
    SELECT id FROM documents WHERE vault_id = 'vault_001' AND doc_id = 'vshadrin'
);
```

**Orphans (документы без входящих ссылок):**
```sql
SELECT d.* FROM documents d
WHERE d.vault_id = 'vault_001'
  AND d.id NOT IN (SELECT DISTINCT target_doc_id FROM links WHERE target_doc_id IS NOT NULL);
```

**Документы с битыми ссылками:**
```sql
SELECT DISTINCT d.doc_id, d.title, l.target_raw
FROM documents d
JOIN links l ON d.id = l.source_doc_id
WHERE l.target_doc_id IS NULL;
```

### LanceDB: Векторный поиск

**Семантический поиск с фильтром:**
```python
table = lance_db.open_table("chunks")

results = (
    table.search(query_embedding)
    .where("vault_id = 'vault_001' AND doc_type = 'person'")
    .limit(10)
    .to_list()
)
```

**Hybrid search (vector + FTS):**
```python
results = (
    table.search(query_embedding, query_type="hybrid")
    .where("vault_id = 'vault_001'")
    .limit(10)
    .to_list()
)
```

---

## Миграция данных

### Парсинг frontmatter → DOCUMENT_PROPERTIES

```python
import yaml
from typing import Any

def parse_frontmatter_to_properties(
    document_id: str,
    frontmatter: dict[str, Any],
    schema_cache: dict[str, str]  # key → schema_id
) -> list[dict]:
    """Convert frontmatter dict to normalized property records."""
    
    properties = []
    
    for key, value in frontmatter.items():
        # Skip special fields stored in documents table
        if key in ('title', 'type', 'id'):
            continue
        
        schema_id = schema_cache.get(key)
        
        # Handle lists
        if isinstance(value, list):
            for idx, item in enumerate(value):
                properties.append(
                    _create_property_record(document_id, schema_id, key, item, idx)
                )
        else:
            properties.append(
                _create_property_record(document_id, schema_id, key, value, 0)
            )
    
    return properties


def _create_property_record(
    document_id: str,
    schema_id: str | None,
    key: str,
    value: Any,
    list_index: int
) -> dict:
    """Create a single property record with proper typing."""
    
    record = {
        "id": f"{document_id}_{key}_{list_index}",
        "document_id": document_id,
        "schema_id": schema_id,
        "key": key,
        "list_index": list_index,
        "value_string": None,
        "value_number": None,
        "value_date": None,
        "value_boolean": None,
        "value_link_target": None,
        "value_link_raw": None,
    }
    
    # Detect type and set appropriate field
    if isinstance(value, bool):
        record["value_type"] = "boolean"
        record["value_boolean"] = 1 if value else 0
    
    elif isinstance(value, (int, float)):
        record["value_type"] = "number"
        record["value_number"] = float(value)
    
    elif isinstance(value, str):
        # Check if it's a wikilink
        if value.startswith("[[") and value.endswith("]]"):
            record["value_type"] = "link"
            record["value_link_raw"] = value
            # Extract target: [[path/to/doc|alias]] → doc_id
            record["value_link_target"] = _extract_link_target(value)
        
        # Check if it's a date (YYYY-MM-DD)
        elif _is_date(value):
            record["value_type"] = "date"
            record["value_date"] = value
        
        else:
            record["value_type"] = "string"
            record["value_string"] = value
    
    else:
        record["value_type"] = "string"
        record["value_string"] = str(value)
    
    return record


def _extract_link_target(wikilink: str) -> str:
    """Extract doc_id from [[path/to/doc|alias]]."""
    inner = wikilink[2:-2]  # Remove [[ and ]]
    if "|" in inner:
        inner = inner.split("|")[0]
    # Get last path component without extension
    return inner.split("/")[-1].replace(".md", "")


def _is_date(value: str) -> bool:
    """Check if string is ISO date."""
    import re
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', value))
```

---

## Структура файлов

```
~/.obsidian-kb/
├── data/
│   ├── metadata.db              # SQLite: все таблицы кроме chunks
│   ├── vectors.lance/           # LanceDB: chunks с векторами
│   └── cache/
│       └── embeddings.db        # Отдельный SQLite для embedding cache
├── config.yaml                  # Глобальная конфигурация
└── logs/
    └── obsidian-kb.log
```

---

## Преимущества нормализованной схемы

| Аспект | JSON в документе | Нормализованная таблица |
|--------|------------------|------------------------|
| Поиск по полю | Медленный LIKE/JSON_EXTRACT | Быстрый индексированный |
| Агрегация | Сложная | Простой GROUP BY |
| Типизация | Нет | Строгая |
| Валидация | Нет | Через PROPERTY_SCHEMAS |
| Схема vault'а | Неизвестна | Автоматически собирается |
| Ссылки в frontmatter | Теряются | Связаны с LINKS |
