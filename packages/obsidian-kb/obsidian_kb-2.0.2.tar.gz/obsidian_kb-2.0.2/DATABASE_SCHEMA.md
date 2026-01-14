# Структура векторной таблицы базы знаний

**Версия документа:** 4.0  
**Версия проекта:** 0.7.0
**Дата обновления:** 2026-01-06

## Обзор

База данных использует **LanceDB** для хранения индексированных документов из Obsidian vault'ов. Каждый vault хранится в **четырёх нормализованных таблицах** с именами:
- `vault_{vault_name}_documents` — метаданные документов
- `vault_{vault_name}_chunks` — векторные представления чанков
- `vault_{vault_name}_document_properties` — свойства документов (key-value)
- `vault_{vault_name}_metadata` — полный frontmatter в JSON

Это обеспечивает изоляцию данных между разными vault'ами и эффективную фильтрацию по свойствам документов.

**Текущая версия схемы:** **v4** (нормализованная схема с четырьмя таблицами)

---

## Схема таблиц v4

### Таблица 1: `vault_{vault_name}_documents`

Хранит метаданные документов (файлов).

| Колонка | Тип | Описание | Использование |
|---------|-----|----------|---------------|
| `document_id` | `string` | Уникальный ID документа<br>`{vault_name}::{file_path}` | Primary key, связь с другими таблицами |
| `vault_name` | `string` | Имя vault'а | Фильтрация по vault'у |
| `file_path` | `string` | Относительный путь к файлу | Навигация, группировка |
| `file_path_full` | `string` | Полный абсолютный путь | Доступ к файлу |
| `file_name` | `string` | Имя файла без расширения | Поиск по имени |
| `file_extension` | `string` | Расширение файла (.md, .pdf) | Фильтрация по типу |
| `content_type` | `string` | Тип контента (markdown, pdf, image) | Фильтрация по типу |
| `title` | `string` | Заголовок документа | Отображение, FTS |
| `created_at` | `string` (ISO datetime) | Дата создания | Фильтрация, сортировка |
| `modified_at` | `string` (ISO datetime) | Дата изменения | Инкрементальное индексирование |
| `file_size` | `int64` | Размер файла в байтах | Статистика |
| `chunk_count` | `int64` | Количество чанков документа | Статистика |

---

### Таблица 2: `vault_{vault_name}_chunks`

Хранит векторные представления и текст чанков.

| Колонка | Тип | Описание | Использование |
|---------|-----|----------|---------------|
| `chunk_id` | `string` | Уникальный ID чанка<br>`{vault_name}::{file_path}::{chunk_index}` | Primary key, дедупликация |
| `document_id` | `string` | ID документа (FK) | Связь с documents |
| `vault_name` | `string` | Имя vault'а | Фильтрация |
| `section` | `string` | Заголовок секции (H1-H3) | Контекст в результатах |
| `content` | `string` | Текст чанка (до 600 символов) | **Основной текст для поиска** - FTS индекс |
| `tags` | `list[string]` | Объединенные теги (обратная совместимость) | Фильтрация |
| `frontmatter_tags` | `list[string]` | Теги из frontmatter | Фильтрация по frontmatter тегам |
| `inline_tags` | `list[string]` | Inline теги из текста (`#tag`) | Фильтрация по inline тегам |
| `links` | `list[string]` | Массив wikilinks `[[note-name]]` | Поиск связанных заметок |
| `vector` | `list[float32]` | Векторное представление (1024 dim) | **Векторный поиск** |

---

### Таблица 3: `vault_{vault_name}_document_properties`

Хранит свойства документов в формате key-value для эффективной фильтрации.

| Колонка | Тип | Описание | Использование |
|---------|-----|----------|---------------|
| `document_id` | `string` | ID документа (FK) | Связь с documents |
| `vault_name` | `string` | Имя vault'а | Фильтрация |
| `property_key` | `string` | Ключ свойства (type, author, status, etc.) | Фильтрация по ключу |
| `property_value` | `string` | Нормализованное значение | Фильтрация по значению |
| `property_value_raw` | `string` | Оригинальное значение | Отображение, fuzzy matching |
| `property_type` | `string` | Тип значения (string, number, boolean, date) | Типизация |

