# Roadmap v0.10.0 → v1.0.0: Multi-Provider Enrichment Release

**Дата начала:** 2026-01-07
**Текущая версия:** 0.9.1
**Промежуточный релиз:** v0.10.0 (унификация enrichment + прозрачность)
**Финальный релиз:** v1.0.0 (адаптивный rate limiting + документация)
**Цель:** Стабильный production-ready релиз с полной поддержкой multi-provider

---

## Готовность к 1.0.0

### Что уже сделано (v0.7.0 - v0.9.1)

| Компонент | Статус | Описание |
|-----------|--------|----------|
| Архитектура | ✅ Готово | Слоистая архитектура, Facade pattern, DI через ServiceContainer |
| Тесты | ✅ Готово | 997 тестов, покрытие ≥85% |
| Поиск | ✅ Готово | Adaptive Search v5, hybrid search, intent detection |
| Индексация | ✅ Готово | Background jobs, parallel enrichment, change detection |
| Провайдеры | ⚠️ Почти | Ollama + Yandex работают, но enrichment не унифицирован |
| Стабильность | ⚠️ Почти | Graceful degradation есть, но нет прозрачности ошибок |
| Документация | ⚠️ Частично | README есть, но нет полной API документации |

### Что нужно для 1.0.0

**Блокирующие проблемы:**

1. **Enrichment не использует провайдеры** — старые стратегии жёстко привязаны к Ollama
2. **Ошибки enrichment скрываются** — job показывает "completed" без информации о fallback
3. **Rate limiting для Yandex** — нет автоматической адаптации к лимитам API

**Желательные улучшения:**

4. Унификация обработки ошибок (ProviderError вместо OllamaConnectionError)
5. Deprecate EmbeddingService в пользу IEmbeddingProvider

---

## Философия релиза v1.0.0

> "Production-ready = стабильно, прозрачно, предсказуемо"

v1.0.0 — это **stability & transparency release**:
- Все провайдеры работают одинаково для всех операций
- Ошибки видны пользователю, а не скрыты graceful degradation
- Rate limiting адаптируется к реальным лимитам API
- Код унифицирован, дублирование устранено

---

## Фазы разработки

### Phase 1: Унификация Enrichment Providers (P0)
**Цель:** Enrichment работает с любым провайдером (Ollama, Yandex, будущие)
**Приоритет:** Блокирующий для релиза

#### 1.1 Рефакторинг ContextualRetrievalService

**Файл:** `src/obsidian_kb/enrichment/contextual_retrieval.py`

**Текущее состояние:** Уже использует `IChatCompletionProvider` ✅

**Изменения:**
- Добавить статистику успешных/неуспешных обогащений
- Добавить информацию о fallback в EnrichedChunk

```python
@dataclass
class EnrichedChunk:
    chunk_info: "ChunkInfo"
    context_prefix: str
    provider_info: dict[str, str] | None = None
    # Новые поля:
    enrichment_status: Literal["success", "fallback", "skipped"] = "success"
    error_message: str | None = None

@dataclass
class EnrichmentStats:
    """Статистика обогащения."""
    total_chunks: int
    enriched_ok: int
    enriched_fallback: int
    errors: list[str]
```

#### 1.2 Удаление LLMEnrichmentService и старых стратегий

**Файлы для рефакторинга:**
- `src/obsidian_kb/enrichment/llm_enrichment_service.py` → Deprecated
- `src/obsidian_kb/enrichment/strategies/full_enrichment_strategy.py` → Удалить
- `src/obsidian_kb/enrichment/strategies/fast_enrichment_strategy.py` → Удалить
- `src/obsidian_kb/service_container.py:524-537` → Использовать ContextualRetrievalService

**Альтернатива (менее рискованная):**
- Рефакторить FullEnrichmentStrategy на использование IChatCompletionProvider вместо Ollama HTTP

