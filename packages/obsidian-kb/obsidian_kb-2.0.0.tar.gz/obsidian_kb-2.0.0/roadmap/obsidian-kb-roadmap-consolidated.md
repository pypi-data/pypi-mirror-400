# obsidian-kb Roadmap v2.0

## Стратегия развития

```
═══════════════════════════════════════════════════════════════════════════════
                            2025 ROADMAP
═══════════════════════════════════════════════════════════════════════════════

  Q1 2025                    Q2 2025                    Q3 2025
  ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
  │  RELEASE 2.0    │        │  RELEASE 2.1    │        │  RELEASE 2.2    │
  │  Storage Layer  │───────▶│  Search Quality │───────▶│  Intelligence   │
  │                 │        │                 │        │                 │
  │ • SQLite для    │        │ • BGE-M3        │        │ • Contextual    │
  │   метаданных    │        │   embeddings    │        │   Retrieval     │
  │ • Нормализация  │        │ • Graph queries │        │ • Query         │
  │   frontmatter   │        │ • Entity NER    │        │   rewriting     │
  │ • Embedding     │        │ • Hybrid        │        │ • Semantic      │
  │   cache         │        │   reranking     │        │   cache         │
  │ • Incremental   │        │                 │        │                 │
  │   indexing      │        │                 │        │                 │
  └─────────────────┘        └─────────────────┘        └─────────────────┘
        4-6 недель                 4-6 недель                 6-8 недель
        
═══════════════════════════════════════════════════════════════════════════════
```

---

# Release 2.0 — "Storage Layer"

## Цель

Миграция на гибридную архитектуру **SQLite + LanceDB** для:
- Ускорения поиска по метаданным (свойства, теги, связи)
- Включения инкрементальной индексации
- Кэширования embeddings

## Целевые метрики

| Метрика | v1.0 | v2.0 Target | Улучшение |
|---------|------|-------------|-----------|
| Полная индексация 1000 файлов | ~5 мин | ~2 мин | 2.5x |
| Инкрементальная индексация (10 файлов) | ~5 мин | ~5 сек | 60x |
| Поиск по свойству `status=active` | ~500ms | ~10ms | 50x |
| Агрегация по полю | ~1s | ~20ms | 50x |
| Повторная векторизация unchanged | 100% | 0% | ∞ |

## Архитектура

```
┌────────────────────────────────────────────────────────────────────────┐
│                              STORAGE v2.0                               │
├────────────────────────────────────┬───────────────────────────────────┤
│            SQLite                  │           LanceDB                  │
│   (metadata, graph, cache)         │      (vectors, FTS)               │
├────────────────────────────────────┼───────────────────────────────────┤
│ • vaults                           │ • chunks                          │
│ • documents                        │   - id, document_id               │
│ • document_properties ←── NEW      │   - content, context              │
│ • property_schemas    ←── NEW      │   - embedding (float32[1024])     │
│ • tags, document_tags              │   - doc_type, doc_id, tags        │
│ • links               ←── NEW      │     (денормализация)              │
│ • entities, document_entities      │                                   │
│ • embedding_cache     ←── NEW      │                                   │
│ • search_history                   │                                   │
└────────────────────────────────────┴───────────────────────────────────┘
```

## Фазы реализации

### Фаза 2.0.1 — SQLite Infrastructure (неделя 1-2)

**Цель:** Базовая инфраструктура SQLite с миграциями

| Задача | Приоритет | Сложность | Файлы |
|--------|-----------|-----------|-------|
| SQLiteManager с connection pooling | P0 | M | `storage/sqlite/manager.py` |
| Schema DDL (все 10 таблиц) | P0 | M | `storage/sqlite/schema.py` |
| Migration runner | P0 | S | `storage/sqlite/migrations/` |
| DocumentRepository | P0 | M | `storage/sqlite/repositories/document.py` |
| Protocol интерфейсы | P0 | S | `interfaces.py` |

**Deliverables:**
- [ ] SQLite БД создаётся с полной схемой
- [ ] CRUD операции для documents
- [ ] Unit тесты ≥90% coverage

