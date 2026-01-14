# obsidian-kb Database Schema v2.1

## Изменения относительно v2.0

**Добавлено:**
- `DOCUMENT_PROPERTIES` — EAV-таблица для свойств frontmatter
- `PROPERTY_SCHEMA` — схема свойств vault'а с типизацией
- Убран `frontmatter JSON` из DOCUMENTS, заменён на `frontmatter_raw` (backup)

**Преимущества:**
- Быстрые запросы: `WHERE key='status' AND value_string='active'`
- Типизированные значения (string, number, date, list, link)
- Автоматическое обнаружение схемы vault'а
- Агрегации: `GROUP BY key, value_string`

---

## Архитектура хранения

```
┌─────────────────────────────────────────────────────────────┐
│                        SQLite                               │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │   VAULTS    │  │    DOCUMENTS     │  │    LINKS      │  │
│  └─────────────┘  └──────────────────┘  └───────────────┘  │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │    TAGS     │  │DOCUMENT_PROPERTIES│ │PROPERTY_SCHEMA│  │
│  └─────────────┘  └──────────────────┘  └───────────────┘  │
│  ┌─────────────┐  ┌──────────────────┐                     │
│  │  ENTITIES   │  │ EMBEDDING_CACHE  │                     │
│  └─────────────┘  └──────────────────┘                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        LanceDB                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                     CHUNKS                           │   │
│  │   id | document_id | content | embedding | metadata  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Таблицы

### 1. DOCUMENT_PROPERTIES — Свойства документов (EAV)

```sql
CREATE TABLE document_properties (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    property_key TEXT NOT NULL,           -- "role", "status", "priority"
    value_type TEXT NOT NULL,             -- "string", "number", "date", "list", "link"
    
    -- Типизированные значения (только одно заполнено)
    value_string TEXT,                    -- "Lead Developer"
    value_number REAL,                    -- 42.5
    value_date DATE,                      -- 2025-01-08
    value_list JSON,                      -- ["tag1", "tag2"]
    value_link_target TEXT,               -- "vshadrin" (doc_id)
    
    -- Для полнотекстового поиска
    value_text_search TEXT,               -- normalized для FTS
    
    UNIQUE(document_id, property_key)
);

-- Индексы для быстрых запросов
CREATE INDEX idx_props_key ON document_properties(property_key);
CREATE INDEX idx_props_key_string ON document_properties(property_key, value_string);
CREATE INDEX idx_props_key_number ON document_properties(property_key, value_number);
CREATE INDEX idx_props_key_date ON document_properties(property_key, value_date);
CREATE INDEX idx_props_link ON document_properties(value_link_target);

-- FTS индекс для текстового поиска по значениям
CREATE VIRTUAL TABLE document_properties_fts USING fts5(
    property_key, value_text_search, 
    content='document_properties', 
    content_rowid='rowid'
);
```

**Value Types:**

| Type | Поле | Пример frontmatter | Значение в БД |
|------|------|---------------------|---------------|
| `string` | `value_string` | `role: Lead Developer` | `"Lead Developer"` |
| `number` | `value_number` | `priority: 1` | `1.0` |
| `date` | `value_date` | `due: 2025-01-15` | `2025-01-15` |
| `list` | `value_list` | `skills: [Python, SQL]` | `["Python", "SQL"]` |
| `link` | `value_link_target` | `manager: "[[vshadrin]]"` | `"vshadrin"` |

**Примеры данных:**

| id | document_id | property_key | value_type | value_string | value_number | value_date | value_list | value_link_target |
|----|-------------|--------------|------------|--------------|--------------|------------|------------|-------------------|
| `prop_001` | `doc_001` | `role` | `string` | Lead Developer | NULL | NULL | NULL | NULL |
| `prop_002` | `doc_001` | `team` | `string` | Platform | NULL | NULL | NULL | NULL |
| `prop_003` | `doc_001` | `manager` | `link` | NULL | NULL | NULL | NULL | `amuratov` |
| `prop_004` | `doc_002` | `status` | `string` | active | NULL | NULL | NULL | NULL |
| `prop_005` | `doc_002` | `priority` | `number` | NULL | 1 | NULL | NULL | NULL |
| `prop_006` | `doc_002` | `start_date` | `date` | NULL | NULL | 2024-06-01 | NULL | NULL |
| `prop_007` | `doc_003` | `participants` | `list` | NULL | NULL | NULL | `["vshadrin","amuratov"]` | NULL |

---

### 2. PROPERTY_SCHEMA — Схема свойств vault'а

```sql
CREATE TABLE property_schema (
    id TEXT PRIMARY KEY,
    vault_id TEXT NOT NULL REFERENCES vaults(id),
    property_key TEXT NOT NULL,           -- "role", "status"
    value_type TEXT NOT NULL,             -- detected or configured
    allowed_values JSON,                  -- ["active", "done", "blocked"] для enum
    usage_count INT DEFAULT 0,            -- сколько документов используют
    sample_values JSON,                   -- ["Lead", "Senior", "Junior"] — примеры
    is_indexed BOOLEAN DEFAULT FALSE,     -- создан ли индекс
    is_required BOOLEAN DEFAULT FALSE,    -- обязательное поле
    description TEXT,                     -- описание для UI
    
    UNIQUE(vault_id, property_key)
);