```python
# БЫЛО (full_enrichment_strategy.py):
class FullEnrichmentStrategy:
    def __init__(self, base_url: str, model: str):
        self._base_url = base_url  # Жёстко Ollama!
        self._model = model

# СТАЛО:
class FullEnrichmentStrategy(BaseEnrichmentStrategy):
    def __init__(self, chat_provider: IChatCompletionProvider):
        self._chat = chat_provider
```

#### 1.3 Обновление ServiceContainer

**Файл:** `src/obsidian_kb/service_container.py`

```python
# БЫЛО:
strategy = FullEnrichmentStrategy(
    base_url=self._ollama_url,  # ВСЕГДА Ollama!
    model=self._settings.llm_model,
)

# СТАЛО:
strategy = FullEnrichmentStrategy(
    chat_provider=self.enrichment_chat_provider,  # Любой провайдер
)
```

**Критерии завершения Phase 1:** ✅ ЗАВЕРШЕНО (2026-01-07)
- [x] FullEnrichmentStrategy принимает IChatCompletionProvider
- [x] FastEnrichmentStrategy принимает IChatCompletionProvider
- [x] ServiceContainer передаёт enrichment_chat_provider в стратегии
- [x] EnrichedChunk содержит enrichment_status и error_message
- [x] Все 997+ тестов проходят

---

### Phase 2: Прозрачность статуса Enrichment (P0)
**Цель:** Пользователь видит реальный статус обогащения
**Приоритет:** Блокирующий для релиза

#### 2.1 Расширение IndexingResult

**Файл:** `src/obsidian_kb/indexing/orchestrator.py`

```python
@dataclass
class IndexingResult:
    job_id: str
    documents_processed: int
    documents_total: int
    chunks_created: int
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    # Новые поля:
    enrichment_stats: EnrichmentStats | None = None
    warnings: list[str] = field(default_factory=list)
```

#### 2.2 Интеграция статистики в orchestrator

**Файл:** `src/obsidian_kb/indexing/orchestrator.py:395-458`

```python
async def _enrich_document(
    self,
    processed: ProcessedDocument,
    strategy: EnrichmentStrategy,
) -> tuple[EnrichedDocument, EnrichmentStats]:
    """Phase 3: Обогащение чанков с трекингом статистики."""
    stats = EnrichmentStats(
        total_chunks=len(processed.chunks),
        enriched_ok=0,
        enriched_fallback=0,
        errors=[],
    )

    enriched_chunks = []

    if strategy == EnrichmentStrategy.CONTEXTUAL:
        if self._contextual_retrieval:
            enriched_chunks = await self._contextual_retrieval.enrich_chunks(
                chunks=processed.chunks,
                document_context=processed.title,
            )
            # Считаем статистику
            for chunk in enriched_chunks:
                if chunk.enrichment_status == "success":
                    stats.enriched_ok += 1
                elif chunk.enrichment_status == "fallback":
                    stats.enriched_fallback += 1
                    if chunk.error_message:
                        stats.errors.append(chunk.error_message)

    return EnrichedDocument(...), stats
```

#### 2.3 Отображение в job status

**Файл:** `src/obsidian_kb/indexing/job_queue.py`

```python
@dataclass
class BackgroundJob:
    # ... существующие поля ...
    enrichment_stats: EnrichmentStats | None = None

    def to_dict(self) -> dict[str, Any]:
        """Сериализация для MCP."""
        result = {
            "id": self.id,
            "status": self.status.value,
            "progress": self.progress,
            # ...
        }
        if self.enrichment_stats:
            result["enrichment"] = {
                "total": self.enrichment_stats.total_chunks,
                "success": self.enrichment_stats.enriched_ok,
                "fallback": self.enrichment_stats.enriched_fallback,
                "errors": len(self.enrichment_stats.errors),
            }
        return result
```

**Критерии завершения Phase 2:** ✅ ЗАВЕРШЕНО (2026-01-07)
- [x] IndexingResult содержит enrichment_stats
- [x] BackgroundJob.to_dict() включает enrichment статистику
- [x] get_job_status MCP tool показывает enrichment статистику
- [x] При fallback в статусе появляется warning
- [x] Все 1002 тестов проходят (добавлено 5 новых)