**Примеры записей:**
- `document_id="vault::file.md"`, `property_key="type"`, `property_value="протокол"`
- `document_id="vault::file.md"`, `property_key="author"`, `property_value="john doe"`
- `document_id="vault::file.md"`, `property_key="status"`, `property_value="draft"`

---

### Таблица 4: `vault_{vault_name}_metadata`

Хранит полный frontmatter в JSON формате.

| Колонка | Тип | Описание | Использование |
|---------|-----|----------|---------------|
| `document_id` | `string` | ID документа (FK) | Связь с documents |
| `vault_name` | `string` | Имя vault'а | Фильтрация |
| `metadata_json` | `string` (JSON) | Сериализованный frontmatter | Расширенные метаданные |
| `metadata_hash` | `string` | SHA-256 хеш метаданных | Дедупликация, проверка изменений |

---

## Двухэтапные запросы (v4)

В v4 используется **двухэтапный подход** для эффективной фильтрации по свойствам документов:

### Этап 1: Фильтрация документов по свойствам

```python
# Получаем document_ids документов с типом "протокол"
doc_ids = await db_manager.get_documents_by_property(
    vault_name="vault",
    property_key="type",
    property_value="протокол"
)
# Возвращает: {"vault::file1.md", "vault::file2.md"}
```

### Этап 2: Поиск среди чанков отфильтрованных документов

```python
# Выполняем поиск только среди чанков этих документов
results = await db_manager.vector_search(
    vault_name="vault",
    query_vector=query_embedding,
    limit=10,
    document_ids=doc_ids  # Фильтрация по document_ids
)
```

### Преимущества двухэтапных запросов

1. **Эффективность** — фильтрация по индексированным свойствам вместо парсинга JSON
2. **Масштабируемость** — работает быстро даже с миллионами чанков
3. **Гибкость** — поддержка произвольных свойств без изменения схемы
4. **Производительность** — индексы на `property_key` и `property_value`

---

## Детальное описание колонок

### `document_id` - Уникальный идентификатор документа

**Формат:** `{vault_name}::{file_path}`

**Пример:** `my-vault::notes/python-guide.md`

**Назначение:**
- Primary key для таблицы `documents`
- Foreign key в таблицах `chunks`, `document_properties`, `metadata`
- Связь между нормализованными таблицами

---

### `chunk_id` - Уникальный идентификатор чанка

**Формат:** `{vault_name}::{file_path}::{chunk_index}`

**Пример:** `my-vault::notes/python-guide.md::0`

**Назначение:**
- Primary key для таблицы `chunks`
- Дедупликация результатов поиска
- Отслеживание изменений файлов

---

### `property_key` и `property_value` - Свойства документов

**Назначение:**
- Быстрая фильтрация по произвольным свойствам из frontmatter
- Индексация для эффективного поиска
- Нормализация значений для консистентности

**Примеры свойств:**
- `type` → `"протокол"`, `"договор"`, `"проект"`
- `author` → `"john doe"`, `"иван иванов"`
- `status` → `"draft"`, `"published"`, `"archived"`
- `priority` → `"low"`, `"medium"`, `"high"`
- `project` → `"api design"`, `"backend"`

---

## Индексы для оптимизации поиска

### 1. Векторный индекс (IVF-PQ) на таблице `chunks`

**Условие создания:** При количестве записей ≥ 10,000

**Параметры:**
- Метрика: `cosine` (косинусное расстояние)
- Партиции: 256
- Подвекторы: 16

**Код:**
```python
chunks_table.create_index(
    metric="cosine",
    num_partitions=256,
    num_sub_vectors=16,
)
```

---

### 2. FTS индекс (BM25) на таблице `chunks`

**Поля:** `content`, `title` (из таблицы `documents`)

**Алгоритм:** BM25 (Best Matching 25)

**Код:**
```python
chunks_table.create_fts_index("content", replace=True)
```

---

### 3. Индексы на таблице `document_properties`

**Индексы:**
- `property_key` — для быстрого поиска по типу свойства
- `property_value` — для быстрого поиска по значению
- Композитный индекс `(property_key, property_value)` — для точного поиска

**Использование:**
```python
# Быстрый поиск документов с типом "протокол"
properties_table.search().where(
    "property_key = 'type' AND property_value = 'протокол'"
)
```

---

## Типы поиска (v4)