---

### Фаза 2.0.2 — Normalized Frontmatter (неделя 2-3)

**Цель:** Парсинг frontmatter в отдельные типизированные записи

| Задача | Приоритет | Сложность | Файлы |
|--------|-----------|-----------|-------|
| FrontmatterParser (YAML → Properties) | P0 | M | `storage/sqlite/frontmatter_parser.py` |
| PropertyRepository с типизированным поиском | P0 | M | `storage/sqlite/repositories/property.py` |
| PropertySchemaBuilder (auto-schema) | P1 | M | `storage/sqlite/schema_builder.py` |
| Извлечение ссылок из frontmatter | P0 | S | В FrontmatterParser |

**Пример нормализации:**

```yaml
# Исходный frontmatter
---
type: 1-1
participant: "[[vshadrin]]"
date: 2025-01-08
status: active
tags: [meeting, q1]
priority: 1
---
```

```
# Записи в document_properties
┌─────────────┬────────────┬──────────────┬──────────────┬────────────┐
│ key         │ value_type │ value_string │ value_number │ list_index │
├─────────────┼────────────┼──────────────┼──────────────┼────────────┤
│ participant │ link       │              │              │ 0          │ → value_link_target = "vshadrin"
│ date        │ date       │              │              │ 0          │ → value_date = "2025-01-08"
│ status      │ string     │ active       │              │ 0          │
│ tags        │ string     │ meeting      │              │ 0          │
│ tags        │ string     │ q1           │              │ 1          │
│ priority    │ number     │              │ 1.0          │ 0          │
└─────────────┴────────────┴──────────────┴──────────────┴────────────┘
```

**Deliverables:**
- [ ] Frontmatter парсится в типизированные записи
- [ ] Поиск по свойствам работает через индексы (<50ms)
- [ ] `get_vault_schema()` возвращает все поля

---

### Фаза 2.0.3 — Embedding Cache (неделя 3-4)

**Цель:** Кэширование embeddings для избежания повторной векторизации

| Задача | Приоритет | Сложность | Файлы |
|--------|-----------|-----------|-------|
| EmbeddingCache (hash-based) | P0 | M | `storage/sqlite/embedding_cache.py` |
| CachedEmbeddingProvider wrapper | P0 | M | `providers/cached_provider.py` |
| Batch get/set для эффективности | P1 | S | В EmbeddingCache |
| Cache statistics (hits/misses) | P2 | S | В CachedEmbeddingProvider |

**Логика кэширования:**

```python
# При индексации chunk'а
content_hash = MD5(chunk.content)

cached = cache.get(content_hash, model="bge-m3")
if cached:
    embedding = cached  # Cache HIT
else:
    embedding = await provider.embed(chunk.content)
    cache.set(content_hash, embedding, model="bge-m3")  # Cache MISS
```

**Deliverables:**
- [ ] Cache hit rate ≥95% при повторной индексации
- [ ] Время повторной индексации 1000 файлов < 30 сек
- [ ] Метрики доступны через API

---

### Фаза 2.0.4 — Incremental Indexing (неделя 4-5)

**Цель:** Индексация только изменённых файлов

| Задача | Приоритет | Сложность | Файлы |
|--------|-----------|-----------|-------|
| ChangeDetector (hash comparison) | P0 | M | `storage/change_detector.py` |
| IncrementalIndexer | P0 | L | `storage/indexing/incremental.py` |
| Batch upsert с транзакциями | P1 | M | В repositories |
| File watcher (watchdog) | P1 | M | `storage/file_watcher.py` |

**ChangeSet:**

```python
@dataclass
class ChangeSet:
    added: list[Path]      # Новые файлы
    modified: list[Path]   # Изменённые (hash отличается)
    deleted: list[str]     # Удалённые (document_id)
    unchanged: int         # Количество без изменений
```

**Deliverables:**
- [ ] Инкрементальная индексация 10 файлов < 5 сек
- [ ] Удалённые файлы удаляются из индекса
- [ ] File watcher триггерит переиндексацию

---

### Фаза 2.0.5 — Migration & Integration (неделя 5-6)