---

### Phase 3: Адаптивный Rate Limiting для Yandex (P1)
**Цель:** Автоматическая адаптация к лимитам Yandex API
**Приоритет:** Высокий

#### 3.1 Adaptive Rate Limiter

**Новый файл:** `src/obsidian_kb/providers/rate_limiter.py`

```python
import asyncio
import time
from dataclasses import dataclass


@dataclass
class RateLimitState:
    """Состояние rate limiter."""
    current_rps: float  # Текущий RPS
    max_rps: float  # Максимальный RPS
    min_rps: float  # Минимальный RPS
    last_429_time: float | None = None  # Время последнего 429
    consecutive_success: int = 0  # Последовательных успехов


class AdaptiveRateLimiter:
    """Адаптивный rate limiter с экспоненциальным backoff.

    - При 429 ошибке: уменьшаем RPS в 2 раза
    - После N успешных запросов: увеличиваем RPS на 10%
    - Не превышаем max_rps, не опускаемся ниже min_rps
    """

    def __init__(
        self,
        initial_rps: float = 10.0,
        max_rps: float = 100.0,
        min_rps: float = 1.0,
        recovery_threshold: int = 50,  # Успехов для увеличения RPS
    ):
        self._state = RateLimitState(
            current_rps=initial_rps,
            max_rps=max_rps,
            min_rps=min_rps,
        )
        self._recovery_threshold = recovery_threshold
        self._semaphore = asyncio.Semaphore(int(initial_rps))
        self._last_request_time = 0.0

    async def acquire(self) -> None:
        """Ожидание слота для запроса."""
        async with self._semaphore:
            # Минимальный интервал между запросами
            min_interval = 1.0 / self._state.current_rps
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            self._last_request_time = time.monotonic()

    def record_success(self) -> None:
        """Записать успешный запрос."""
        self._state.consecutive_success += 1
        if self._state.consecutive_success >= self._recovery_threshold:
            self._increase_rps()
            self._state.consecutive_success = 0

    def record_rate_limit(self) -> None:
        """Записать 429 ошибку."""
        self._state.last_429_time = time.monotonic()
        self._state.consecutive_success = 0
        self._decrease_rps()

    def _decrease_rps(self) -> None:
        """Уменьшить RPS в 2 раза."""
        new_rps = max(self._state.min_rps, self._state.current_rps / 2)
        if new_rps != self._state.current_rps:
            logger.warning(f"Rate limit hit, reducing RPS: {self._state.current_rps:.1f} → {new_rps:.1f}")
            self._state.current_rps = new_rps
            self._update_semaphore()

    def _increase_rps(self) -> None:
        """Увеличить RPS на 10%."""
        new_rps = min(self._state.max_rps, self._state.current_rps * 1.1)
        if new_rps != self._state.current_rps:
            logger.info(f"Increasing RPS: {self._state.current_rps:.1f} → {new_rps:.1f}")
            self._state.current_rps = new_rps
            self._update_semaphore()

    def _update_semaphore(self) -> None:
        """Обновить семафор под новый RPS."""
        self._semaphore = asyncio.Semaphore(max(1, int(self._state.current_rps)))
```

#### 3.2 Интеграция в YandexChatProvider

**Файл:** `src/obsidian_kb/providers/yandex/chat_provider.py`

```python
from obsidian_kb.providers.rate_limiter import AdaptiveRateLimiter

class YandexChatProvider:
    def __init__(self, ...):
        # ...
        self._rate_limiter = AdaptiveRateLimiter(
            initial_rps=config.rate_limit_rps or 20,
            max_rps=100,
            min_rps=1,
        )

    async def complete(self, messages: list[dict], ...) -> str:
        await self._rate_limiter.acquire()

        try:
            result = await self._complete_internal(messages, ...)
            self._rate_limiter.record_success()
            return result
        except ProviderRateLimitError:
            self._rate_limiter.record_rate_limit()
            raise
```

#### 3.3 Конфигурация через ProviderConfig

