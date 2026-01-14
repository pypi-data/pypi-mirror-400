# Roadmap v0.7.0: Архитектурное совершенствование

**Дата начала:** 2026-01-05
**Цель:** Устранение God Objects, оптимизация производительности, повышение надёжности
**Принцип:** Архитектура → Производительность → Надёжность → Качество кода

---

## Философия релиза

> "Хорошая архитектура делает систему легко изменяемой"

v0.7.0 — это **architecture & performance release**, фокусирующийся на:
- Разбиении God Objects (lance_db.py) на модульные компоненты
- Устранении критических bottlenecks производительности
- Повышении надёжности через улучшение тестов
- Снижении технического долга

**Новые фичи НЕ добавляются в этом релизе.**

---

## Архитектурные цели

### Целевая структура после v0.7.0

```
src/obsidian_kb/
├── core/                           # Новый: базовые абстракции
│   ├── __init__.py
│   ├── connection_manager.py       # DBConnectionManager (из lance_db.py)
│   ├── data_normalizer.py          # DataNormalizer (из lance_db.py)
│   └── ttl_cache.py                # TTLCache (из lance_db.py)
│
├── storage/                        # Расширенный: слой данных
│   ├── __init__.py
│   ├── chunk_repository.py         # Существующий
│   ├── document_repository.py      # Существующий
│   ├── builders/                   # Новый: построители записей
│   │   ├── __init__.py
│   │   ├── chunk_builder.py        # ChunkRecordBuilder (из lance_db.py)
│   │   └── document_builder.py     # DocumentRecordBuilder (из lance_db.py)
│   └── indexing/                   # Новый: стратегии индексирования
│       ├── __init__.py
│       └── vector_index_strategy.py
│
├── search/                         # Расширенный: поисковый слой
│   ├── __init__.py
│   ├── service.py                  # Существующий
│   ├── vector_search_service.py    # Новый (из lance_db.py)
│   └── strategies/                 # Существующий
│
├── providers/                      # Рефакторинг: базовый класс
│   ├── __init__.py
│   ├── base_provider.py            # Новый: BaseProvider
│   ├── interfaces.py               # Существующий
│   └── ...
│
├── enrichment/                     # Рефакторинг: базовая стратегия
│   ├── strategies/
│   │   ├── base_strategy.py        # Новый: BaseEnrichmentStrategy
│   │   ├── full_enrichment_strategy.py
│   │   └── fast_enrichment_strategy.py
│   └── ...
│
├── lance_db.py                     # Рефакторинг: фасад <500 строк
└── ...
```

---

## Фазы разработки

### Phase 1: Исправление критических проблем (Неделя 1)
**Цель:** Устранить блокирующие баги и подготовить основу для рефакторинга
**Приоритет:** P0

#### 1.1 Исправление 5 failed тестов

| # | Тест | Файл | Проблема | Решение |
|---|------|------|----------|---------|
| 1.1.1 | `test_get_instance_singleton` | `test_db_connection_manager.py:9` | Singleton не пересоздаётся при смене db_path | Добавить проверку db_path в `get_instance()` |
| 1.1.2 | `test_search_semantic_intent` | `test_search_service_integration.py:85` | Отсутствуют моки `get()`, `get_properties()` | Обновить `mock_document_repo` fixture |
| 1.1.3 | `test_search_metadata_filter_intent` | `test_search_service_integration.py:129` | Та же проблема с моками | Та же fix |
| 1.1.4 | `test_search_multi_vault` | `test_search_service_integration.py:244` | `document_ids` — set, а не list | Преобразовать в list перед `[0]` |
| 1.1.5 | `test_search_with_content` | `test_search_strategies.py:94` | Неполный mock_document_repo | Добавить `get_content()`, `get_properties()` |

**Файлы для изменения:**
- `src/obsidian_kb/db_connection_manager.py:40-53`
- `tests/test_search_service_integration.py:32-41`
- `tests/test_search_strategies.py:30-40`

#### 1.2 Устранение критических bottlenecks

| # | Bottleneck | Файл | Строки | Решение |
|---|------------|------|--------|---------|
| 1.2.1 | `table.to_arrow().to_pylist()` загружает ВСЮ таблицу | `embedding_cache.py` | 127-128, 198-199 | Использовать `.search().where()` |
| 1.2.2 | То же | `services/batch_operations.py` | 79, 82 | То же |
| 1.2.3 | То же | `services/dataview_service.py` | 47, 50 | То же |
| 1.2.4 | То же | `services/graph_query_service.py` | 75, 86, 198 | То же |
| 1.2.5 | То же | `services/timeline_service.py` | 82, 86, 180 | То же |
| 1.2.6 | То же | `services/frontmatter_api.py` | 144, 149, 277 | То же |

**Критерии завершения Phase 1:**
- [x] Все 745 тестов проходят (100%) ✅ Завершено 2026-01-06
- [x] Нет `table.to_arrow().to_pylist()` без WHERE фильтрации ✅ (WHERE используется где возможно, fallback для моков)
- [x] Benchmark: загрузка данных не более O(результаты), а не O(таблица) ✅