### 1. Векторный поиск с фильтрацией по document_ids

```python
# Двухэтапный запрос
doc_ids = await db_manager.get_documents_by_property(
    vault_name="vault",
    property_key="type",
    property_value="протокол"
)

results = await db_manager.vector_search(
    vault_name="vault",
    query_vector=query_embedding,
    limit=10,
    document_ids=doc_ids  # Фильтрация по document_ids
)
```

---

### 2. Полнотекстовый поиск с фильтрацией по document_ids

```python
results = await db_manager.fts_search(
    vault_name="vault",
    query="Python async",
    limit=10,
    document_ids=doc_ids  # Опционально
)
```

---

### 3. Гибридный поиск с фильтрацией по document_ids

```python
results = await db_manager.hybrid_search(
    vault_name="vault",
    query_vector=query_embedding,
    query_text="Python async",
    limit=10,
    document_ids=doc_ids  # Опционально
)
```

---

## Фильтрация результатов (v4)

### Поддерживаемые фильтры

1. **По тегам (в таблице chunks):**
   ```python
   where = "array_contains(frontmatter_tags, 'python')"
   ```

2. **По типу документа (двухэтапный запрос):**
   ```python
   # Этап 1: Получаем document_ids
   doc_ids = await db_manager.get_documents_by_property(
       vault_name="vault",
       property_key="type",
       property_value="протокол"
   )
   # Этап 2: Поиск с фильтрацией
   results = await db_manager.vector_search(
       vault_name="vault",
       query_vector=query_embedding,
       document_ids=doc_ids
   )
   ```

3. **По датам (в таблице documents):**
   ```python
   # Фильтрация через WHERE на chunks (с обогащением из documents)
   where = "created_at >= '2024-01-01'"  # Применяется к chunks
   ```

4. **Комбинированные фильтры:**
   ```python
   # Комбинация двухэтапного запроса и WHERE фильтров
   doc_ids = await db_manager.get_documents_by_property(...)
   results = await db_manager.vector_search(
       vault_name="vault",
       query_vector=query_embedding,
       where="array_contains(frontmatter_tags, 'python')",
       document_ids=doc_ids
   )
   ```

---

## Новые методы API (v4)

### `get_documents_by_property()`

Получение `document_id` документов с указанным свойством.

```python
doc_ids = await db_manager.get_documents_by_property(
    vault_name="vault",
    property_key="type",
    property_value="протокол"
)
```

**Параметры:**
- `property_key` — ключ свойства (type, author, status, etc.)
- `property_value` — точное значение (опционально)
- `property_value_pattern` — паттерн для поиска (LIKE, опционально)

**Возвращает:** `set[str]` — множество `document_id`

---

### `get_document_properties()`

Получение всех свойств документа.

```python
properties = await db_manager.get_document_properties(
    vault_name="vault",
    document_id="vault::file.md"
)
# Возвращает: {"type": "протокол", "author": "john doe", "status": "draft"}
```

**Возвращает:** `dict[str, str]` — словарь `{property_key: property_value}`

---

### `get_document_info()`

Получение метаданных документа.

```python
doc_info = await db_manager.get_document_info(
    vault_name="vault",
    document_id="vault::file.md"
)
# Возвращает: DocumentInfo с полями title, file_path, created_at, etc.
```

**Возвращает:** `DocumentInfo | None`

---

## Примеры использования схемы v4

### Пример 1: Поиск протоколов за последний месяц (двухэтапный запрос)

```python
from datetime import datetime, timedelta

# Этап 1: Получаем document_ids протоколов
doc_ids = await db_manager.get_documents_by_property(
    vault_name="vault",
    property_key="type",
    property_value="протокол"
)

# Этап 2: Фильтруем по дате и выполняем поиск
month_ago = (datetime.now() - timedelta(days=30)).isoformat()
results = await db_manager.hybrid_search(
    vault_name="vault",
    query_vector=query_embedding,
    query_text="заседание",
    where=f"created_at >= '{month_ago}'",  # Фильтр по дате
    document_ids=doc_ids,  # Фильтр по типу документа
    limit=20
)
```

---

### Пример 2: Поиск документов конкретного автора