**Файл:** `src/obsidian_kb/providers/provider_config.py`

```python
@dataclass(frozen=True)
class ProviderConfig:
    max_concurrent: int
    batch_size: int
    enrichment_concurrent: int
    rate_limit_rps: int | None
    timeout: int
    # Новые параметры:
    adaptive_rate_limit: bool = True  # Включить адаптивный rate limiting
    rate_limit_min_rps: float = 1.0   # Минимальный RPS
    rate_limit_recovery: int = 50     # Успехов для увеличения RPS

PROVIDER_CONFIGS: dict[str, ProviderConfig] = {
    "ollama": ProviderConfig(
        max_concurrent=10,
        batch_size=32,
        enrichment_concurrent=5,
        rate_limit_rps=15,
        timeout=60,
        adaptive_rate_limit=False,  # Локальный, не нужно
    ),
    "yandex": ProviderConfig(
        max_concurrent=50,
        batch_size=100,
        enrichment_concurrent=10,  # Уменьшено с 20
        rate_limit_rps=20,         # Уменьшено с 100
        timeout=30,
        adaptive_rate_limit=True,  # Адаптация к лимитам API
        rate_limit_min_rps=2.0,
        rate_limit_recovery=30,
    ),
}
```

**Критерии завершения Phase 3:** ✅ ЗАВЕРШЕНО (2026-01-07)
- [x] AdaptiveRateLimiter создан и протестирован
- [x] YandexChatProvider использует adaptive rate limiting
- [x] YandexEmbeddingProvider использует adaptive rate limiting
- [x] При 429 ошибке RPS автоматически уменьшается
- [x] После успешных запросов RPS восстанавливается
- [x] Все 1026 тестов проходят (добавлено 24 новых)

---

### Phase 4: Унификация обработки ошибок (P1)
**Цель:** Единая иерархия ошибок для всех провайдеров
**Приоритет:** Высокий

#### 4.1 Замена OllamaConnectionError на ProviderError

**Файлы для изменения:**
- `src/obsidian_kb/types.py` — пометить OllamaConnectionError как deprecated
- `src/obsidian_kb/enrichment/llm_enrichment_service.py:160` — ловить ProviderError
- `src/obsidian_kb/enrichment/strategies/*.py` — использовать ProviderError

```python
# types.py
import warnings

class OllamaConnectionError(Exception):
    """Deprecated: используйте ProviderConnectionError из providers/exceptions.py"""

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "OllamaConnectionError is deprecated, use ProviderConnectionError",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
```

#### 4.2 Унификация catch блоков

```python
# БЫЛО (llm_enrichment_service.py):
from obsidian_kb.types import OllamaConnectionError

try:
    result = await self._strategy.enrich(chunk)
except OllamaConnectionError as e:
    logger.warning(f"LLM connection error: {e}")
    return self._create_empty_enrichment(chunk)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

# СТАЛО:
from obsidian_kb.providers.exceptions import ProviderError, ProviderConnectionError

try:
    result = await self._strategy.enrich(chunk)
except ProviderConnectionError as e:
    logger.warning(f"Provider connection error: {e}")
    return self._create_fallback_enrichment(chunk, error=str(e))
except ProviderError as e:
    logger.warning(f"Provider error: {e}")
    return self._create_fallback_enrichment(chunk, error=str(e))
except Exception as e:
    logger.error(f"Unexpected error during enrichment: {e}")
    raise
```

**Критерии завершения Phase 4:** ✅ ЗАВЕРШЕНО (2026-01-07)
- [x] OllamaConnectionError помечен как deprecated
- [x] Все catch блоки используют ProviderError
- [x] При ProviderError создаётся fallback с информацией об ошибке
- [x] Все 1026 тестов проходят, deprecation warnings логируются

---

### Phase 5: Документация и финализация (P2)
**Цель:** Готовность к публичному релизу
**Приоритет:** Средний

#### 5.1 Обновление документации