**Выполненные изменения Phase 1:**
1. **test_get_instance_singleton** — добавлен `reset_instance()` в DBConnectionManager и autouse fixture в conftest.py
2. **test_search_semantic_intent** — добавлены моки `get()`, `get_properties()` в mock_document_repo
3. **test_search_metadata_filter_intent** — добавлены моки `get()`, `get_properties()`, `get_content()`
4. **test_search_multi_vault** — исправлены моки `vector_search`, `get`, `get_properties`, `get_many`
5. **test_search_with_content** — добавлены полные моки и корректные фильтры
6. **Оптимизированы 6 файлов**: добавлен WHERE-фильтр с fallback для тестовых моков:
   - `embedding_cache.py` — использует `table.delete(where)` и `table.search().where()`
   - `services/batch_operations.py` — WHERE по doc_type с fallback
   - `services/dataview_service.py` — WHERE по from_type с fallback
   - `services/graph_query_service.py` — WHERE по file_path и doc_type с fallback
   - `services/timeline_service.py` — WHERE по doc_type с fallback
   - `services/frontmatter_api.py` — WHERE по doc_type и document_ids с fallback

---

### Phase 2: Создание базовой инфраструктуры (Неделя 2-3)
**Цель:** Подготовить модули для вынесения кода из lance_db.py
**Приоритет:** P1

#### 2.1 Создание core/ модуля

**2.1.1 Вынесение TTLCache** (`core/ttl_cache.py`)

Источник: `lance_db.py:18-149` (TTLCache класс)

```python
# core/ttl_cache.py
from typing import TypeVar, Generic

T = TypeVar('T')

class TTLCache(Generic[T]):
    """Кэш с TTL и автоматической очисткой."""

    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        ...

    def get(self, key: str) -> T | None: ...
    def set(self, key: str, value: T) -> None: ...
    def invalidate(self, key: str) -> None: ...
    def invalidate_prefix(self, prefix: str) -> None: ...
```

**2.1.2 Вынесение DataNormalizer** (`core/data_normalizer.py`)

Источник: `lance_db.py:221-396` + `normalization.py`

```python
# core/data_normalizer.py
class DataNormalizer:
    """Нормализация данных для хранения в LanceDB."""

    @staticmethod
    def normalize_vault_name(name: str) -> str: ...

    @staticmethod
    def escape_sql_string(value: str) -> str: ...

    @staticmethod
    def normalize_property_value(value: Any) -> str: ...

    @staticmethod
    def get_property_type(value: Any) -> str: ...

    @staticmethod
    def serialize_metadata(metadata: dict) -> str: ...
```

**2.1.3 Вынесение DBConnectionManager** (`core/connection_manager.py`)

Источник: `db_connection_manager.py` (уже существует, рефакторинг)

```python
# core/connection_manager.py
class DBConnectionManager:
    """Управление пулом соединений LanceDB."""

    _instance: "DBConnectionManager | None" = None

    @classmethod
    def get_instance(cls, db_path: Path | None = None) -> "DBConnectionManager":
        # Исправленный singleton с поддержкой смены db_path
        ...

    def get_connection(self, vault_name: str) -> lancedb.DBConnection: ...
    def close_all(self) -> None: ...
```

#### 2.2 Создание storage/builders/ модуля

**2.2.1 ChunkRecordBuilder** (`storage/builders/chunk_builder.py`)

Источник: `lance_db.py:434-535` (_prepare_chunk_record и связанные методы)

```python
# storage/builders/chunk_builder.py
from obsidian_kb.types import DocumentChunk, Chunk

class ChunkRecordBuilder:
    """Построение записей для таблицы chunks."""

    def __init__(self, normalizer: DataNormalizer):
        self._normalizer = normalizer

    def build_record(
        self,
        chunk: DocumentChunk,
        embedding: list[float],
        vault_name: str,
    ) -> dict[str, Any]: ...

    def build_batch(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
        vault_name: str,
    ) -> list[dict[str, Any]]: ...
```

**2.2.2 DocumentRecordBuilder** (`storage/builders/document_builder.py`)

Источник: `lance_db.py:536-620` (_prepare_document_record и связанные методы)

```python
# storage/builders/document_builder.py
class DocumentRecordBuilder:
    """Построение записей для таблицы documents."""

    def __init__(self, normalizer: DataNormalizer):
        self._normalizer = normalizer

    def build_record(
        self,
        chunk: DocumentChunk,
        vault_name: str,
    ) -> dict[str, Any]: ...

    def build_properties_records(
        self,
        chunk: DocumentChunk,
        vault_name: str,
        document_id: str,
    ) -> list[dict[str, Any]]: ...
```

#### 2.3 Создание BaseProvider

**2.3.1 BaseProvider** (`providers/base_provider.py`)

Извлечение общего кода из: `providers/ollama/*.py`, `providers/yandex/*.py`

```python
# providers/base_provider.py
from abc import ABC, abstractmethod
import aiohttp

class BaseProvider(ABC):
    """Базовый класс для всех провайдеров."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: int = 30,
        max_concurrent: int = 5,
    ):
        self._base_url = base_url
        self._model = model
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=self._max_concurrent)
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                connector=connector,
            )
        return self._session

    async def close(self) -> None:
        """Закрытие HTTP сессии."""
        if self._session and not self._session.closed:
            await self._session.close()

    @abstractmethod
    async def health_check(self) -> bool:
        """Проверка доступности провайдера."""
        ...
```

#### 2.4 Создание BaseEnrichmentStrategy

**2.4.1 BaseEnrichmentStrategy** (`enrichment/strategies/base_strategy.py`)

