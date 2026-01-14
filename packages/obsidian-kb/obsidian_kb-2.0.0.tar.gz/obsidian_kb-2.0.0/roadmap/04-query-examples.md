# Примеры SQL-запросов для DOCUMENT_PROPERTIES

## Базовые запросы

### Все документы со статусом "active"

```sql
SELECT d.doc_id, d.title, d.type
FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND p.property_key = 'status' 
  AND p.value_string = 'active';
```

### Задачи с приоритетом >= 2

```sql
SELECT d.doc_id, d.title, p.value_number as priority
FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND d.type = 'task'
  AND p.property_key = 'priority'
  AND p.value_number >= 2
ORDER BY p.value_number DESC;
```

### Документы с due date в ближайшие 7 дней

```sql
SELECT d.doc_id, d.title, p.value_date as due
FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND p.property_key = 'due'
  AND p.value_date BETWEEN date('now') AND date('now', '+7 days')
ORDER BY p.value_date;
```

---

## Запросы по ссылкам (link properties)

### Все подчинённые конкретного менеджера

```sql
SELECT d.doc_id, d.title
FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND p.property_key = 'manager'
  AND p.value_link_target = 'vshadrin';
```

### Построить org chart (все manager → подчинённые)

```sql
SELECT 
    p.value_link_target as manager_id,
    d.doc_id as employee_id,
    d.title as employee_name
FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND d.type = 'person'
  AND p.property_key = 'manager'
ORDER BY manager_id;
```

### 1-1 с участием конкретного человека (через list)

```sql
SELECT d.doc_id, d.title, d.file_modified_at
FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND d.type = '1-1'
  AND p.property_key = 'participants'
  AND p.value_list LIKE '%"vshadrin"%'
ORDER BY d.file_modified_at DESC;
```

---

## Агрегации

### Распределение по статусам

```sql
SELECT 
    p.value_string as status, 
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percent
FROM document_properties p
JOIN documents d ON p.document_id = d.id
WHERE d.vault_id = 'vault_001'
  AND p.property_key = 'status'
GROUP BY p.value_string
ORDER BY count DESC;
```

### Топ-10 менеджеров по количеству подчинённых

```sql
SELECT 
    p.value_link_target as manager_id,
    m.title as manager_name,
    COUNT(*) as direct_reports
FROM document_properties p
JOIN documents d ON p.document_id = d.id
LEFT JOIN documents m ON m.doc_id = p.value_link_target AND m.vault_id = d.vault_id
WHERE d.vault_id = 'vault_001'
  AND p.property_key = 'manager'
GROUP BY p.value_link_target
ORDER BY direct_reports DESC
LIMIT 10;
```

### Распределение по командам и ролям

```sql
SELECT 
    team.value_string as team,
    role.value_string as role,
    COUNT(*) as count
FROM documents d
LEFT JOIN document_properties team ON d.id = team.document_id AND team.property_key = 'team'
LEFT JOIN document_properties role ON d.id = role.document_id AND role.property_key = 'role'
WHERE d.vault_id = 'vault_001'
  AND d.type = 'person'
GROUP BY team.value_string, role.value_string
ORDER BY team, count DESC;
```

---

## Dataview-style запросы

### SELECT title, status, priority FROM type:task WHERE status != 'done' SORT BY priority

```sql
SELECT 
    d.title,
    MAX(CASE WHEN p.property_key = 'status' THEN p.value_string END) as status,
    MAX(CASE WHEN p.property_key = 'priority' THEN p.value_number END) as priority
FROM documents d
LEFT JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND d.type = 'task'
GROUP BY d.id
HAVING status IS NULL OR status != 'done'
ORDER BY priority ASC NULLS LAST;
```

### SELECT title, role, team FROM type:person WHERE team = 'Platform'

```sql
SELECT 
    d.title,
    MAX(CASE WHEN p.property_key = 'role' THEN p.value_string END) as role,
    MAX(CASE WHEN p.property_key = 'team' THEN p.value_string END) as team
FROM documents d
LEFT JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND d.type = 'person'
GROUP BY d.id
HAVING team = 'Platform';
```

### Все поля конкретного документа (pivot)