```python
# Этап 1: Получаем document_ids документов автора
doc_ids = await db_manager.get_documents_by_property(
    vault_name="vault",
    property_key="author",
    property_value="john doe"
)

# Этап 2: Выполняем поиск
results = await db_manager.vector_search(
    vault_name="vault",
    query_vector=query_embedding,
    document_ids=doc_ids,
    limit=10
)
```

---

### Пример 3: Комбинированная фильтрация (тип + теги)

```python
# Этап 1: Фильтрация по типу документа
doc_ids = await db_manager.get_documents_by_property(
    vault_name="vault",
    property_key="type",
    property_value="проект"
)

# Этап 2: Поиск с фильтром по тегам
results = await db_manager.vector_search(
    vault_name="vault",
    query_vector=query_embedding,
    where="array_contains(frontmatter_tags, 'python') AND array_contains(frontmatter_tags, 'async')",
    document_ids=doc_ids,
    limit=10
)
```

---

## Версии схемы

### История версий

#### v1-v2 (устарели)
Базовые схемы с минимальным набором полей.

#### v3 (устарела)
Денормализованная схема с полями `author`, `status`, `priority`, `project` в одной таблице.

**Проблемы v3:**
- Дублирование данных (свойства повторяются в каждом чанке)
- Ограниченный набор свойств (только 4 предопределённых)
- Неэффективная фильтрация при большом количестве чанков

#### v4 (текущая версия)

**Нормализованная схема с четырьмя таблицами:**

1. **`documents`** — метаданные документов
2. **`chunks`** — векторные представления и текст чанков
3. **`document_properties`** — свойства документов (key-value)
4. **`metadata`** — полный frontmatter в JSON

**Преимущества v4:**
- ✅ **Нормализация** — нет дублирования данных
- ✅ **Гибкость** — поддержка произвольных свойств без изменения схемы
- ✅ **Эффективность** — двухэтапные запросы для быстрой фильтрации
- ✅ **Масштабируемость** — работает быстро даже с миллионами чанков
- ✅ **Индексация** — индексы на свойства для быстрого поиска

**Миграция с v3 на v4:**
- Старые таблицы v3 удаляются автоматически
- Требуется переиндексация vault'а командой `obsidian-kb reindex --vault <name>`
- Данные не мигрируются автоматически (переиндексация создаёт новую структуру)

---

## Производительность

### Размер таблиц

**Оценка размера одной записи:**

**Таблица `documents`:**
- Метаданные: ~500 bytes
- **Итого:** ~500 bytes на документ

**Таблица `chunks`:**
- Вектор (1024 float32): ~4 KB
- Метаданные: ~1-2 KB
- **Итого:** ~5-6 KB на чанк

**Таблица `document_properties`:**
- Метаданные: ~200 bytes
- **Итого:** ~200 bytes на свойство

**Для vault с 1,000 документов и 10,000 чанков:**
- `documents`: ~500 KB
- `chunks`: ~50-60 MB
- `document_properties`: ~200 KB (при ~10 свойств на документ)
- **Итого:** ~51-61 MB

---

### Скорость поиска

**Векторный поиск (без индекса):**
- 1K чанков: ~10-50 ms
- 10K чанков: ~100-500 ms
- 100K чанков: ~1-5 seconds

**Векторный поиск (с IVF-PQ индексом):**
- 10K+ чанков: ~50-200 ms (ускорение в 5-10 раз)

**Двухэтапный запрос:**
- Фильтрация по свойствам: ~1-10 ms (индексированная таблица `properties`)
- Поиск среди отфильтрованных чанков: зависит от количества `document_ids`
- **Итого:** ~10-100 ms для типичного запроса

**FTS поиск:**
- Любой размер: ~10-100 ms (очень быстрый)

**Гибридный поиск:**
- Зависит от обоих типов поиска
- Обычно: ~100-300 ms для 10K чанков

---

## Заключение

Схема v4 спроектирована для эффективного:

1. **Семантического поиска** через векторные embeddings
2. **Полнотекстового поиска** через FTS индексы
3. **Фильтрации по свойствам** через двухэтапные запросы
4. **Навигации** по связанным заметкам
5. **Группировки** результатов по файлам
6. **Инкрементального обновления** индекса
7. **Масштабируемости** для больших vault'ов

Нормализованная структура обеспечивает гибкость и производительность, необходимые для работы с большими базами знаний.