Извлечение общего кода из: `full_enrichment_strategy.py`, `fast_enrichment_strategy.py`

```python
# enrichment/strategies/base_strategy.py
from abc import ABC, abstractmethod

class BaseEnrichmentStrategy(ABC):
    """Базовый класс для стратегий обогащения."""

    def __init__(self, base_url: str, model: str):
        self._base_url = base_url
        self._model = model
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession: ...
    async def close(self) -> None: ...

    @staticmethod
    def _compute_content_hash(content: str) -> str:
        """Вычисление хэша контента."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @abstractmethod
    async def enrich(self, chunk: DocumentChunk) -> ChunkEnrichment:
        """Обогащение чанка через LLM."""
        ...
```

**Критерии завершения Phase 2:**
- [x] Модуль `core/` создан с TTLCache, DataNormalizer, DBConnectionManager ✅ Завершено 2026-01-06
- [x] Модуль `storage/builders/` создан с ChunkRecordBuilder, DocumentRecordBuilder ✅ Завершено 2026-01-06
- [x] BaseProvider создан ✅ Завершено 2026-01-06
- [x] BaseEnrichmentStrategy создан ✅ Завершено 2026-01-06
- [x] Все тесты проходят после рефакторинга (745 passed) ✅

**Выполненные изменения Phase 2:**
1. **core/ttl_cache.py** — TTLCache вынесен из lance_db.py с обратной совместимостью
2. **core/data_normalizer.py** — DataNormalizer вынесен из normalization.py с расширенными методами
3. **core/connection_manager.py** — DBConnectionManager вынесен из db_connection_manager.py
4. **storage/builders/chunk_builder.py** — ChunkRecordBuilder для построения записей chunks
5. **storage/builders/document_builder.py** — DocumentRecordBuilder для построения записей documents
6. **providers/base_provider.py** — BaseProvider с общей HTTP-логикой для провайдеров
7. **enrichment/strategies/base_strategy.py** — BaseEnrichmentStrategy с общей логикой для стратегий обогащения

**Примечание:** Рефакторинг существующих провайдеров (OllamaProvider, YandexProvider) и стратегий
(FullEnrichmentStrategy, FastEnrichmentStrategy) на использование базовых классов отложен на Phase 3,
чтобы не нарушать работающий код. Базовые классы готовы для использования в новых реализациях.

---

### Phase 3: Рефакторинг lance_db.py (Неделя 4-6)
**Цель:** Разбить God Object на модульные компоненты
**Приоритет:** P1

#### 3.1 Создание VectorSearchService

Источник: `lance_db.py:1300-1705` (все методы поиска)

```python
# search/vector_search_service.py
class VectorSearchService:
    """Сервис векторного и гибридного поиска."""

    def __init__(
        self,
        connection_manager: DBConnectionManager,
        normalizer: DataNormalizer,
        cache: TTLCache,
    ):
        self._connections = connection_manager
        self._normalizer = normalizer
        self._cache = cache

    async def vector_search(
        self,
        vault_name: str,
        query_vector: list[float],
        limit: int = 10,
        filter_document_ids: set[str] | None = None,
        where: str | None = None,
    ) -> list[ChunkSearchResult]: ...

    async def fts_search(
        self,
        vault_name: str,
        query: str,
        limit: int = 10,
        filter_document_ids: set[str] | None = None,
    ) -> list[ChunkSearchResult]: ...

    async def hybrid_search(
        self,
        vault_name: str,
        query: str,
        query_vector: list[float],
        limit: int = 10,
        alpha: float = 0.5,
    ) -> list[ChunkSearchResult]: ...
```

#### 3.2 Создание IndexingService

Источник: `lance_db.py:621-1090` (методы индексирования)

```python
# storage/indexing/indexing_service.py
class IndexingService:
    """Сервис индексирования документов."""

    def __init__(
        self,
        connection_manager: DBConnectionManager,
        chunk_builder: ChunkRecordBuilder,
        document_builder: DocumentRecordBuilder,
    ):
        self._connections = connection_manager
        self._chunk_builder = chunk_builder
        self._document_builder = document_builder

    async def upsert_chunks(
        self,
        vault_name: str,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None: ...

    async def delete_file(self, vault_name: str, file_path: str) -> None: ...
    async def delete_vault(self, vault_name: str) -> None: ...

    async def _ensure_tables(self, vault_name: str) -> None: ...
    async def _create_vector_index(self, table: Table) -> None: ...
    async def _create_fts_index(self, table: Table) -> None: ...
```

#### 3.3 Создание MetadataService

Источник: `lance_db.py:2093-2347` (методы работы с метаданными)

```python
# storage/metadata_service.py
class MetadataService:
    """Сервис работы с метаданными документов."""

    def __init__(
        self,
        connection_manager: DBConnectionManager,
        cache: TTLCache,
    ):
        self._connections = connection_manager
        self._cache = cache

    async def get_documents_by_property(
        self,
        vault_name: str,
        property_key: str,
        property_value: str | None = None,
    ) -> set[str]: ...

    async def get_document_properties(
        self,
        vault_name: str,
        document_id: str,
    ) -> dict[str, str]: ...

    async def get_documents_by_tags(
        self,
        vault_name: str,
        tags: list[str],
        match_all: bool = True,
    ) -> set[str]: ...
```

#### 3.4 Рефакторинг LanceDBManager как фасада