| Документ | Статус | Действие |
|----------|--------|----------|
| README.md | ✅ Готово | Добавлены multi-provider примеры |
| CHANGELOG.md | ✅ Готово | Полное описание v1.0.0 |
| API_DOCUMENTATION.md | ✅ Готово | Обновлена версия до 1.0.0 |
| MIGRATION.md | ✅ Готово | Создан гайд миграции с v0.x на v1.0.0 |

#### 5.2 Финальные проверки

- [x] Все 1026 тестов проходят
- [x] Нет deprecation warnings (кроме внешних библиотек)
- [x] pyproject.toml version = "1.0.0"
- [ ] Git tag v1.0.0 создан

**Критерии завершения Phase 5:** ✅ ЗАВЕРШЕНО (2026-01-07)

---

## Метрики успеха v1.0.0

| Метрика | v0.9.1 | Текущее | v1.0.0 Target |
|---------|--------|---------|---------------|
| Тесты | 997 | 1026 | 1050+ |
| Enrichment providers | Только Ollama* | Ollama + Yandex ✅ | Ollama + Yandex |
| Enrichment status | Скрыт | Прозрачный ✅ | Прозрачный |
| Rate limit handling | Фиксированный | Адаптивный ✅ | Адаптивный |
| ProviderError usage | Частичное | 100% ✅ | 100% |

*IndexingOrchestrator уже использует Yandex, но LLMEnrichmentService — только Ollama

---

## Временная шкала

```
Фаза 1:   [████████] Унификация Enrichment Providers      ✅ ЗАВЕРШЕНО
Фаза 2:   [████████] Прозрачность статуса Enrichment      ✅ ЗАВЕРШЕНО
Фаза 3:   [████████] Адаптивный Rate Limiting             ✅ ЗАВЕРШЕНО
Фаза 4:   [████████] Унификация обработки ошибок          ✅ ЗАВЕРШЕНО
Фаза 5:   [████████] Документация и финализация           ✅ ЗАВЕРШЕНО
         [████████] v1.0.0 Release                        ✅ ЗАВЕРШЕНО
```

**Дата завершения:** 2026-01-07

---

## Стратегия релизов

### v0.10.0 — Multi-Provider Enrichment (Phase 1-2)

**Включает:**
- Унификация Enrichment Providers (Phase 1)
- Прозрачность статуса Enrichment (Phase 2)

**Критерии релиза:**
- FullEnrichmentStrategy и FastEnrichmentStrategy используют IChatCompletionProvider
- IndexingResult содержит enrichment_stats
- Job status показывает успешные/fallback обогащения
- Все 1000+ тестов проходят

### v1.0.0 — Production Release (Phase 3-5)

**Включает:**
- Адаптивный Rate Limiting для Yandex (Phase 3)
- Унификация обработки ошибок (Phase 4)
- Документация и финализация (Phase 5)

**Критерии релиза:**
- Автоматическая адаптация к rate limits API
- Единая иерархия ProviderError
- Полная документация API

---

## Начало работы

### Для Phase 1: Унификация Enrichment

```bash
git checkout main
git pull origin main
git checkout -b feature/v0.10.0-enrichment-providers
```

**Промпт для Claude:**
```
Начинаем работу над ROADMAP_v0.10.0.md.

Прочитай ROADMAP_v0.10.0.md и начни Phase 1: Унификация Enrichment Providers.

Задачи Phase 1:
1. Рефакторинг FullEnrichmentStrategy на использование IChatCompletionProvider
2. Рефакторинг FastEnrichmentStrategy аналогично
3. Обновление ServiceContainer для передачи enrichment_chat_provider
4. Добавление enrichment_status и error_message в EnrichedChunk

Начни с анализа текущего кода FullEnrichmentStrategy и плана рефакторинга.
После каждого изменения запускай тесты для проверки.
```

---

## Риски и митигация

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Регрессии при рефакторинге enrichment | Средняя | Инкрементальные изменения, тесты |
| Yandex API меняет лимиты | Низкая | Адаптивный rate limiter |
| Несовместимость с существующими vaults | Низкая | Миграционный скрипт если нужно |
