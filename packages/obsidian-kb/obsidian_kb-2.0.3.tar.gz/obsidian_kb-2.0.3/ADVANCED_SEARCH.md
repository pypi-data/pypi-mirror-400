# Расширенный поиск в obsidian-kb

## Обзор

obsidian-kb поддерживает расширенный поиск с фильтрами по тегам, датам, типам документов и связанным заметкам (wikilinks). Все фильтры можно комбинировать в одном запросе.

---

## Поиск по тегам

### Синтаксис

```
tags:tag1 tag2                    # AND (по умолчанию)
tags:tag1 OR tags:tag2            # OR оператор
tags:tag1 NOT tags:tag2           # NOT оператор (исключение)
tags:tag1,tag2,tag3               # Через запятые
tag:tag1                          # Альтернативный синтаксис
```

### Примеры

```bash
# Поиск документов с тегом "python"
uv run obsidian-kb search --vault tech-notes --query "tags:python"

# Поиск документов с тегами "python" И "async" (AND)
uv run obsidian-kb search --vault tech-notes --query "Python tags:python async"

# Поиск документов с тегом "python" ИЛИ "javascript" (OR)
uv run obsidian-kb search --vault tech-notes --query "tags:python OR tags:javascript"

# Поиск документов с тегом "python", но БЕЗ тега "deprecated" (NOT)
uv run obsidian-kb search --vault tech-notes --query "tags:python NOT tags:deprecated"

# Комбинация OR и NOT
uv run obsidian-kb search --vault tech-notes --query "tags:python OR tags:javascript NOT tags:deprecated"

# Поиск через запятые
uv run obsidian-kb search --vault tech-notes --query "tags:python,async,test"
```

### В MCP (Claude Desktop)

```python
# AND (по умолчанию)
search_vault("tech-notes", "Python tags:python async")

# OR оператор
search_vault("tech-notes", "tags:python OR tags:javascript")

# NOT оператор
search_vault("tech-notes", "tags:python NOT tags:deprecated")

# Комбинация
search_vault("tech-notes", "tags:python OR tags:javascript NOT tags:deprecated")
```

### Как это работает

- Фильтр `tags:python` находит все документы, у которых в массиве `tags` есть значение "python"
- Несколько тегов в одном фильтре объединяются через И (AND): `tags:python async` найдёт документы с обоими тегами
- Оператор `OR` позволяет найти документы с одним из тегов: `tags:python OR tags:javascript`
- Оператор `NOT` исключает документы с указанным тегом: `tags:python NOT tags:deprecated`
- Можно использовать несколько фильтров `tags:` в одном запросе — они объединяются

---

## Поиск по датам

### Синтаксис

```
created:YYYY-MM-DD          # Точная дата
created:>YYYY-MM-DD         # После даты
created:>=YYYY-MM-DD        # С даты и позже
created:<YYYY-MM-DD         # До даты
created:<=YYYY-MM-DD        # До даты включительно
modified:YYYY-MM-DD         # По дате изменения
modified:YYYY-MM-DD HH:MM:SS  # С указанием времени
```

### Примеры

```bash
# Документы созданные 1 января 2024
uv run obsidian-kb search --vault tech-notes --query "created:2024-01-01"

# Документы созданные после 1 января 2024
uv run obsidian-kb search --vault tech-notes --query "created:>2024-01-01"

# Документы изменённые в декабре 2024
uv run obsidian-kb search --vault tech-notes --query "modified:>=2024-12-01 modified:<=2024-12-31"

# С указанием времени
uv run obsidian-kb search --vault tech-notes --query "created:2024-01-01 10:30:00"
```

### В MCP (Claude Desktop)

```
search_vault("tech-notes", "created:>2024-01-01 modified:<2024-12-31")
```

### Как это работает

- Фильтры по датам работают с полями `created_at` и `modified_at` в базе данных
- Даты хранятся в ISO формате и сравниваются как строки
- Поддерживаются операторы: `=`, `>`, `<`, `>=`, `<=`

---

## Поиск по типам документов

### Синтаксис

```
type:тип_документа              # AND (по умолчанию)
type:тип1 OR type:тип2          # OR оператор
type:тип1 NOT type:тип2         # NOT оператор (исключение)
```

### Примеры

```bash
# Поиск протоколов
uv run obsidian-kb search --vault tech-notes --query "type:протокол"

# Поиск протоколов ИЛИ договоров (OR)
uv run obsidian-kb search --vault tech-notes --query "type:протокол OR type:договор"

# Поиск протоколов, но НЕ из архива (NOT)
uv run obsidian-kb search --vault tech-notes --query "type:протокол NOT type:архив"

# Поиск договоров
uv run obsidian-kb search --vault tech-notes --query "type:договор"

# Поиск решений
uv run obsidian-kb search --vault tech-notes --query "type:решение"
```