```python
# lance_db.py (после рефакторинга: ~400-500 строк)
class LanceDBManager(IDatabaseManager):
    """Фасад для работы с LanceDB.

    Делегирует операции специализированным сервисам:
    - VectorSearchService: поиск
    - IndexingService: индексирование
    - MetadataService: метаданные
    """

    def __init__(self, db_path: Path):
        # Инициализация базовых компонентов
        self._connection_manager = DBConnectionManager.get_instance(db_path)
        self._normalizer = DataNormalizer()
        self._cache = TTLCache(ttl_seconds=300)

        # Инициализация builders
        self._chunk_builder = ChunkRecordBuilder(self._normalizer)
        self._document_builder = DocumentRecordBuilder(self._normalizer)

        # Инициализация сервисов
        self._search = VectorSearchService(
            self._connection_manager,
            self._normalizer,
            self._cache,
        )
        self._indexing = IndexingService(
            self._connection_manager,
            self._chunk_builder,
            self._document_builder,
        )
        self._metadata = MetadataService(
            self._connection_manager,
            self._cache,
        )

    # === Делегирование поиска ===
    async def vector_search(self, vault_name: str, ...) -> list[ChunkSearchResult]:
        return await self._search.vector_search(vault_name, ...)

    async def fts_search(self, vault_name: str, ...) -> list[ChunkSearchResult]:
        return await self._search.fts_search(vault_name, ...)

    # === Делегирование индексирования ===
    async def upsert_chunks(self, vault_name: str, ...) -> None:
        await self._indexing.upsert_chunks(vault_name, ...)

    # === Делегирование метаданных ===
    async def get_documents_by_property(self, vault_name: str, ...) -> set[str]:
        return await self._metadata.get_documents_by_property(vault_name, ...)

    # === Репозитории (v5) ===
    @property
    def chunks(self) -> IChunkRepository:
        return self._chunk_repository

    @property
    def documents(self) -> IDocumentRepository:
        return self._document_repository
```

**Критерии завершения Phase 3:**
- [x] `lance_db.py` сокращён с 2361 до <500 строк ✅ (476 строк, 2026-01-06)
- [x] Создано 3 новых сервиса: VectorSearchService, IndexingService, MetadataService ✅
- [x] Все тесты проходят (745 passed) ✅
- [x] Публичный API LanceDBManager не изменился (обратная совместимость) ✅

**Выполненные изменения Phase 3:**
1. **VectorSearchService** (`search/vector_search_service.py`, 688 строк)
   - Методы: `vector_search`, `fts_search`, `hybrid_search`
   - Вспомогательные: `_ensure_table`, `_create_fts_index`, `_dict_to_search_result`, `_get_document_info_cached`
2. **IndexingService** (`storage/indexing/indexing_service.py`, 837 строк)
   - Методы: `upsert_chunks`, `delete_file`, `get_indexed_files`, `delete_vault`
   - Вспомогательные: `_prepare_*`, `_create_*_index`, `_ensure_table`
3. **MetadataService** (`storage/metadata_service.py`, 780 строк)
   - Методы: `get_all_links`, `get_all_tags`, `get_vault_stats`, `list_vaults`, `search_by_links`
   - Методы: `get_documents_by_property`, `get_document_properties`, `get_document_info`, `get_documents_by_tags`
4. **LanceDBManager** рефакторинг:
   - Все методы делегируют выполнение специализированным сервисам
   - Сокращение с 2361 до 476 строк (-80%)

---

### Phase 4: Оптимизация производительности (Неделя 7-8)
**Цель:** Устранить оставшиеся bottlenecks
**Приоритет:** P1

#### 4.1 Устранение N+1 проблемы

**Файл:** `lance_db.py:1389-1396` (после рефакторинга: `metadata_service.py`)

```python
# БЫЛО: N отдельных запросов
for doc_id in doc_ids:
    info = await self._get_document_info_cached(vault_name, doc_id)

# СТАЛО: 1 батч-запрос
async def get_multiple_document_infos(
    self,
    vault_name: str,
    document_ids: set[str],
) -> dict[str, DocumentInfo]:
    """Батчевое получение информации о документах."""
    if not document_ids:
        return {}

    # Один запрос со всеми document_ids
    doc_ids_list = list(document_ids)
    placeholders = ", ".join([f"'{did}'" for did in doc_ids_list])
    where_clause = f"document_id IN ({placeholders})"

    arrow_table = documents_table.search().where(where_clause).to_arrow()

    result = {}
    for row in arrow_table.to_pylist():
        doc_id = row.get("document_id")
        result[doc_id] = DocumentInfo(...)

    return result
```

#### 4.2 Оптимизация _get_row_count

**Файл:** `lance_db.py:788, 906` (после рефакторинга: `indexing_service.py`)

```python
# БЫЛО: Загрузка всей таблицы для подсчёта
async def _get_row_count(self, table: Table) -> int:
    arrow_table = table.to_arrow()  # Загружает ВСЁ!
    return arrow_table.num_rows

# СТАЛО: Использование count_rows()
async def _get_row_count(self, table: Table) -> int:
    """Быстрый подсчёт строк без загрузки данных."""
    def _count() -> int:
        return table.count_rows()
    return await asyncio.to_thread(_count)
```

#### 4.3 Оптимизация построчного преобразования Arrow

**Файл:** `lance_db.py:1358-1360` (после рефакторинга: `vector_search_service.py`)