```sql
SELECT 
    d.doc_id,
    d.title,
    d.type,
    GROUP_CONCAT(p.property_key || ': ' || 
        COALESCE(p.value_string, 
                 CAST(p.value_number AS TEXT), 
                 p.value_date,
                 p.value_link_target,
                 p.value_list), '; ') as properties
FROM documents d
LEFT JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND d.doc_id = 'vshadrin'
GROUP BY d.id;
```

---

## Schema Discovery

### Все уникальные ключи свойств

```sql
SELECT DISTINCT property_key, value_type, COUNT(*) as usage
FROM document_properties p
JOIN documents d ON p.document_id = d.id
WHERE d.vault_id = 'vault_001'
GROUP BY property_key, value_type
ORDER BY usage DESC;
```

### Уникальные значения для enum-подобных свойств

```sql
-- Для status
SELECT DISTINCT value_string, COUNT(*) as count
FROM document_properties
WHERE property_key = 'status'
GROUP BY value_string
ORDER BY count DESC;

-- Для role
SELECT DISTINCT value_string, COUNT(*) as count
FROM document_properties
WHERE property_key = 'role'
GROUP BY value_string
ORDER BY count DESC;
```

### Найти свойства только для определённого типа документов

```sql
SELECT 
    p.property_key,
    p.value_type,
    COUNT(DISTINCT p.document_id) as usage
FROM document_properties p
JOIN documents d ON p.document_id = d.id
WHERE d.vault_id = 'vault_001'
  AND d.type = 'person'
GROUP BY p.property_key, p.value_type
ORDER BY usage DESC;
```

---

## Поиск проблем

### Документы без обязательного свойства

```sql
-- Люди без team
SELECT d.doc_id, d.title
FROM documents d
WHERE d.vault_id = 'vault_001'
  AND d.type = 'person'
  AND NOT EXISTS (
      SELECT 1 FROM document_properties p 
      WHERE p.document_id = d.id AND p.property_key = 'team'
  );
```

### Свойства с NULL значениями

```sql
SELECT d.doc_id, p.property_key
FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND p.value_string IS NULL 
  AND p.value_number IS NULL
  AND p.value_date IS NULL
  AND p.value_list IS NULL
  AND p.value_link_target IS NULL;
```

### Битые ссылки в link properties

```sql
SELECT 
    d.doc_id as source,
    p.property_key,
    p.value_link_target as broken_link
FROM documents d
JOIN document_properties p ON d.id = p.document_id
WHERE d.vault_id = 'vault_001'
  AND p.value_type = 'link'
  AND NOT EXISTS (
      SELECT 1 FROM documents target 
      WHERE target.vault_id = d.vault_id 
        AND target.doc_id = p.value_link_target
  );
```

---

## Миграция данных

### Из JSON frontmatter в EAV (string values)

```sql
INSERT INTO document_properties (id, document_id, property_key, value_type, value_string)
SELECT 
    'prop_' || hex(randomblob(8)),
    d.id,
    j.key,
    'string',
    j.value
FROM documents d, json_each(d.frontmatter_raw) j
WHERE d.vault_id = 'vault_001'
  AND j.key NOT IN ('id', 'title', 'type', 'tags')
  AND json_type(j.value) = 'text'
ON CONFLICT(document_id, property_key) DO UPDATE SET
  value_string = excluded.value_string;
```

### Из JSON frontmatter в EAV (number values)

```sql
INSERT INTO document_properties (id, document_id, property_key, value_type, value_number)
SELECT 
    'prop_' || hex(randomblob(8)),
    d.id,
    j.key,
    'number',
    CAST(j.value AS REAL)
FROM documents d, json_each(d.frontmatter_raw) j
WHERE d.vault_id = 'vault_001'
  AND j.key NOT IN ('id', 'title', 'type', 'tags')
  AND json_type(j.value) IN ('integer', 'real')
ON CONFLICT(document_id, property_key) DO UPDATE SET
  value_number = excluded.value_number;
```

### Пересчёт usage_count в property_schema

```sql
UPDATE property_schema
SET usage_count = (
    SELECT COUNT(DISTINCT p.document_id)
    FROM document_properties p
    JOIN documents d ON p.document_id = d.id
    WHERE d.vault_id = property_schema.vault_id
      AND p.property_key = property_schema.property_key
);
```