### В MCP (Claude Desktop)

```python
# Обычный поиск
search_vault("tech-notes", "type:протокол")

# OR оператор
search_vault("tech-notes", "type:протокол OR type:договор")

# NOT оператор
search_vault("tech-notes", "type:протокол NOT type:архив")
```

### Как это работает

- Тип документа извлекается из frontmatter: поле `type` или `document_type`
- **В схеме v4** типы документов хранятся в нормализованной таблице `document_properties` с ключом `"type"`
- Поиск выполняется через двухэтапный запрос:
  1. Поиск `document_id` в таблице `document_properties` по `property_key="type"` и `property_value`
  2. Фильтрация чанков по найденным `document_id`
- Оператор `OR` позволяет найти документы одного из типов
- Оператор `NOT` исключает документы указанного типа
- Тип должен быть указан в frontmatter файла:

```yaml
---
title: Протокол заседания
type: протокол
---
```

**Примечание:** В версии 0.2.0+ используется схема базы данных v4 с нормализованной структурой для лучшей производительности и масштабируемости.

---

## Поиск по связанным заметкам (wikilinks)

### Синтаксис

```
links:note-name                  # AND (по умолчанию)
links:note1 OR links:note2       # OR оператор
links:note1 NOT links:note2      # NOT оператор (исключение)
link:note-name                   # Альтернативный синтаксис
links:note1,note2,note3           # Через запятые
```

### Примеры

```bash
# Поиск заметок, которые ссылаются на "Python"
uv run obsidian-kb search --vault tech-notes --query "links:Python"

# Поиск заметок, которые ссылаются на "Python" ИЛИ "Flask" (OR)
uv run obsidian-kb search --vault tech-notes --query "links:Python OR links:Flask"

# Поиск заметок, которые ссылаются на "Python", но НЕ на "deprecated" (NOT)
uv run obsidian-kb search --vault tech-notes --query "links:Python NOT links:deprecated"

# Поиск заметок, которые ссылаются на несколько заметок (AND)
uv run obsidian-kb search --vault tech-notes --query "links:Python async"

# Поиск через запятые
uv run obsidian-kb search --vault tech-notes --query "links:Python,async,test"

# Комбинация с текстовым запросом
uv run obsidian-kb search --vault tech-notes --query "программирование links:Python"

# Комбинация с другими фильтрами
uv run obsidian-kb search --vault tech-notes --query "links:Python tags:python created:>2024-01-01"
```

### В MCP (Claude Desktop)

```python
# Только по связанным заметкам
search_vault("tech-notes", "links:Python")

# OR оператор
search_vault("tech-notes", "links:Python OR links:Flask")

# NOT оператор
search_vault("tech-notes", "links:Python NOT links:deprecated")

# С текстовым запросом
search_vault("tech-notes", "программирование links:Python")

# С другими фильтрами
search_vault("tech-notes", "links:Python tags:python created:>2024-01-01")
```

### Как это работает

- Фильтр `links:note-name` находит все документы, которые содержат wikilink `[[note-name]]`
- Wikilinks извлекаются из текста заметок при индексации
- Несколько links в одном фильтре объединяются через И (AND): `links:note1 note2` найдёт документы, которые ссылаются на обе заметки
- Оператор `OR` позволяет найти документы, которые ссылаются на один из указанных links
- Оператор `NOT` исключает документы, которые ссылаются на указанный link
- Можно использовать несколько фильтров `links:` в одном запросе — они объединяются
- Если указан только `links:` без текстового запроса и других фильтров, используется оптимизированный поиск по связанным заметкам

### Примеры использования

```bash
# Найти все заметки, которые ссылаются на заметку "Методы разработки"
uv run obsidian-kb search --vault tech-notes --query "links:Методы разработки"

# Найти заметки, которые ссылаются на "Python" И "async"
uv run obsidian-kb search --vault tech-notes --query "links:Python async"

# Найти заметки с тегом "python", которые ссылаются на "Flask"
uv run obsidian-kb search --vault tech-notes --query "tags:python links:Flask"
```

---

## Комбинирование фильтров

Все фильтры можно комбинировать в одном запросе, включая OR и NOT операторы:

### Примеры