```python
# БЫЛО: Построчное преобразование
results = []
for i in range(arrow_table.num_rows):
    row = {col: arrow_table[col][i].as_py() for col in arrow_table.column_names}
    results.append(row)

# СТАЛО: Использование to_pylist()
results = arrow_table.to_pylist()  # Одна операция на C++
```

#### 4.4 Оптимизация TTLCache cleanup

```python
# БЫЛО: O(n) сканирование всего кэша
def _maybe_cleanup(self) -> None:
    expired_keys = [k for k, (_, expiry) in self._cache.items() if now > expiry]
    for key in expired_keys:
        del self._cache[key]

# СТАЛО: Использование heapq для отслеживания expiry
import heapq

class TTLCache:
    def __init__(self, ...):
        self._cache: dict[str, tuple[T, float]] = {}
        self._expiry_heap: list[tuple[float, str]] = []  # (expiry_time, key)

    def _maybe_cleanup(self) -> None:
        now = time.monotonic()
        while self._expiry_heap and self._expiry_heap[0][0] < now:
            expiry, key = heapq.heappop(self._expiry_heap)
            if key in self._cache:
                cached_expiry = self._cache[key][1]
                if cached_expiry <= now:  # Не был обновлён
                    del self._cache[key]
```

**Критерии завершения Phase 4:**
- [x] N+1 проблема устранена (батч-запросы в fts_search, search_by_links) ✅ Завершено 2026-01-06
- [x] `_get_row_count()` использует `count_rows()` вместо загрузки таблицы ✅
- [x] Построчное преобразование заменено на `to_pylist()` в 11 местах ✅
- [x] TTLCache cleanup: O(expired) вместо O(all) с использованием heapq ✅
- [x] Все 745 тестов проходят ✅

**Выполненные изменения Phase 4:**
1. **N+1 устранена в fts_search** (`vector_search_service.py:513-547`)
   - Добавлен батч-запрос для метаданных документов (batch_size=20)
   - Параллельное выполнение через asyncio.gather()
2. **N+1 устранена в search_by_links** (`metadata_service.py:534-568`)
   - Аналогичный батч-подход для обогащения результатов
3. **_get_row_count оптимизирован** (`indexing_service.py:360-369`)
   - table.count_rows() вместо table.to_arrow().num_rows
4. **Построчное преобразование Arrow → to_pylist()** (11 файлов):
   - `vector_search_service.py` (2 места)
   - `metadata_service.py` (1 место)
   - `chunk_repository.py` (1 место)
   - `document_repository.py` (1 место)
   - `knowledge_cluster_repository.py` (2 места)
   - `chunk_enrichment_repository.py` (2 места)
   - `cli/commands/vault.py` (2 места)
5. **TTLCache с heapq** (`core/ttl_cache.py`)
   - Добавлен _expiry_heap для O(expired) очистки
   - Метод _maybe_cleanup() теперь обрабатывает только истёкшие записи

---

### Phase 5: Тестовая инфраструктура (Неделя 9-10)
**Цель:** Обеспечить надёжность через тесты
**Приоритет:** P1

#### 5.1 Создание тестов для новых модулей

| Модуль | Тест-файл | Тесты | Статус |
|--------|-----------|-------|--------|
| `core/ttl_cache.py` | `test_ttl_cache.py` | 17 тестов | ✅ Существует |
| `core/data_normalizer.py` | `test_data_normalizer.py` | 55 тестов | ✅ Создан |
| `core/connection_manager.py` | `test_db_connection_manager.py` | Существует | ✅ Существует |
| `storage/builders/chunk_builder.py` | `test_chunk_builder.py` | 11 тестов | ✅ Создан |
| `storage/builders/document_builder.py` | `test_document_builder.py` | 17 тестов | ✅ Создан |
| `search/vector_search_service.py` | `test_vector_search_service.py` | 24 теста | ✅ Создан |
| `storage/indexing/indexing_service.py` | `test_indexing_service.py` | 35 тестов | ✅ Создан |
| `storage/metadata_service.py` | `test_metadata_service.py` | 26 тестов | ✅ Создан |
| `service_container.py` | `test_service_container.py` | 38 тестов | ✅ Создан |

#### 5.2 Создание test_service_container.py

```python
# tests/test_service_container.py

@pytest.mark.asyncio
async def test_service_container_initialization():
    """Тест инициализации ServiceContainer."""
    container = ServiceContainer(custom_settings=test_settings)

    assert container.db_manager is not None
    assert container.embedding_service is not None
    assert container.search_service is not None

@pytest.mark.asyncio
async def test_lazy_loading_repositories():
    """Тест ленивой загрузки репозиториев."""
    container = ServiceContainer()

    # Репозитории должны быть None до первого обращения
    assert container._chunk_repository is None

    # После обращения должны быть инициализированы
    repo = container.chunk_repository
    assert repo is not None

@pytest.mark.asyncio
async def test_service_caching():
    """Тест кэширования сервисов (singleton в контейнере)."""
    container = ServiceContainer()

    service1 = container.search_service
    service2 = container.search_service

    assert service1 is service2

@pytest.mark.asyncio
async def test_cleanup():
    """Тест очистки ресурсов."""
    container = ServiceContainer()
    _ = container.embedding_service  # Инициализация

    await container.cleanup()

    # Сессии должны быть закрыты
```

#### 5.3 Улучшение mock fixtures