**Цель:** Миграция данных и интеграция в существующий код

| Задача | Приоритет | Сложность | Файлы |
|--------|-----------|-----------|-------|
| Migration script v1 → v2 | P0 | L | `scripts/migrate_v2.py` |
| ServiceContainer update | P0 | M | `service_container.py` |
| MCP tools update | P0 | M | `mcp_server.py` |
| Backward compatibility layer | P1 | M | `compat/` |
| Documentation update | P1 | S | `README.md`, `CHANGELOG.md` |

**Deliverables:**
- [ ] Миграция без потери данных
- [ ] Все существующие MCP tools работают
- [ ] Документация обновлена

---

## Структура файлов Release 2.0

```
src/obsidian_kb/
├── storage/
│   ├── sqlite/                          # NEW
│   │   ├── __init__.py
│   │   ├── manager.py                   # SQLiteManager
│   │   ├── schema.py                    # DDL
│   │   ├── types.py                     # ValueType, LinkType enums
│   │   ├── frontmatter_parser.py        # FrontmatterParser
│   │   ├── schema_builder.py            # PropertySchemaBuilder
│   │   ├── embedding_cache.py           # EmbeddingCache
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── runner.py
│   │   │   └── v001_initial.py
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── document.py
│   │       ├── property.py
│   │       ├── link.py
│   │       ├── tag.py
│   │       └── entity.py
│   ├── lance/                           # EXISTING (updated)
│   │   ├── manager.py
│   │   └── chunk_repository.py
│   ├── change_detector.py               # NEW
│   ├── file_watcher.py                  # NEW
│   └── indexing/
│       ├── incremental.py               # NEW
│       └── ...
├── providers/
│   └── cached_provider.py               # NEW
└── ...
```

---

## Риски и митигации

| Риск | Вероятность | Impact | Митигация |
|------|-------------|--------|-----------|
| Потеря данных при миграции | Medium | Critical | Backup + dry-run режим |
| Breaking changes в API | High | High | Backward compat layer |
| SQLite lock contention | Medium | Medium | WAL mode + connection pool |
| Performance regression | Medium | High | Benchmarks на каждой фазе |

---

## Критерии готовности Release 2.0

### Функциональные
- [ ] SQLite хранит все метаданные (documents, properties, links, tags)
- [ ] LanceDB хранит только chunks с векторами
- [ ] Frontmatter нормализован в типизированные записи
- [ ] Embedding cache работает с hit rate ≥95%
- [ ] Инкрементальная индексация работает

### Качество
- [ ] Все тесты проходят (≥1100 тестов)
- [ ] Coverage ≥85% для новых модулей
- [ ] Нет регрессий в существующих функциях

### Производительность
- [ ] Поиск по свойству < 50ms
- [ ] Инкрементальная индексация < 5 сек для 10 файлов
- [ ] Полная переиндексация < 30 сек при cache hit

### Документация
- [ ] README обновлён
- [ ] CHANGELOG с breaking changes
- [ ] Migration guide

---

# Release 2.1 — "Search Quality"

## Цель

Улучшение качества поиска через лучшие модели, граф-запросы и reranking.

## Целевые метрики

| Метрика | v2.0 | v2.1 Target |
|---------|------|-------------|
| Recall@10 | ~70% | ~85% |
| Поиск по русским именам | Ненадёжен | Надёжен (aliases) |
| Multi-hop queries | Нет | Работает |

## Фазы

### Фаза 2.1.1 — BGE-M3 Integration (1-2 недели)

| Задача | Описание |
|--------|----------|
| BGE-M3 provider | Замена nomic-embed-text на BGE-M3 (1024 dim) |
| Sparse vectors | Поддержка dense + sparse для hybrid search |
| Migration embeddings | Переиндексация с новой моделью |

**Выигрыш:** BGE-M3 показывает 70.0 nDCG@10 на MIRACL (русский) vs ~50% для nomic.

---

### Фаза 2.1.2 — Entity Extraction (1-2 недели)