CREATE INDEX idx_schema_vault ON property_schema(vault_id);
```

**Примеры данных (auto-discovered):**

| vault_id | property_key | value_type | allowed_values | usage_count | sample_values |
|----------|--------------|------------|----------------|-------------|---------------|
| `vault_001` | `type` | `string` | `["person","project","1-1","adr","meeting"]` | 847 | NULL |
| `vault_001` | `status` | `string` | `["active","done","blocked","pending"]` | 234 | NULL |
| `vault_001` | `role` | `string` | NULL | 52 | `["Lead","Senior","Manager"]` |
| `vault_001` | `priority` | `number` | NULL | 89 | `[1, 2, 3]` |
| `vault_001` | `due` | `date` | NULL | 156 | NULL |
| `vault_001` | `participants` | `list` | NULL | 67 | NULL |
| `vault_001` | `manager` | `link` | NULL | 48 | NULL |

---

### 3. DOCUMENTS — Обновлённая таблица

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    vault_id TEXT NOT NULL REFERENCES vaults(id),
    path TEXT NOT NULL,                   -- относительный путь
    doc_id TEXT,                          -- семантический ID
    title TEXT,
    type TEXT,                            -- из frontmatter (денормализация)
    content_hash TEXT NOT NULL,           -- MD5 для change detection
    frontmatter_raw JSON,                 -- backup оригинального YAML
    content TEXT,                         -- raw markdown (опционально)
    file_created_at TIMESTAMP,
    file_modified_at TIMESTAMP,
    indexed_at TIMESTAMP,
    
    UNIQUE(vault_id, path)
);
```

**Примечание:** `type` остаётся в DOCUMENTS как денормализация — это самое частое поле для фильтрации.

---

## Типичные запросы

### Простые запросы по свойствам

```sql
-- Все документы со статусом "active"
SELECT d.* FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE p.property_key = 'status' AND p.value_string = 'active';

-- Задачи с приоритетом >= 2
SELECT d.* FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.type = 'task' 
  AND p.property_key = 'priority' 
  AND p.value_number >= 2;

-- Документы с due date в следующие 7 дней
SELECT d.* FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE p.property_key = 'due' 
  AND p.value_date BETWEEN date('now') AND date('now', '+7 days');
```

### Запросы по ссылкам в frontmatter

```sql
-- Все документы, где manager = vshadrin
SELECT d.* FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE p.property_key = 'manager' AND p.value_link_target = 'vshadrin';

-- Все 1-1 с участием конкретного человека (через list)
SELECT d.* FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.type = '1-1' 
  AND p.property_key = 'participants'
  AND json_each.value = 'vshadrin'
JOIN json_each(p.value_list);
```

### Агрегации

```sql
-- Распределение документов по статусам
SELECT p.value_string as status, COUNT(*) as count
FROM document_properties p
WHERE p.property_key = 'status'
GROUP BY p.value_string
ORDER BY count DESC;

-- Топ-10 людей по количеству упоминаний в manager
SELECT p.value_link_target as manager, COUNT(*) as reports
FROM document_properties p
WHERE p.property_key = 'manager'
GROUP BY p.value_link_target
ORDER BY reports DESC
LIMIT 10;

-- Все уникальные значения свойства role
SELECT DISTINCT p.value_string 
FROM document_properties p 
WHERE p.property_key = 'role';
```

### Dataview-style запросы

```sql
-- SELECT title, status, priority FROM type:task WHERE status != 'done' SORT BY priority
SELECT 
    d.title,
    MAX(CASE WHEN p.property_key = 'status' THEN p.value_string END) as status,
    MAX(CASE WHEN p.property_key = 'priority' THEN p.value_number END) as priority
FROM documents d
LEFT JOIN document_properties p ON d.id = p.document_id
WHERE d.type = 'task'
GROUP BY d.id
HAVING status != 'done' OR status IS NULL
ORDER BY priority ASC;
```

### Обнаружение схемы vault'а

```sql
-- Автоматическое построение PROPERTY_SCHEMA
INSERT INTO property_schema (id, vault_id, property_key, value_type, usage_count, sample_values)
SELECT 
    'schema_' || hex(randomblob(8)),
    d.vault_id,
    p.property_key,
    p.value_type,
    COUNT(DISTINCT p.document_id) as usage_count,
    json_group_array(DISTINCT p.value_string) as sample_values
FROM document_properties p
JOIN documents d ON p.document_id = d.id
WHERE d.vault_id = ?
GROUP BY d.vault_id, p.property_key, p.value_type;
```

---