```bash
# Текст + теги + дата + тип + links
uv run obsidian-kb search --vault tech-notes --query "Python tags:python async created:>2024-01-01 type:guide links:Flask"

# Только фильтры (без текстового запроса)
uv run obsidian-kb search --vault tech-notes --query "tags:python created:>2024-01-01 type:протокол links:Python"

# С OR оператором
uv run obsidian-kb search --vault tech-notes --query "tags:python OR tags:javascript type:протокол"

# С NOT оператором
uv run obsidian-kb search --vault tech-notes --query "tags:python NOT tags:deprecated type:документ"

# Комбинация OR и NOT
uv run obsidian-kb search --vault tech-notes --query "tags:python OR tags:javascript NOT tags:deprecated type:протокол OR type:договор"

# Несколько тегов, дат и links
uv run obsidian-kb search --vault tech-notes --query "tags:python,async created:>2024-01-01 modified:<2024-12-31 links:Python async"
```

### В MCP (Claude Desktop)

```python
# Обычная комбинация
search_vault("tech-notes", "Python tags:python async created:>2024-01-01 type:guide")

# С OR оператором
search_vault("tech-notes", "tags:python OR tags:javascript type:протокол")

# С NOT оператором
search_vault("tech-notes", "tags:python NOT tags:deprecated type:документ")

# Комбинация OR и NOT
search_vault("tech-notes", "tags:python OR tags:javascript NOT tags:deprecated type:протокол")
```

### Логика комбинирования

- Все фильтры одного типа объединяются через И (AND) по умолчанию
- Оператор `OR` позволяет объединить фильтры через ИЛИ
- Оператор `NOT` исключает документы с указанным фильтром
- Разные типы фильтров (tags, type, links, dates) всегда объединяются через AND
- Текстовый запрос выполняется через семантический/полнотекстовый поиск
- Фильтры применяются дополнительно к результатам поиска
- Если указан только `links:` без текста и других фильтров, используется оптимизированный поиск по связанным заметкам

---

## Использование в CLI

### Базовый синтаксис

```bash
uv run obsidian-kb search --vault <vault_name> --query "<запрос с фильтрами>"
```

### Опции

- `--vault` — имя vault'а (обязательно)
- `--query` — поисковый запрос с фильтрами (обязательно)
- `--limit` — максимум результатов (по умолчанию: 10)
- `--type` — тип поиска: `vector`, `fts`, `hybrid` (по умолчанию: `hybrid`)
- `--export` — путь для экспорта результатов
- `--format` — формат экспорта: `json`, `markdown`, `csv` (по умолчанию: `json`)

### Примеры

```bash
# Простой поиск
uv run obsidian-kb search --vault tech-notes --query "Python"

# С фильтрами
uv run obsidian-kb search --vault tech-notes --query "Python tags:python created:>2024-01-01"

# С экспортом
uv run obsidian-kb search --vault tech-notes --query "tags:python" --export results.json --format json
```

---

## Использование в MCP (Claude Desktop)

### `search_vault`

```python
# Обычный поиск
search_vault(
    vault_name="tech-notes",
    query="Python tags:python async created:>2024-01-01",
    limit=10,
    search_type="hybrid"
)

# С OR оператором
search_vault("tech-notes", "tags:python OR tags:javascript", limit=10)

# С NOT оператором
search_vault("tech-notes", "tags:python NOT tags:deprecated", limit=10)
```

### `search_multi_vault`

```python
search_multi_vault(
    vault_names=["tech-notes", "personal"],
    query="tags:python created:>2024-01-01",
    limit=5
)
```

### Автодополнение для Claude

Для удобства использования с Claude доступны инструменты автодополнения:

```python
# Получить список всех тегов в vault'е
list_tags("tech-notes")

# Получить список всех типов документов
list_doc_types("tech-notes")

# Получить список всех wikilinks
list_links("tech-notes")

# Получить справку по синтаксису поиска
search_help()
```

---

## Двухэтапные запросы (v4)

**Версия 0.2.0+** использует схему базы данных v4 с двухэтапными запросами для эффективной фильтрации по свойствам документов.

### Как это работает

Для фильтров по типам документов (`type:протокол`) система выполняет двухэтапный запрос:

**Этап 1: Фильтрация документов по свойствам**
```python
# Поиск document_id документов с типом "протокол"
doc_ids = await db_manager.get_documents_by_property(
    vault_name="vault",
    property_key="type",
    property_value="протокол"
)
# Возвращает: {"vault::file1.md", "vault::file2.md"}
```

**Этап 2: Поиск среди чанков отфильтрованных документов**
```python
# Выполняем поиск только среди чанков этих документов
results = await db_manager.vector_search(
    vault_name="vault",
    query_vector=query_embedding,
    limit=10,
    document_ids=doc_ids  # Фильтрация по document_id
)
```

### Преимущества двухэтапных запросов