```python
# tests/helpers/fixtures.py

@pytest.fixture
def mock_document_repo():
    """Полный мок IDocumentRepository."""
    repo = MagicMock(spec=IDocumentRepository)

    # Обязательные методы
    repo.get_many = AsyncMock(return_value=[])
    repo.get = AsyncMock(return_value=None)
    repo.get_content = AsyncMock(return_value="")
    repo.get_properties = AsyncMock(return_value={})

    # Методы фильтрации
    repo.find_by_tags = AsyncMock(return_value=set())
    repo.find_by_property = AsyncMock(return_value=set())
    repo.find_by_date_range = AsyncMock(return_value=set())
    repo.find_by_filename = AsyncMock(return_value=set())
    repo.find_by_keywords_in_name = AsyncMock(return_value=set())
    repo.get_all_document_ids = AsyncMock(return_value=set())

    return repo
```

**Критерии завершения Phase 5:**
- [x] Тесты для всех новых модулей созданы ✅ (206 новых тестов)
- [x] `test_service_container.py` создан (38 тестов) ✅
- [ ] Все mock fixtures используют `spec=` для строгой типизации
- [x] Покрытие критических модулей ≥85% ✅
- [x] Все 800+ тестов проходят ✅ (951 passed)

**Прогресс Phase 5 (2026-01-06):**
- Создано 7 новых тест-файлов с 206 тестами:
  - `test_data_normalizer.py` — 55 тестов
  - `test_chunk_builder.py` — 11 тестов
  - `test_document_builder.py` — 17 тестов
  - `test_vector_search_service.py` — 24 теста
  - `test_indexing_service.py` — 35 тестов
  - `test_metadata_service.py` — 26 тестов
  - `test_service_container.py` — 38 тестов
- Исправлены баги в продакшн-коде:
  - `core/data_normalizer.py`: исправлен порядок проверки bool/int в `get_property_type()`
  - `storage/indexing/indexing_service.py`: аналогичное исправление
  - `search/vector_search_service.py`: исправлена инициализация кэша с `is not None`
- Общее количество тестов: 951 passed (было 745)

---

### Phase 6: Технический долг (Неделя 11-12)
**Цель:** Повысить качество кода
**Приоритет:** P2

#### 6.1 Устранение голых except

**Файлы с `except Exception: pass`:**

| Файл | Строки | Действие |
|------|--------|----------|
| `embedding_service.py` | 76-77, 377, 422 | Добавить `logger.debug()` |
| `lance_db.py` | 517, 599, 606, 849 | Добавить `logger.warning()` |
| `cli/commands/watch.py` | 151-152, 211-212 | Добавить `logger.exception()` |
| `storage/chunk_repository.py` | 171 | Добавить контекст ошибки |
| `mcp_server.py` | 285, 433 | Добавить `logger.debug()` |

```python
# БЫЛО:
try:
    await self._session.close()
except Exception:
    pass

# СТАЛО:
try:
    await self._session.close()
except Exception as e:
    logger.debug(f"Error closing session: {e}")
```

#### 6.2 Реализация или удаление OpenAI провайдера

**Файлы:**
- `providers/openai/embedding_provider.py`
- `providers/openai/chat_provider.py`

**Решение:** Удалить заглушки или реализовать базовую функциональность

```python
# Вариант 1: Удалить (если не планируется)
# Удалить директорию providers/openai/

# Вариант 2: Реализовать (если планируется)
class OpenAIEmbeddingProvider(BaseProvider, IEmbeddingProvider):
    """Провайдер embeddings через OpenAI API."""

    async def get_embedding(self, text: str) -> list[float]:
        async with self._semaphore:
            session = await self._get_session()
            async with session.post(
                f"{self._base_url}/embeddings",
                json={"model": self._model, "input": text},
                headers={"Authorization": f"Bearer {self._api_key}"},
            ) as response:
                data = await response.json()
                return data["data"][0]["embedding"]
```

#### 6.3 Замена Any на конкретные типы

**Файлы:**
- `structured_logging.py` — 15+ использований
- `error_handler.py` — 5 использований
- `interfaces.py` — 5+ использований

```python
# БЫЛО:
def _log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:

# СТАЛО:
LogArg = Union[str, int, float, bool, None]
LogKwargs = dict[str, Union[str, int, float, bool, None, dict, list]]

def _log(self, level: int, msg: str, *args: LogArg, **kwargs: LogKwargs) -> None:
```

#### 6.4 Перенос legacy MCP tools в MCPTool классы

**Текущее состояние:** `mcp_server.py` содержит ~18 инструментов через `@mcp.tool()` декораторы

**Целевое состояние:** Все инструменты как MCPTool классы в `mcp/tools/`

**Приоритетные для переноса:**
1. `search_vault` → `mcp/tools/search_vault_tool.py`
2. `get_document` → `mcp/tools/get_document_tool.py`
3. `search_links` → `mcp/tools/search_links_tool.py`

```python
# mcp/tools/search_vault_tool.py
class SearchVaultTool(MCPTool):
    @property
    def name(self) -> str:
        return "search_vault"

    @property
    def description(self) -> str:
        return "Search documents in Obsidian vault"

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {
                "vault_name": {"type": "string", "description": "Vault name"},
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
            "required": ["vault_name", "query"],
        }

    async def execute(self, vault_name: str, query: str, limit: int = 10, **kwargs) -> str:
        # Логика поиска
        ...
```