| Задача | Описание |
|--------|----------|
| NER pipeline | spaCy для извлечения people, orgs, projects |
| Entity linking | Связь с canonical документами (vshadrin → doc_001) |
| Alias search | Поиск "Сева" → находит vshadrin |

**Пример:**

```
Текст: "Обсудил с Севой архитектуру PSB"

Entities:
- "Сева" → entity: vshadrin (person) → canonical: doc_001
- "PSB" → entity: psb (project) → canonical: doc_002
```

---

### Фаза 2.1.3 — Graph Queries (1-2 недели)

| Задача | Описание |
|--------|----------|
| NetworkX integration | Граф из таблицы LINKS |
| Traversal queries | `find_connected(doc, depth=2)` |
| Path finding | `find_path(from, to)` |
| Centrality metrics | Важность документов |

**Новые MCP tools:**

```python
find_connected(vault, doc_id, depth=2)  # Все связанные на расстоянии 2
find_path(vault, from_doc, to_doc)      # Кратчайший путь
get_central_docs(vault, limit=10)       # Самые связанные документы
```

---

### Фаза 2.1.4 — Hybrid Reranking (1 неделя)

| Задача | Описание |
|--------|----------|
| Cross-encoder | Rerank top-50 → top-10 |
| RRF fusion | Объединение vector + FTS + graph scores |
| Tunable weights | Настройка весов по типу запроса |

---

# Release 2.2 — "Intelligence"

## Цель

AI-powered улучшения: контекстное обогащение, переформулировка запросов, семантический кэш.

## Целевые метрики

| Метрика | v2.1 | v2.2 Target |
|---------|------|-------------|
| Retrieval quality | Baseline | +20% с Contextual |
| Query understanding | Literal | Smart rewriting |
| Cache efficiency | Hash-based | +30% semantic hits |

## Фазы

### Фаза 2.2.1 — Contextual Retrieval (2-3 недели)

Добавление context prefix к каждому chunk для улучшения retrieval.

**До:**
```
"1. Ревью архитектуры PSB
2. Подготовка Q1 roadmap"
```

**После:**
```
"[Document: vshadrin.md (person profile). Section: Текущие задачи. 
This chunk lists current tasks for Vsevolod Shadrin, Technical Lead.]

1. Ревью архитектуры PSB
2. Подготовка Q1 roadmap"
```

---

### Фаза 2.2.2 — Query Rewriting (2 недели)

LLM-based улучшение запросов перед поиском.

**Примеры:**

| Исходный запрос | Переписанный |
|-----------------|--------------|
| "встречи с Севой" | "1-1 participant:vshadrin OR mentions:vshadrin" |
| "что решили по PSB" | "project:psb type:meeting status:done decisions" |
| "архитектура" | "архитектура ADR architecture design" |

---

### Фаза 2.2.3 — Semantic Cache (2 недели)

Кэширование результатов для семантически похожих запросов.

```python
# Query: "встречи с Шадриным"
# → Embedding similarity check
# → Cache HIT: "1-1 с vshadrin" (similarity 0.92)
# → Return cached results
```

---

### Фаза 2.2.4 — Auto-enrichment (2-3 недели)

Автоматическое обогащение документов при индексации.

| Enrichment | Описание |
|------------|----------|
| Auto-summary | Краткое содержание документа |
| Auto-tags | Предложение тегов на основе контента |
| Related docs | Автоматические связи по similarity |

---

# Сводная таблица релизов

| Release | Фокус | Срок | Ключевые deliverables |
|---------|-------|------|----------------------|
| **2.0** | Storage | 4-6 нед | SQLite, normalized frontmatter, cache, incremental |
| **2.1** | Search | 4-6 нед | BGE-M3, NER, graph queries, reranking |
| **2.2** | AI | 6-8 нед | Contextual, query rewriting, semantic cache |

---

# Immediate Next Steps (Release 2.0)

1. **Создать ветку** `feature/storage-v2`
2. **Начать с Phase 2.0.1**: SQLiteManager + schema
3. **Параллельно**: написать миграционный скрипт (dry-run)
4. **Milestone**: работающий прототип через 2 недели
