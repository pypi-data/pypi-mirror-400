# Миграция на v1.0.0

Руководство по миграции с версий v0.x на v1.0.0.

---

## Содержание

1. [Обзор изменений](#обзор-изменений)
2. [Breaking Changes](#breaking-changes)
3. [Deprecated API](#deprecated-api)
4. [Миграция кода](#миграция-кода)
5. [Миграция конфигурации](#миграция-конфигурации)
6. [Переиндексация данных](#переиндексация-данных)

---

## Обзор изменений

v1.0.0 — первый production-ready релиз с полной поддержкой multi-provider архитектуры.

### Ключевые изменения

| Компонент | v0.x | v1.0.0 |
|-----------|------|--------|
| Enrichment providers | Только Ollama (hardcoded) | Любой провайдер через IChatCompletionProvider |
| Enrichment status | Скрыт | Прозрачный (success/fallback/skipped) |
| Rate limiting | Фиксированный | Адаптивный с backoff |
| Error handling | OllamaConnectionError | Единая иерархия ProviderError |

---

## Breaking Changes

### 1. Удалён прямой HTTP доступ к Ollama в enrichment

**Было (v0.x):**
```python
from obsidian_kb.enrichment.strategies import FullEnrichmentStrategy

# Прямое указание Ollama URL
strategy = FullEnrichmentStrategy(
    base_url="http://localhost:11434",
    model="llama3.2"
)
```

**Стало (v1.0.0):**
```python
from obsidian_kb.enrichment.strategies import FullEnrichmentStrategy
from obsidian_kb.providers import OllamaChatProvider

# Через IChatCompletionProvider
chat_provider = OllamaChatProvider(
    base_url="http://localhost:11434",
    model="llama3.2"
)
strategy = FullEnrichmentStrategy(chat_provider=chat_provider)
```

### 2. EnrichedChunk содержит новые поля

**Было (v0.x):**
```python
@dataclass
class EnrichedChunk:
    chunk_info: ChunkInfo
    context_prefix: str
    provider_info: dict[str, str] | None = None
```

**Стало (v1.0.0):**
```python
@dataclass
class EnrichedChunk:
    chunk_info: ChunkInfo
    context_prefix: str
    provider_info: dict[str, str] | None = None
    enrichment_status: Literal["success", "fallback", "skipped"] = "success"
    error_message: str | None = None
```

### 3. IndexingResult содержит enrichment_stats

**Было (v0.x):**
```python
@dataclass
class IndexingResult:
    job_id: str
    documents_processed: int
    documents_total: int
    chunks_created: int
    errors: list[str]
    duration_seconds: float
```

**Стало (v1.0.0):**
```python
@dataclass
class IndexingResult:
    job_id: str
    documents_processed: int
    documents_total: int
    chunks_created: int
    errors: list[str]
    duration_seconds: float
    enrichment_stats: EnrichmentStats | None = None  # Новое
    warnings: list[str] = field(default_factory=list)  # Новое
```

---

## Deprecated API

### OllamaConnectionError

`OllamaConnectionError` помечен как deprecated. При использовании будет выводиться DeprecationWarning.

**Было:**
```python
from obsidian_kb.types import OllamaConnectionError

try:
    result = await strategy.enrich(chunk)
except OllamaConnectionError as e:
    logger.warning(f"Ollama connection error: {e}")
```

**Рекомендуется:**
```python
from obsidian_kb.providers.exceptions import ProviderConnectionError, ProviderError

try:
    result = await strategy.enrich(chunk)
except ProviderConnectionError as e:
    logger.warning(f"Provider connection error: {e}")
except ProviderError as e:
    logger.warning(f"Provider error: {e}")
```

### Иерархия ProviderError

Новая унифицированная иерархия ошибок:

```python
from obsidian_kb.providers.exceptions import (
    ProviderError,           # Базовый класс
    ProviderConnectionError, # Ошибки соединения
    ProviderRateLimitError,  # Rate limit (429)
    ProviderTimeoutError,    # Таймауты
    ProviderAuthError,       # Ошибки авторизации
)
```

---

## Миграция кода

### Обновление enrichment стратегий

Если вы создавали собственные enrichment стратегии или использовали FullEnrichmentStrategy напрямую:

```python
# v0.x
from obsidian_kb.enrichment.strategies import FullEnrichmentStrategy

strategy = FullEnrichmentStrategy(
    base_url=ollama_url,
    model=model_name,
)

# v1.0.0
from obsidian_kb.enrichment.strategies import FullEnrichmentStrategy
from obsidian_kb.service_container import get_service_container

# Получение провайдера из ServiceContainer
services = get_service_container()
chat_provider = services.enrichment_chat_provider

strategy = FullEnrichmentStrategy(chat_provider=chat_provider)
```

### Обработка результатов enrichment

```python
# v1.0.0 — проверка статуса обогащения
for chunk in enriched_chunks:
    if chunk.enrichment_status == "success":
        print(f"Успешно обогащено: {chunk.context_prefix[:50]}...")
    elif chunk.enrichment_status == "fallback":
        print(f"Fallback: {chunk.error_message}")
    elif chunk.enrichment_status == "skipped":
        print("Обогащение пропущено")
```

### Мониторинг статистики enrichment

```python
# v1.0.0 — получение статистики через job status
from obsidian_kb.indexing import BackgroundJobQueue

job_queue = BackgroundJobQueue()
job = job_queue.get_job(job_id)

if job.enrichment_stats:
    stats = job.enrichment_stats
    print(f"Всего чанков: {stats.total_chunks}")
    print(f"Успешно: {stats.enriched_ok}")
    print(f"Fallback: {stats.enriched_fallback}")
    print(f"Ошибок: {len(stats.errors)}")
```

---

## Миграция конфигурации

### Yandex Provider с адаптивным rate limiting

v1.0.0 автоматически использует адаптивный rate limiting для Yandex провайдера.

Настройки по умолчанию:
- `initial_rps`: 20
- `max_rps`: 100
- `min_rps`: 2
- `recovery_threshold`: 30 успешных запросов

Эти настройки оптимальны для большинства случаев. При необходимости можно изменить через ProviderConfig:

```python
from obsidian_kb.providers import ProviderConfig

config = ProviderConfig(
    max_concurrent=50,
    batch_size=100,
    enrichment_concurrent=10,
    rate_limit_rps=20,
    timeout=30,
    adaptive_rate_limit=True,
    rate_limit_min_rps=2.0,
    rate_limit_recovery=30,
)
```

---

## Переиндексация данных

### Нужна ли переиндексация?

**Переиндексация НЕ требуется** при обновлении с v0.9.x на v1.0.0:
- Схема базы данных не изменилась
- Формат хранения данных совместим

**Переиндексация рекомендуется** если вы хотите:
- Использовать новый провайдер для enrichment
- Получить улучшенные context prefix от нового провайдера
- Обновить enrichment_status для существующих чанков

### Процесс переиндексации

```bash
# 1. Проверка текущего состояния
obsidian-kb stats --vault "my-vault"

# 2. Переиндексация с новым провайдером
obsidian-kb reindex --vault "my-vault" --force

# 3. Проверка результатов
obsidian-kb stats --vault "my-vault"
```

### Через MCP

```python
# Переиндексация через агента
reindex_vault("my-vault", confirm=True, enrichment="contextual")

# Проверка статуса
index_status(vault_name="my-vault")
```

---

## Проверка миграции

После миграции выполните проверку:

```bash
# 1. Запуск тестов (для разработчиков)
.venv/bin/pytest tests/ -x -q

# 2. Проверка здоровья системы
obsidian-kb doctor

# 3. Проверка провайдеров
# Через MCP: list_providers()
# Через MCP: test_provider("ollama")

# 4. Тестовый поиск
obsidian-kb search --vault "my-vault" --query "test query"
```

---

## Помощь

При возникновении проблем:

1. Проверьте [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Создайте issue на GitHub с описанием проблемы
3. Укажите версию v0.x с которой мигрируете

---

## Ссылки

- [CHANGELOG.md](CHANGELOG.md) — полный список изменений
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) — документация API
- [PROVIDERS.md](PROVIDERS.md) — руководство по провайдерам