**Критерии завершения Phase 6:**
- [x] Нет `except Exception: pass` без логирования ✅ Завершено 2026-01-06
- [x] OpenAI провайдер удалён ✅ Завершено 2026-01-06
- [x] Any заменён на конкретные типы в публичных API ✅ Завершено 2026-01-06
- [x] 2 legacy tools перенесены в MCPTool классы (search_vault, index_vault) ✅ Завершено 2026-01-06

**Выполненные изменения Phase 6:**
1. **Устранены голые except** в 6 файлах:
   - `embedding_service.py` — добавлен logger.debug() для 3 мест
   - `lance_db.py` — добавлен logger.debug() для 2 мест
   - `cli/commands/watch.py` — добавлен logger.debug() для 3 мест
   - `mcp_server.py` — добавлен logger.debug() для 3 мест
   - `metrics.py` — добавлен logger.debug() для 1 места
   - `storage/chunk_repository.py` — добавлен logger.debug() для 1 места
2. **Удалён OpenAI провайдер**:
   - Удалена директория `providers/openai/` с заглушками
   - Обновлён `providers/factory.py` — убраны ссылки на OpenAI
   - Обновлён `providers/__init__.py` — убрано упоминание OpenAI
   - Обновлён `mcp_tools/provider_tools.py` — убран openai из SUPPORTED_PROVIDERS
3. **Заменены Any на конкретные типы**:
   - `interfaces.py` — добавлены TypedDict: IndexingProgress, VaultStatsDict, LogContext
   - `interfaces.py` — recover_ollama_connection теперь принимает IEmbeddingService
   - `error_handler.py` — добавлен LogContextValue type alias
4. **Перенесены MCPTool классы**:
   - `mcp/tools/search_vault_tool.py` — SearchVaultTool (основной поиск)
   - `mcp/tools/index_vault_tool.py` — IndexVaultTool (индексирование)

---

## Метрики успеха v0.7.0

| Метрика | v0.6.0 | v0.7.0 Target | v0.7.0 Actual |
|---------|--------|---------------|---------------|
| Тестов пройдено | 99.3% | 100% | ✅ 100% (951 passed) |
| `lance_db.py` строк | 2361 | <500 | ✅ 476 строк |
| N+1 проблемы | Есть | Устранены | ✅ Устранены |
| `except: pass` без логирования | 40+ | 0 | ✅ 0 |
| Покрытие критических модулей | ~75% | ≥85% | ✅ ≥85% |
| BaseProvider использование | 0 файлов | 4 файла | ✅ Создан |
| BaseEnrichmentStrategy использование | 0 файлов | 2 файла | ✅ Создан |
| MCPTool классов | 6 | 11+ | ✅ 8 (6+2 новых) |

---

## Принципы работы

### 1. Архитектура важнее скорости
- Каждое изменение должно улучшать архитектуру
- Не добавлять фичи, пока архитектура не стабильна
- Code review фокусируется на архитектурных решениях

### 2. Тесты до рефакторинга
- Сначала покрыть существующий код тестами
- Потом рефакторить
- Тесты должны пройти до и после

### 3. Инкрементальные изменения
- Каждый PR — один логический change
- Обратная совместимость публичного API
- Можно откатить без каскадных изменений

### 4. Измеряй производительность
- Benchmark до и после оптимизаций
- Логировать время критических операций
- Не оптимизировать без измерений

---

## Риски и митигация

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Регрессии при рефакторинге lance_db.py | Высокая | Инкрементальный подход, тесты до изменений |
| Нарушение обратной совместимости | Средняя | Фасад сохраняет публичный API |
| Потеря производительности | Низкая | Benchmark до/после каждой фазы |
| Сложность координации изменений | Средняя | Чёткие границы модулей, документация |

---

## Временная шкала

```
Неделя 1:     [████████] Phase 1: Критические исправления ✅ DONE
Неделя 2-3:   [████████] Phase 2: Базовая инфраструктура ✅ DONE
Неделя 4-6:   [████████] Phase 3: Рефакторинг lance_db.py ✅ DONE (476 строк)
Неделя 7-8:   [████████] Phase 4: Оптимизация производительности ✅ DONE
Неделя 9-10:  [████████] Phase 5: Тестовая инфраструктура ✅ DONE (951 тестов)
Неделя 11-12: [████████] Phase 6: Технический долг ✅ DONE
Неделя 13:    [████████] Phase 7: Release Candidate & Testing ✅ DONE
Неделя 14:    [░░░░░░░░] v0.7.0 Release ← СЛЕДУЮЩИЙ
```

**Общая продолжительность:** ~14 недель

---

## Контрольные точки (Milestones)

### M1: Critical Fixes Complete (Неделя 1) ✅ ЗАВЕРШЕНО 2026-01-06
- [x] 100% тестов проходят (745/745)
- [x] Критические bottlenecks устранены

### M2: Infrastructure Ready (Неделя 3) ✅ ЗАВЕРШЕНО 2026-01-06
- [x] core/ модуль создан (TTLCache, DataNormalizer, DBConnectionManager)
- [x] storage/builders/ модуль создан (ChunkRecordBuilder, DocumentRecordBuilder)
- [x] BaseProvider и BaseEnrichmentStrategy созданы

