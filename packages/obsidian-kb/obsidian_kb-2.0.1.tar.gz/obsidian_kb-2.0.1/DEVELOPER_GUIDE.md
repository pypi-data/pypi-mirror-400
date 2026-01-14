# Руководство для разработчиков obsidian-kb

**Версия:** 0.7.0
**Дата обновления:** 2026-01-06  
**Последние изменения:** Реализована полная архитектура с multi-provider support, hybrid indexing pipeline, background jobs и cost tracking. Все фазы разработки (Phase 1-7) завершены.

---

## Содержание

1. [Начало работы](#начало-работы)
2. [Архитектура проекта](#архитектура-проекта)
3. [Добавление нового фильтра](#добавление-нового-фильтра)
4. [Добавление новой стратегии поиска (v5)](#добавление-новой-стратегии-поиска-v5)
5. [Расширение Intent Detection (v5)](#расширение-intent-detection-v5)
6. [Добавление нового типа файла](#добавление-нового-типа-файла)
7. [Best Practices](#best-practices)
8. [Процесс тестирования](#процесс-тестирования)
9. [Отладка](#отладка)

---

## Начало работы

### Требования

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) — менеджер пакетов
- Ollama с моделью `nomic-embed-text`

### Установка зависимостей

```bash
# Клонировать репозиторий
git clone https://github.com/mdemyanov/obsidian-kb.git
cd obsidian-kb

# Установить зависимости
uv sync

# Активировать виртуальное окружение
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows
```

### Запуск тестов

```bash
# Все тесты
uv run pytest tests/

# Конкретный тест
uv run pytest tests/test_filters.py::TestTagFilter

# С покрытием
uv run pytest --cov=src/obsidian_kb tests/
```

### Линтинг и форматирование

```bash
# Проверка стиля
uv run ruff check src/

# Автоисправление
uv run ruff check --fix src/

# Форматирование
uv run ruff format src/
```

---

## Архитектура проекта

### Структура проекта

```
obsidian-kb/
├── src/obsidian_kb/          # Исходный код
│   ├── __init__.py          # Экспорты публичного API
│   ├── config.py            # Конфигурация (Pydantic Settings)
│   ├── types.py             # Типы данных (Pydantic модели)
│   ├── service_container.py # Dependency Injection контейнер
│   ├── vault_indexer.py      # Индексация vault'ов
│   ├── frontmatter_parser.py # Парсинг frontmatter
│   ├── embedding_service.py # Генерация embeddings (Ollama)
│   ├── lance_db.py          # Работа с LanceDB
│   ├── query_parser.py       # Парсинг поисковых запросов
│   ├── filters.py            # Построение SQL фильтров
│   ├── search_optimizer.py   # Оптимизация поиска
│   ├── interfaces.py        # Интерфейсы (Protocol)
│   ├── mcp_server.py        # MCP интерфейс
│   └── cli.py               # CLI интерфейс
├── tests/                    # Тесты
│   ├── test_filters.py      # Тесты фильтров
│   ├── test_query_parser.py # Тесты парсера
│   ├── test_integration.py  # Интеграционные тесты
│   └── ...
├── pyproject.toml           # Зависимости и метаданные
└── README.md                # Документация
```

### Основные компоненты

Подробное описание архитектуры см. в [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Добавление нового фильтра

### Шаг 1: Создать класс фильтра

Создайте новый класс фильтра в `src/obsidian_kb/filters.py`:

```python
class NewFilter:
    """Фильтр по новому полю."""
    
    @staticmethod
    def build_condition(value: str, operator: str = "=") -> FilterCondition:
        """Построение условия фильтрации.
        
        Args:
            value: Значение для фильтрации
            operator: Оператор сравнения (=, !=, >, <, >=, <=)
            
        Returns:
            FilterCondition с SQL условием
        """
        if not value:
            return FilterCondition("")
        
        # Нормализация значения (если нужно)
        normalized_value = DataNormalizer.normalize_value(value)
        
        # Экранирование SQL
        safe_value = DataNormalizer.escape_sql_string(normalized_value)
        
        # Построение SQL условия
        sql = f"new_field {operator} '{safe_value}'"
        
        return FilterCondition(sql)
```

**Важно:**
- Всегда экранируйте значения через `DataNormalizer.escape_sql_string()`
- Нормализуйте значения через `DataNormalizer` (если нужно)
- Возвращайте пустой `FilterCondition("")` для пустых значений

### Шаг 2: Добавить парсинг в QueryParser

Добавьте парсинг нового фильтра в `src/obsidian_kb/query_parser.py`:

```python
# В методе QueryParser.parse()

# Парсинг нового фильтра
new_filter_pattern = r'newfilter:([^\s]+)'
new_filter_matches = re.findall(new_filter_pattern, query)
if new_filter_matches:
    parsed_query.new_filter = new_filter_matches[0]
    # Удаляем фильтр из текстового запроса
    query = re.sub(new_filter_pattern, '', query)
```

**Примеры паттернов:**
- `r'newfilter:([^\s]+)'` — простое значение
- `r'newfilter:([^"\s]+|"[^"]+")'` — значение с кавычками
- `r'newfilter:(>=?|<=?|!=|=)?([^\s]+)'` — с оператором

### Шаг 3: Добавить использование в FilterBuilder

Добавьте использование нового фильтра в `src/obsidian_kb/filters.py`:

```python
# В методе FilterBuilder.build_where_clause()

# Новый фильтр
if new_filter:
    new_filter_condition = NewFilter.build_condition(new_filter)
    if new_filter_condition.sql:
        conditions.append(new_filter_condition.sql)
```

**Добавьте параметр в сигнатуру метода:**
```python
@staticmethod
def build_where_clause(
    # ... существующие параметры ...
    new_filter: str | None = None,
) -> str | None:
```

### Шаг 4: Обновить ParsedQuery

Добавьте поле в `ParsedQuery` в `src/obsidian_kb/query_parser.py`:

```python
@dataclass
class ParsedQuery:
    # ... существующие поля ...
    new_filter: str | None = None
```

### Шаг 5: Добавить тесты

Создайте тесты в `tests/test_filters.py`:

```python
class TestNewFilter:
    """Тесты для NewFilter."""
    
    def test_build_condition_single_value(self):
        """Тест построения условия для одного значения."""
        condition = NewFilter.build_condition("value")
        assert "new_field = 'value'" in condition.sql
    
    def test_build_condition_with_operator(self):
        """Тест построения условия с оператором."""
        condition = NewFilter.build_condition("value", operator=">")
        assert "new_field > 'value'" in condition.sql
    
    def test_build_condition_empty(self):
        """Тест построения условия для пустого значения."""
        condition = NewFilter.build_condition("")
        assert condition.sql == ""
    
    def test_build_condition_normalizes_value(self):
        """Тест нормализации значения."""
        condition = NewFilter.build_condition("Value")
        assert "new_field = 'value'" in condition.sql  # lowercase
```

**Добавьте интеграционные тесты в `tests/test_query_parser.py`:**

```python
def test_parse_new_filter():
    """Тест парсинга нового фильтра."""
    parser = QueryParser()
    parsed = parser.parse("query newfilter:value")
    
    assert parsed.new_filter == "value"
    assert parsed.text_query == "query"
```

### Шаг 6: Обновить документацию

1. Добавьте описание фильтра в [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. Добавьте примеры в [ADVANCED_SEARCH.md](ADVANCED_SEARCH.md)
3. Обновите `search_help()` в `mcp_server.py`

### Пример: Добавление фильтра `author:`

```python
# 1. Создать класс фильтра
class AuthorFilter:
    """Фильтр по автору."""
    
    @staticmethod
    def build_condition(author: str) -> FilterCondition:
        if not author:
            return FilterCondition("")
        
        normalized_author = DataNormalizer.normalize_value(author)
        safe_author = DataNormalizer.escape_sql_string(normalized_author)
        sql = f"author = '{safe_author}'"
        return FilterCondition(sql)

# 2. Добавить парсинг
author_pattern = r'author:([^\s]+)'
author_matches = re.findall(author_pattern, query)
if author_matches:
    parsed_query.author = author_matches[0]
    query = re.sub(author_pattern, '', query)

# 3. Добавить использование
if author:
    author_condition = AuthorFilter.build_condition(author)
    if author_condition.sql:
        conditions.append(author_condition.sql)
```

---

## Добавление новой стратегии поиска (v5)

В v5 система использует паттерн Strategy для выполнения поиска. Вы можете добавить новую стратегию для реализации специфичной логики поиска.

### Шаг 1: Создать класс стратегии

Создайте новый файл в `src/obsidian_kb/search/strategies/`:

```python
# src/obsidian_kb/search/strategies/custom_strategy.py

from typing import TYPE_CHECKING, Any

from obsidian_kb.search.strategies.base import BaseSearchStrategy
from obsidian_kb.types import DocumentSearchResult

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IDocumentRepository


class CustomStrategy(BaseSearchStrategy):
    """Кастомная стратегия поиска.
    
    Описание того, для каких случаев используется эта стратегия.
    """
    
    def __init__(
        self,
        document_repo: "IDocumentRepository",
        # Добавьте дополнительные зависимости если нужно
    ) -> None:
        """Инициализация стратегии.
        
        Args:
            document_repo: Репозиторий документов
        """
        super().__init__(document_repo)
        # Инициализация дополнительных зависимостей
    
    @property
    def name(self) -> str:
        """Имя стратегии для логирования."""
        return "custom"
    
    async def search(
        self,
        vault_name: str,
        query: str,
        parsed_filters: dict[str, Any],
        limit: int = 10,
        options: dict[str, Any] | None = None,
    ) -> list[DocumentSearchResult]:
        """Выполнение поиска согласно стратегии.
        
        Args:
            vault_name: Имя vault'а
            query: Текстовый запрос (может быть пустым)
            parsed_filters: Извлечённые фильтры
            limit: Максимум результатов
            options: Дополнительные опции
            
        Returns:
            Список результатов поиска
        """
        options = options or {}
        
        # 1. Применение фильтров (если нужно)
        document_ids = await self._apply_filters(vault_name, parsed_filters)
        
        # 2. Ваша логика поиска
        # ...
        
        # 3. Получение документов
        documents = await self._documents.get_many(vault_name, document_ids)
        
        # 4. Построение результатов
        results = []
        for doc in documents[:limit]:
            # Создание DocumentSearchResult
            result = DocumentSearchResult(
                document=doc,
                score=RelevanceScore.exact_match(),  # Или ваша логика scoring
                matched_chunks=[],
                matched_sections=[],
            )
            results.append(result)
        
        return results
```

### Шаг 2: Зарегистрировать стратегию в SearchService

Обновите `src/obsidian_kb/search/service.py`:

```python
from obsidian_kb.search.strategies.custom_strategy import CustomStrategy

class SearchService:
    def __init__(self, ...):
        # ...
        self._strategies: dict[str, "ISearchStrategy"] = {
            "document_level": DocumentLevelStrategy(document_repo),
            "chunk_level": ChunkLevelStrategy(...),
            "custom": CustomStrategy(document_repo),  # Новая стратегия
        }
```

### Шаг 3: Добавить выбор стратегии

Если стратегия должна выбираться автоматически, обновите метод `_select_strategy()`:

```python
def _select_strategy(self, granularity: RetrievalGranularity) -> "ISearchStrategy":
    """Выбор стратегии на основе granularity или других условий."""
    if granularity == RetrievalGranularity.DOCUMENT:
        return self._strategies["document_level"]
    elif granularity == RetrievalGranularity.CUSTOM:  # Новый тип
        return self._strategies["custom"]
    return self._strategies["chunk_level"]
```

### Шаг 4: Добавить тесты

Создайте тесты в `tests/test_custom_strategy.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from obsidian_kb.search.strategies.custom_strategy import CustomStrategy

@pytest.fixture
def mock_document_repo():
    repo = MagicMock()
    repo.get_many = AsyncMock(return_value=[])
    repo.find_by_tags = AsyncMock(return_value=set())
    return repo

@pytest.mark.asyncio
async def test_custom_strategy_search(mock_document_repo):
    """Тест кастомной стратегии."""
    strategy = CustomStrategy(mock_document_repo)
    
    results = await strategy.search(
        vault_name="test",
        query="test",
        parsed_filters={},
        limit=10,
    )
    
    assert isinstance(results, list)
    assert all(isinstance(r, DocumentSearchResult) for r in results)
```

### Примеры использования

**Пример 1: Стратегия для поиска по связанным документам**

```python
class RelatedDocumentsStrategy(BaseSearchStrategy):
    """Стратегия поиска связанных документов через wikilinks."""
    
    async def search(self, vault_name, query, parsed_filters, limit, options):
        # Получаем документ по query (если это имя файла)
        doc = await self._documents.get(vault_name, f"{vault_name}::{query}")
        if not doc:
            return []
        
        # Получаем связанные документы через links
        related_ids = set()
        for link in doc.links:
            # Поиск документов с этим link
            # ...
        
        # Получаем связанные документы
        related_docs = await self._documents.get_many(vault_name, related_ids)
        
        # Строим результаты
        return [DocumentSearchResult(...) for doc in related_docs]
```

---

## Расширение Intent Detection (v5)

Вы можете расширить IntentDetector для поддержки новых типов intent или улучшения точности определения.

### Шаг 1: Добавить новый тип Intent

Обновите `src/obsidian_kb/types.py`:

```python
class SearchIntent(Enum):
    METADATA_FILTER = "metadata_filter"
    KNOWN_ITEM = "known_item"
    SEMANTIC = "semantic"
    EXPLORATORY = "exploratory"
    PROCEDURAL = "procedural"
    CUSTOM_INTENT = "custom_intent"  # Новый тип
```

### Шаг 2: Добавить логику определения в IntentDetector

Обновите `src/obsidian_kb/search/intent_detector.py`:

```python
class IntentDetector:
    # Добавьте паттерны для нового intent
    CUSTOM_PATTERNS = [
        r'\bcustom\b',
        r'\bpattern\b',
    ]
    
    def detect(self, query: str, parsed_filters: dict[str, Any]) -> IntentDetectionResult:
        # ... существующая логика ...
        
        # Добавьте проверку нового intent перед SEMANTIC
        if has_text and any(re.search(p, query, re.IGNORECASE) for p in self.CUSTOM_PATTERNS):
            signals['custom_pattern'] = True
            return IntentDetectionResult(
                intent=SearchIntent.CUSTOM_INTENT,
                confidence=0.85,
                signals=signals,
                recommended_granularity=RetrievalGranularity.DOCUMENT,  # Или CHUNK
            )
        
        # ... остальная логика ...
```

### Шаг 3: Обновить маппинг intent → granularity

Обновите `SearchService._intent_to_granularity()`:

```python
@staticmethod
def _intent_to_granularity(intent: SearchIntent) -> RetrievalGranularity:
    """Маппинг intent → granularity."""
    document_intents = {
        SearchIntent.METADATA_FILTER,
        SearchIntent.KNOWN_ITEM,
        SearchIntent.PROCEDURAL,
        SearchIntent.CUSTOM_INTENT,  # Новый intent
    }
    if intent in document_intents:
        return RetrievalGranularity.DOCUMENT
    return RetrievalGranularity.CHUNK
```

### Шаг 4: Добавить тесты

Создайте тесты в `tests/test_intent_detector.py`:

```python
def test_custom_intent_detection():
    """Тест определения custom intent."""
    detector = IntentDetector()
    result = detector.detect("custom pattern", {})
    
    assert result.intent == SearchIntent.CUSTOM_INTENT
    assert result.confidence >= 0.8
```

### Рекомендации по улучшению точности

1. **Добавьте больше паттернов** — чем больше паттернов, тем выше точность
2. **Используйте сигналы** — сохраняйте информацию о том, почему intent был определён
3. **Настройте confidence** — используйте разные уровни уверенности для разных случаев
4. **Тестируйте на реальных данных** — используйте `tests/intent_test_queries.md` для проверки

### Пример: Улучшение определения KNOWN_ITEM

```python
class IntentDetector:
    # Расширенный список паттернов
    FILE_PATTERNS = [
        r'\b[\w-]+\.(md|pdf|txt)\b',
        r'\b(README|CHANGELOG|LICENSE|TODO|CONTRIBUTING|INSTALLATION)\b',
        r'\b[A-Z][A-Z_]+\.md\b',  # Файлы в UPPERCASE
        r'^[\w-]+\.md$',  # Только имя файла
    ]
    
    def detect(self, query: str, parsed_filters: dict[str, Any]) -> IntentDetectionResult:
        # Проверка на known-item с более строгими условиями
        if has_text:
            # Проверяем, что запрос похож на имя файла
            is_file_like = any(re.search(p, query, re.IGNORECASE) for p in self.FILE_PATTERNS)
            is_short = len(query.split()) <= 2  # Короткий запрос
            
            if is_file_like and is_short:
                return IntentDetectionResult(
                    intent=SearchIntent.KNOWN_ITEM,
                    confidence=0.95,  # Высокая уверенность
                    signals={"file_reference": True, "short_query": True},
                    recommended_granularity=RetrievalGranularity.DOCUMENT,
                )
```

---

## Добавление нового типа файла

### Шаг 1: Создать парсер файла

Создайте парсер в `src/obsidian_kb/file_parsers.py`:

```python
class NewFileParser:
    """Парсер для нового типа файла."""
    
    @staticmethod
    async def parse(
        file_path: Path,
        vault_name: str,
        indexer: VaultIndexer
    ) -> list[DocumentChunk]:
        """Парсинг файла нового типа.
        
        Args:
            file_path: Путь к файлу
            vault_name: Имя vault'а
            indexer: Индексатор для доступа к утилитам
            
        Returns:
            Список чанков документа
        """
        # Чтение файла
        content = await asyncio.to_thread(file_path.read_text, encoding="utf-8")
        
        # Парсинг содержимого
        # ...
        
        # Создание чанков
        chunks = []
        for i, section in enumerate(sections):
            chunk = DocumentChunk(
                id=f"{vault_name}::{file_path.relative_to(vault_path)}::{i}",
                vault_name=vault_name,
                file_path=str(file_path.relative_to(vault_path)),
                title=section.title,
                content=section.content,
                # ... другие поля ...
            )
            chunks.append(chunk)
        
        return chunks
```

### Шаг 2: Зарегистрировать парсер в VaultIndexer

Добавьте обработку нового типа файла в `src/obsidian_kb/vault_indexer.py`:

```python
# В методе VaultIndexer._scan_file()

async def _scan_file(self, file_path: Path) -> list[DocumentChunk]:
    """Сканирование файла."""
    
    # Существующие обработчики
    if file_path.suffix == ".md":
        return await self._scan_markdown_file(file_path)
    
    # Новый тип файла
    if file_path.suffix == ".new":
        from obsidian_kb.file_parsers import NewFileParser
        return await NewFileParser.parse(file_path, self.vault_name, self)
    
    return []
```

### Шаг 3: Обновить ignore_patterns (если нужно)

Если новый тип файла должен игнорироваться по умолчанию, добавьте паттерн в `src/obsidian_kb/ignore_patterns.py`:

```python
DEFAULT_IGNORE_PATTERNS = [
    # ... существующие паттерны ...
    "*.new",  # Игнорировать файлы .new
]
```

### Шаг 4: Добавить тесты

Создайте тесты в `tests/test_file_parsers.py`:

```python
class TestNewFileParser:
    """Тесты для NewFileParser."""
    
    @pytest.mark.asyncio
    async def test_parse_new_file(self, tmp_path):
        """Тест парсинга нового типа файла."""
        # Создать тестовый файл
        test_file = tmp_path / "test.new"
        test_file.write_text("test content")
        
        # Парсинг
        parser = NewFileParser()
        chunks = await parser.parse(test_file, "test-vault", mock_indexer)
        
        # Проверки
        assert len(chunks) > 0
        assert chunks[0].content == "test content"
```

### Пример: Добавление поддержки `.txt` файлов

```python
# 1. Создать парсер
class TextFileParser:
    """Парсер для текстовых файлов."""
    
    @staticmethod
    async def parse(
        file_path: Path,
        vault_name: str,
        indexer: VaultIndexer
    ) -> list[DocumentChunk]:
        content = await asyncio.to_thread(file_path.read_text, encoding="utf-8")
        
        # Разбить на чанки по параграфам
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        
        chunks = []
        for i, para in enumerate(paragraphs):
            chunk = DocumentChunk(
                id=f"{vault_name}::{file_path.name}::{i}",
                vault_name=vault_name,
                file_path=str(file_path.name),
                title=file_path.stem,
                content=para[:600],  # Макс 600 символов
            )
            chunks.append(chunk)
        
        return chunks

# 2. Зарегистрировать
if file_path.suffix == ".txt":
    from obsidian_kb.file_parsers import TextFileParser
    return await TextFileParser.parse(file_path, self.vault_name, self)
```

---

## Best Practices

### 1. Обработка ошибок

Всегда используйте специализированные исключения из `obsidian_kb.types`:

```python
from obsidian_kb.types import ObsidianKBError, IndexingError

try:
    # Код
except Exception as e:
    raise IndexingError(f"Failed to index file: {e}") from e
```

**Типы исключений:**
- `ObsidianKBError` — базовое исключение
- `IndexingError` — ошибки индексации
- `VaultNotFoundError` — vault не найден
- `OllamaConnectionError` — ошибки подключения к Ollama
- `DatabaseError` — ошибки БД
- `ValidationError` — ошибки валидации

### 2. Асинхронность

Используйте асинхронные функции для I/O операций:

```python
# ✅ Правильно
async def read_file(file_path: Path) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, file_path.read_text, "utf-8")

# ❌ Неправильно (блокирует event loop)
async def read_file(file_path: Path) -> str:
    return file_path.read_text("utf-8")  # Синхронный I/O
```

### 3. Нормализация данных

Всегда нормализуйте данные через `DataNormalizer`:

```python
from obsidian_kb.normalization import DataNormalizer

# Нормализация тегов
normalized_tag = DataNormalizer.normalize_tag("Python")  # → "python"

# Нормализация типов документов
normalized_type = DataNormalizer.normalize_doc_type("Протокол")  # → "протокол"

# Нормализация ссылок
normalized_link = DataNormalizer.normalize_link("[[Python Guide]]")  # → "python guide"
```

### 4. Экранирование SQL

Всегда экранируйте значения для SQL:

```python
from obsidian_kb.normalization import DataNormalizer

# Экранирование строк
safe_value = DataNormalizer.escape_sql_string(user_input)
sql = f"field = '{safe_value}'"
```

### 5. Логирование

Используйте структурированное логирование:

```python
import logging

logger = logging.getLogger(__name__)

# Логирование с контекстом
logger.info("Indexing file", extra={
    "file_path": str(file_path),
    "vault_name": vault_name,
    "chunks_count": len(chunks)
})
```

### 6. Типизация

Используйте типы из `typing` и Pydantic модели:

```python
from typing import list, dict, Any
from obsidian_kb.types import DocumentChunk

def process_chunks(chunks: list[DocumentChunk]) -> dict[str, Any]:
    # ...
```

### 7. Валидация входных данных

Валидируйте входные данные через функции из `validation.py`:

```python
from obsidian_kb.validation import validate_search_params, ValidationError

try:
    validate_search_params(query=query, vault_name=vault_name, limit=limit)
except ValidationError as e:
    raise
```

### 8. Connection Pooling

Используйте `DBConnectionManager` для работы с БД:

```python
from obsidian_kb.db_connection_manager import DBConnectionManager

db_manager = DBConnectionManager.get_instance()

with db_manager.get_connection() as db:
    table = db.open_table("vault_my_vault")
    # Работа с таблицей
```

### 9. Кэширование

Используйте `EmbeddingCache` для кэширования embeddings:

```python
from obsidian_kb.embedding_cache import EmbeddingCache

cache = EmbeddingCache()
cached_embeddings = await cache.get_cached_embeddings(texts, model_name)
```

### 10. Тестирование

Пишите тесты для всех новых функций:

```python
import pytest

@pytest.mark.asyncio
async def test_new_function():
    # Arrange
    input_data = "test"
    
    # Act
    result = await new_function(input_data)
    
    # Assert
    assert result == expected_output
```

---

## Процесс тестирования

### Использование ServiceContainer в тестах

Для тестирования с dependency injection используйте `ServiceContainer`:

```python
import pytest
import asyncio
from pathlib import Path
from obsidian_kb.service_container import ServiceContainer, reset_service_container

@pytest.fixture
def service_container(temp_db):
    """Создание контейнера сервисов для тестов."""
    # Сбрасываем глобальный контейнер перед каждым тестом
    reset_service_container()
    container = ServiceContainer(db_path=temp_db)
    yield container
    # Очищаем ресурсы после теста
    try:
        asyncio.run(container.cleanup())
    except Exception:
        pass
    reset_service_container()

@pytest.mark.asyncio
async def test_with_service_container(service_container):
    """Пример теста с использованием ServiceContainer."""
    db_manager = service_container.db_manager
    embedding_service = service_container.embedding_service
    
    # Использование сервисов...
    results = await db_manager.vector_search(...)
```

**Преимущества:**
- Изоляция тестов (каждый тест получает свой контейнер)
- Легкая подмена зависимостей для моков
- Автоматическая очистка ресурсов

### Старый способ (без ServiceContainer)

Если нужно создать сервисы напрямую (для unit-тестов):

```python
from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.embedding_service import EmbeddingService

@pytest.fixture
def db_manager(temp_db):
    return LanceDBManager(db_path=temp_db)

@pytest.fixture
def embedding_service():
    return EmbeddingService()
```

## Процесс тестирования (продолжение)

### Структура тестов

Тесты организованы по модулям:

```
tests/
├── test_filters.py          # Тесты фильтров
├── test_query_parser.py     # Тесты парсера
├── test_indexer.py          # Тесты индексации
├── test_lancedb.py          # Тесты БД
├── test_embedding.py        # Тесты embeddings
├── test_cto_vault_scenarios.py  # Тесты на тестовых данных CTO vault
├── test_data/               # Тестовые данные
│   └── cto_vault/          # Тестовый vault для автоматического тестирования
└── conftest.py             # Фикстуры
```

### Тестирование на тестовых данных CTO vault

Для качественного автоматического тестирования создан структурированный набор тестовых данных, имитирующий реальную базу знаний руководителя ИТ-компании.

**Расположение:** `tests/test_data/cto_vault/`

**Структура:**
- `01_CONTEXT/` — организационная информация
- `02_TECHNOLOGY/` — технологические решения
- `03_METHODOLOGY/` — методология
- `04_TEMPLATES/` — шаблоны документов
- `05_DECISIONS/` — архитектурные решения (ADR)
- `06_CURRENT/projects/` — текущие проекты
- `07_PEOPLE/` — профили людей и встречи 1-1
- `08_COMMITTEES/` — комитеты и протоколы

**Запуск тестов:**

```bash
# Запуск всех тестовых сценариев на тестовых данных
uv run python tests/test_cto_vault_scenarios.py
```

**Что тестируется:**
- Поиск по метаданным (type, tags, links, dates)
- Поиск известных документов (KNOWN_ITEM)
- Семантический поиск (SEMANTIC)
- Исследовательские вопросы (EXPLORATORY)
- How-to запросы (PROCEDURAL)
- Комплексные запросы

**Ожидаемый результат:** Все 24 тестовых сценария должны проходить успешно (100%).

**Документация:**
- `tests/test_data/README.md` — описание тестовых данных
- `tests/TEST_DATA_GUIDE.md` — руководство по использованию
- `tests/FIXES_SUMMARY.md` — сводка исправлений

**Важно:** Тестирование на тестовых данных включено в обязательный процесс проверки качества проекта (`tests/final_check.py`).

### Запуск тестов

```bash
# Все тесты
uv run pytest

# Конкретный файл
uv run pytest tests/test_filters.py

# Конкретный тест
uv run pytest tests/test_filters.py::TestTagFilter::test_build_condition_single_tag

# С покрытием
uv run pytest --cov=src/obsidian_kb --cov-report=html

# С verbose выводом
uv run pytest -v

# Остановка на первой ошибке
uv run pytest -x
```

### Фикстуры

Используйте фикстуры из `conftest.py`:

```python
@pytest.fixture
def sample_vault_path(tmp_path):
    """Создать тестовый vault."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    return vault_path

@pytest.fixture
def sample_chunks():
    """Создать тестовые чанки."""
    return [
        DocumentChunk(
            id="test::file.md::0",
            vault_name="test",
            file_path="file.md",
            content="test content",
            # ...
        )
    ]
```

### Моки

Используйте `unittest.mock` для мокирования:

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_with_mock():
    # Мокирование асинхронной функции
    mock_service = AsyncMock()
    mock_service.get_embedding.return_value = [0.1] * 1024
    
    # Использование мока
    result = await mock_service.get_embedding("test")
    assert len(result) == 1024
```

### Интеграционные тесты

Для интеграционных тестов используйте реальные компоненты:

```python
@pytest.mark.asyncio
async def test_integration_search(tmp_path):
    """Интеграционный тест поиска."""
    # Создать тестовый vault
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    
    # Создать тестовый файл
    test_file = vault_path / "test.md"
    test_file.write_text("---\ntitle: Test\n---\n# Test\nContent")
    
    # Индексировать
    indexer = VaultIndexer(vault_path, "test")
    chunks = await indexer.scan_all()
    
    # Поиск
    db_manager = LanceDBManager(tmp_path / "test.lance")
    await db_manager.upsert_chunks("test", chunks, [[0.1] * 1024] * len(chunks))
    
    results = await db_manager.hybrid_search("test", "Content", limit=10)
    assert len(results) > 0
```

---

## Отладка

### Логирование

Включите детальное логирование:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Диагностические команды

Используйте диагностические команды:

```bash
# Проверка системы
obsidian-kb doctor

# Проверка индексации
obsidian-kb check-index --vault "my-vault"

# Проверка покрытия индекса
obsidian-kb index-coverage --vault "my-vault"

# Проверка метрик
obsidian-kb check-metrics --days 7
```

### Отладка в IDE

Используйте отладчик IDE:

```python
# Точка останова
import pdb; pdb.set_trace()

# Или используйте breakpoint() (Python 3.7+)
breakpoint()
```

### Профилирование

Профилирование производительности:

```bash
# Профилирование с cProfile
python -m cProfile -o profile.stats script.py

# Анализ профиля
python -m pstats profile.stats
```

---

## Ссылки

- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура системы
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) — документация API
- [CONTRIBUTING.md](CONTRIBUTING.md) — руководство по внесению вклада
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) — схема базы данных