## Парсинг frontmatter → DOCUMENT_PROPERTIES

```python
from typing import Any
import re
from datetime import date
import uuid

def parse_frontmatter_to_properties(
    document_id: str, 
    frontmatter: dict[str, Any]
) -> list[dict]:
    """Convert frontmatter dict to DOCUMENT_PROPERTIES rows."""
    properties = []
    
    for key, value in frontmatter.items():
        if key in ('id', 'title', 'type', 'tags'):  # Skip special fields
            continue
            
        prop = {
            'id': f'prop_{uuid.uuid4().hex[:12]}',
            'document_id': document_id,
            'property_key': key,
            'value_string': None,
            'value_number': None,
            'value_date': None,
            'value_list': None,
            'value_link_target': None,
            'value_text_search': None,
        }
        
        # Detect type and fill appropriate field
        if isinstance(value, bool):
            prop['value_type'] = 'string'
            prop['value_string'] = 'true' if value else 'false'
            
        elif isinstance(value, (int, float)):
            prop['value_type'] = 'number'
            prop['value_number'] = float(value)
            
        elif isinstance(value, list):
            prop['value_type'] = 'list'
            prop['value_list'] = value
            prop['value_text_search'] = ' '.join(str(v) for v in value)
            
        elif isinstance(value, str):
            # Check if it's a wikilink: [[doc_id]] or [[doc_id|alias]]
            link_match = re.match(r'^\[\[([^\]|]+)(?:\|[^\]]+)?\]\]$', value)
            if link_match:
                prop['value_type'] = 'link'
                prop['value_link_target'] = link_match.group(1)
            # Check if it's a date: YYYY-MM-DD
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                prop['value_type'] = 'date'
                prop['value_date'] = value
            else:
                prop['value_type'] = 'string'
                prop['value_string'] = value
                prop['value_text_search'] = value.lower()
        else:
            # Fallback: convert to string
            prop['value_type'] = 'string'
            prop['value_string'] = str(value)
            
        properties.append(prop)
    
    return properties


# Example usage
frontmatter = {
    'type': 'person',
    'title': 'Всеволод Шадрин',
    'role': 'Lead Developer',
    'team': 'Platform',
    'manager': '[[amuratov]]',
    'joined': '2020-03-15',
    'skills': ['Python', 'SQL', 'Architecture'],
    'level': 3,
    'active': True
}

props = parse_frontmatter_to_properties('doc_001', frontmatter)
# Returns 6 properties (type, title excluded)
```

---

## Индексация

### Рекомендуемые индексы

```sql
-- Основные индексы (создаются автоматически)
CREATE INDEX idx_props_key ON document_properties(property_key);
CREATE INDEX idx_props_key_string ON document_properties(property_key, value_string);
CREATE INDEX idx_props_key_number ON document_properties(property_key, value_number);
CREATE INDEX idx_props_key_date ON document_properties(property_key, value_date);
CREATE INDEX idx_props_link ON document_properties(value_link_target);

-- Составной индекс для частых запросов
CREATE INDEX idx_props_doc_key ON document_properties(document_id, property_key);

-- Частичные индексы для популярных свойств
CREATE INDEX idx_props_status ON document_properties(value_string) 
    WHERE property_key = 'status';
CREATE INDEX idx_props_priority ON document_properties(value_number) 
    WHERE property_key = 'priority';
```

### Автоматическое создание индексов

```sql
-- Создать индекс для свойства с usage_count > 50
UPDATE property_schema SET is_indexed = TRUE 
WHERE usage_count > 50 AND is_indexed = FALSE;

-- Затем создать соответствующие индексы
```

---

## Миграция данных

```sql
-- Из старой схемы (frontmatter JSON) в новую
INSERT INTO document_properties (id, document_id, property_key, value_type, value_string)
SELECT 
    'prop_' || hex(randomblob(8)),
    d.id,
    j.key,
    'string',
    j.value
FROM documents d, json_each(d.frontmatter) j
WHERE j.key NOT IN ('id', 'title', 'type', 'tags')
  AND json_type(j.value) = 'text';

-- Аналогично для numbers, arrays, etc.
```

---

## Сравнение с JSON-подходом

| Критерий | JSON в DOCUMENTS | DOCUMENT_PROPERTIES |
|----------|------------------|---------------------|
| Запрос по ключу | `json_extract(frontmatter, '$.status')` — медленно | `WHERE key='status'` — быстро |
| Индексы | Сложные expression indexes | Обычные B-tree |
| Типизация | Нет | Да (string/number/date) |
| Агрегации | Сложные subqueries | Простой GROUP BY |
| Schema discovery | Парсить JSON | SELECT DISTINCT key |
| Хранение | Компактнее | ~20% overhead |
| Обновление одного поля | Перезаписать весь JSON | UPDATE одной строки |

**Вывод:** Для vault'а с 1000+ документов и частыми запросами по свойствам, EAV-подход значительно эффективнее.