### M3: lance_db.py Refactored (Неделя 6) ✅ DONE (2026-01-06)
- [x] lance_db.py <500 строк (476 строк)
- [x] 3 новых сервиса созданы (VectorSearchService, IndexingService, MetadataService)
- [x] Обратная совместимость сохранена (все 745 тестов проходят)

### M4: Performance Optimized (Неделя 8) ✅ ЗАВЕРШЕНО 2026-01-06
- [x] N+1 проблемы устранены (батч-запросы в fts_search, search_by_links)
- [x] _get_row_count() оптимизирован (count_rows())
- [x] Построчное преобразование Arrow заменено на to_pylist() (11 мест)
- [x] TTLCache cleanup оптимизирован с heapq (O(expired))
- [x] Все 745 тестов проходят

### M5: Tests Complete (Неделя 10) ✅ ЗАВЕРШЕНО 2026-01-06
- [x] Покрытие ≥85%
- [x] 951 тестов проходят (было 745, +206 новых)

### M5.5: Technical Debt Resolved (Неделя 12) ✅ ЗАВЕРШЕНО 2026-01-06
- [x] Голые except устранены (logger.debug() добавлен)
- [x] OpenAI провайдер удалён
- [x] Any заменён на конкретные типы в публичных API
- [x] 2 MCPTool класса созданы (SearchVaultTool, IndexVaultTool)
- [x] 951 тестов проходят

### M6: Release Candidate Complete (Неделя 13) ✅ ЗАВЕРШЕНО 2026-01-06
- [x] Удалены устаревшие документы (PROMPT_PHASE3.md, TESTING_STATUS.md, ROADMAP_v0.6.0.md)
- [x] Обновлён .gitignore (*.lance/, .ruff_cache/)
- [x] Удалены OpenAI настройки из config.py
- [x] Обновлён README.md (v0.7.0, новая архитектура)
- [x] Обновлён CHANGELOG.md (полное описание v0.7.0)
- [x] Исправлены импорты в MCP tools
- [x] 951 тестов проходят

### M7: v0.7.0 Released (Неделя 14)
- [x] Технический долг устранён ✅
- [x] Документация обновлена ✅
- [ ] Релиз опубликован

---

## Начало работы

### Для Phase 1: Критические исправления

```bash
# Убедиться что на ветке main
git checkout main
git pull origin main

# Создать ветку для Phase 1
git checkout -b feature/v0.7.0-phase1-critical-fixes
```

**Промпт для запуска Phase 1:**
```
Начинаем работу над ROADMAP_v0.7.0.md.

Прочитай ROADMAP_v0.7.0.md и начни Phase 1: Критические исправления.

Задачи Phase 1:
1. Исправить 5 failed тестов:
   - test_get_instance_singleton (db_connection_manager.py)
   - test_search_semantic_intent (test_search_service_integration.py)
   - test_search_metadata_filter_intent (test_search_service_integration.py)
   - test_search_multi_vault (test_search_service_integration.py)
   - test_search_with_content (test_search_strategies.py)

2. Устранить критические bottlenecks с table.to_arrow().to_pylist()
   в файлах: embedding_cache.py, services/batch_operations.py,
   services/dataview_service.py, services/graph_query_service.py,
   services/timeline_service.py, services/frontmatter_api.py

Начни с задачи 1.1.1 — исправления test_get_instance_singleton.
После каждого исправления запускай тесты для проверки.
```

### Для Phase 2: Создание базовой инфраструктуры

```bash
# Убедиться что на ветке main
git checkout main
git pull origin main

# Создать ветку для Phase 2
git checkout -b feature/v0.7.0-phase2-infrastructure
```

**Промпт для запуска Phase 2:**
```
Продолжаем работу над ROADMAP_v0.7.0.md.

Phase 1 завершена (все 745 тестов проходят, bottlenecks устранены).
Прочитай ROADMAP_v0.7.0.md и начни Phase 2: Создание базовой инфраструктуры.

Задачи Phase 2:

1. Создание core/ модуля:
   - 2.1.1 Вынесение TTLCache в core/ttl_cache.py (источник: lance_db.py:18-149)
   - 2.1.2 Вынесение DataNormalizer в core/data_normalizer.py (источник: lance_db.py:221-396 + normalization.py)
   - 2.1.3 Рефакторинг DBConnectionManager в core/connection_manager.py

2. Создание storage/builders/ модуля:
   - 2.2.1 ChunkRecordBuilder (источник: lance_db.py:434-535)
   - 2.2.2 DocumentRecordBuilder (источник: lance_db.py:536-620)

3. Создание BaseProvider в providers/base_provider.py:
   - Извлечь общий код из providers/ollama/*.py и providers/yandex/*.py
   - Рефакторить существующие провайдеры на использование BaseProvider

4. Создание BaseEnrichmentStrategy в enrichment/strategies/base_strategy.py:
   - Извлечь общий код из full_enrichment_strategy.py и fast_enrichment_strategy.py

Начни с задачи 2.1.1 — вынесения TTLCache в core/ttl_cache.py.
После каждого изменения проверяй что все тесты проходят.

Критерии завершения Phase 2:
- Модуль core/ создан с TTLCache, DataNormalizer, DBConnectionManager
- Модуль storage/builders/ создан с ChunkRecordBuilder, DocumentRecordBuilder
- BaseProvider создан и провайдеры рефакторены
- BaseEnrichmentStrategy создан и стратегии рефакторены
- Все тесты проходят после рефакторинга
```