1. **Эффективность** — фильтрация по индексированным свойствам вместо парсинга JSON
2. **Масштабируемость** — работает быстро даже с миллионами чанков
3. **Гибкость** — поддержка произвольных свойств из frontmatter без изменения схемы
4. **Производительность** — индексы на `property_key` и `property_value` в таблице `document_properties`

### Какие фильтры используют двухэтапные запросы

- `type:тип_документа` — поиск по типу документа
- Произвольные свойства из frontmatter (например, `author:Иванов`, `status:активен`)

### Какие фильтры используют одноэтапные запросы

- `tags:тег` — поиск по тегам (хранятся в таблице `chunks`)
- `links:заметка` — поиск по связанным заметкам (хранятся в таблице `chunks`)
- `created:дата`, `modified:дата` — поиск по датам (хранятся в таблице `documents`)

---

## Технические детали

### Парсинг запросов

Расширенные запросы парсятся модулем `query_parser.py`:

1. Извлекаются фильтры (теги, даты, типы, links)
2. Остальной текст используется как текстовый запрос
3. **В схеме v4** для фильтров по типам документов используется двухэтапный запрос:
   - Этап 1: Поиск `document_id` в таблице `document_properties`
   - Этап 2: Фильтрация чанков по найденным `document_id`
4. Строится SQL WHERE условие для LanceDB (для фильтров по тегам, links, датам)
5. Фильтры применяются к результатам поиска
6. Для поиска только по links используется оптимизированный метод `search_by_links()`

### Поддерживаемые операторы для дат

- `=` — равенство (по умолчанию)
- `>` — больше
- `<` — меньше
- `>=` — больше или равно
- `<=` — меньше или равно

### Форматы дат

- `YYYY-MM-DD` — дата
- `YYYY-MM-DD HH:MM:SS` — дата и время
- ISO формат: `2024-01-01T10:30:00`

### Ограничения

- Теги нормализуются (приводятся к lowercase) при индексации и поиске
- Даты должны быть в формате YYYY-MM-DD
- **В схеме v4** тип документа ищется в таблице `document_properties` через двухэтапный запрос
- Links нормализуются (приводятся к lowercase) при индексации и поиске
- OR и NOT операторы работают только для фильтров одного типа (tags, type, links)
- Разные типы фильтров всегда объединяются через AND
- FTS индекс создается автоматически при первом поиске, если его нет (версия 0.2.6+)

---

## Примеры использования

### Поиск протоколов за период

```bash
uv run obsidian-kb search --vault "ТСН Чистова 16 к 2" \
  --query "type:протокол created:>=2024-01-01 created:<=2024-12-31"
```

### Поиск документов с определёнными тегами

```bash
uv run obsidian-kb search --vault tech-notes \
  --query "tags:python async programming"
```

### Поиск недавно изменённых документов

```bash
uv run obsidian-kb search --vault tech-notes \
  --query "modified:>2024-12-01"
```

### Комплексный поиск

```bash
uv run obsidian-kb search --vault "Naumen CTO" \
  --query "технологии"
```

### Поиск по связанным заметкам

```bash
# Найти все заметки, которые ссылаются на "Python"
uv run obsidian-kb search --vault tech-notes \
  --query "links:Python"

# Найти заметки, которые ссылаются на "Python" и имеют тег "python"
uv run obsidian-kb search --vault tech-notes \
  --query "links:Python tags:python"
```

---

## Советы и рекомендации

1. **Используйте теги для категоризации** — это самый быстрый способ фильтрации
2. **Комбинируйте фильтры** — можно использовать несколько фильтров одновременно
3. **Типы документов** — полезны для структурированных vault'ов (протоколы, договоры, решения)
4. **Даты** — используйте для поиска документов за определённый период
5. **Связанные заметки (wikilinks)** — найдите все заметки, которые ссылаются на конкретную заметку
6. **Текстовый запрос + фильтры** — комбинируйте семантический поиск с фильтрами для лучших результатов
7. **Поиск по links** — особенно полезен для навигации по связанным заметкам и построения графа знаний

---

## Устранение неполадок

### Фильтры не работают

- Убедитесь, что vault проиндексирован: `uv run obsidian-kb list-vaults`
- Проверьте формат фильтров (теги без пробелов, даты в формате YYYY-MM-DD)
- Проверьте, что в документах есть соответствующие поля (теги в frontmatter, даты создания)

### Нет результатов при фильтрах

- Проверьте правильность написания тегов (чувствительны к регистру)
- Убедитесь, что даты указаны в правильном формате
- Проверьте, что тип документа указан в frontmatter файлов

### Ошибки парсинга

- Используйте кавычки для запросов с пробелами в терминале
- Экранируйте специальные символы если нужно
- Проверьте синтаксис фильтров

