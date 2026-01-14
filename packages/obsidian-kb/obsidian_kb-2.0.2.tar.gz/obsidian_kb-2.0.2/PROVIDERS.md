# Провайдеры LLM

obsidian-kb поддерживает несколько провайдеров для генерации embeddings и chat completion. Вы можете выбрать провайдера в зависимости от ваших потребностей: локальный (Ollama) для приватности и экономии, или облачный (Yandex Cloud) для большей производительности.

**Версия:** 0.7.0
**Дата обновления:** 2026-01-06

---

## Содержание

1. [Обзор провайдеров](#обзор-провайдеров)
2. [Ollama (локальный)](#ollama-локальный)
3. [Yandex Cloud](#yandex-cloud)
4. [Сравнительная таблица](#сравнительная-таблица)
5. [Настройка провайдеров](#настройка-провайдеров)
6. [Переключение между провайдерами](#переключение-между-провайдерами)
7. [Стоимость и лимиты](#стоимость-и-лимиты)
8. [Troubleshooting](#troubleshooting)

---

## Обзор провайдеров

obsidian-kb поддерживает два типа провайдеров:

| Провайдер | Тип | Embeddings | Chat | Статус |
|-----------|-----|------------|------|--------|
| **Ollama** | Локальный | ✅ | ✅ | Полностью реализован |
| **Yandex Cloud** | Облачный | ✅ | ✅ | Полностью реализован |

### Типы провайдеров

- **Embedding провайдеры** — генерация векторных представлений текста для семантического поиска
- **Chat провайдеры** — генерация текста для LLM-обогащения (context prefix, document summary)

Вы можете использовать разные провайдеры для embeddings и chat completion. Например:
- Ollama для embeddings (бесплатно, локально)
- Yandex Cloud для chat completion (лучшее качество)

---

## Ollama (локальный)

**Тип:** Локальный провайдер  
**Стоимость:** Бесплатно  
**Приватность:** Полная (данные не покидают ваш компьютер)

### Описание

Ollama — это локальный провайдер, который работает на вашем компьютере. Идеально подходит для:
- Приватной работы с данными
- Экономии средств (бесплатно)
- Работы без интернета
- Разработки и тестирования

### Модели

#### Embeddings

**Рекомендуемая модель:** `nomic-embed-text`
- Размерность: 768
- Контекстное окно: ~8000 токенов
- Качество: Отличное для большинства задач

**Альтернативные модели:**
- `mxbai-embed-large` (1024 размерности, больше контекста)
- `all-minilm` (384 размерности, быстрее)

#### Chat Completion

**Рекомендуемая модель:** `qwen2.5:7b-instruct`
- Размер: 7B параметров
- Качество: Хорошее для обогащения документов
- Скорость: Быстрая на современных GPU

**Альтернативные модели:**
- `llama3:8b` — более мощная модель
- `mistral:7b` — хороший баланс качества и скорости

### Установка

```bash
# Установите Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Загрузите модель для embeddings
ollama pull nomic-embed-text

# Загрузите модель для chat completion
ollama pull qwen2.5:7b-instruct
```

### Конфигурация

```bash
# Переменные окружения
export OBSIDIAN_KB_EMBEDDING_PROVIDER=ollama
export OBSIDIAN_KB_CHAT_PROVIDER=ollama
export OBSIDIAN_KB_OLLAMA_URL=http://localhost:11434
export OBSIDIAN_KB_OLLAMA_EMBEDDING_MODEL=nomic-embed-text
export OBSIDIAN_KB_OLLAMA_CHAT_MODEL=qwen2.5:7b-instruct
```

### Использование через MCP tools

```python
# Переключение на Ollama
set_provider("ollama", provider_type="embedding")
set_provider("ollama", provider_type="chat")

# Тестирование провайдера
test_provider("ollama")
```

### Преимущества

- ✅ Бесплатно
- ✅ Полная приватность данных
- ✅ Работает без интернета
- ✅ Нет лимитов на количество запросов
- ✅ Быстрая работа на локальной машине

### Недостатки

- ⚠️ Требует мощное железо (GPU рекомендуется)
- ⚠️ Модели занимают место на диске (несколько GB)
- ⚠️ Может быть медленнее облачных провайдеров

### Troubleshooting

**Проблема:** Ollama не запускается  
**Решение:** Проверьте, что Ollama установлен и запущен:
```bash
ollama serve
```

**Проблема:** Модель не найдена  
**Решение:** Загрузите модель:
```bash
ollama pull nomic-embed-text
```

**Проблема:** Медленная работа  
**Решение:** Используйте GPU (CUDA/Metal) или более легкую модель

---

## Yandex Cloud

**Тип:** Облачный провайдер  
**Стоимость:** Платно (см. [цены](https://yandex.cloud/ru/docs/ai-studio/pricing))  
**Приватность:** Данные обрабатываются в облаке Yandex

### Описание

Yandex Cloud AI Studio предоставляет мощные модели для embeddings и chat completion. Идеально подходит для:
- Production окружений
- Больших объёмов данных
- Высокого качества обогащения
- Dedicated instances для изоляции

### Модели

#### Embeddings

**Рекомендуемая модель:** `text-search-doc/latest`
- Размерность: 256
- Качество: Отличное для документов
- Скорость: Быстрая

**Альтернативные модели:**
- `text-search-query/latest` — для поисковых запросов

#### Chat Completion

**Рекомендуемая модель:** `yandexgpt/latest`
- Качество: Отличное
- Скорость: Быстрая
- Поддержка русского языка: Отличная

**Альтернативные модели:**
- `yandexgpt-pro/latest` — более мощная модель
- `yandexgpt-lite/latest` — быстрая и легкая модель

**Dedicated instances:**
- Формат: `gpt://{folder_id}/yandexgpt/{instance_id}`
- Изолированные инстансы для production

### Настройка

1. **Создайте каталог в Yandex Cloud:**
   - Перейдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
   - Создайте каталог (folder)
   - Запишите ID каталога (начинается с `b1g...`)

2. **Создайте API ключ:**
   - Перейдите в раздел "Сервисные аккаунты"
   - Создайте сервисный аккаунт
   - Выдайте ему роль `ai.languageModels.user`
   - Создайте API ключ

3. **Настройте переменные окружения:**

```bash
export OBSIDIAN_KB_EMBEDDING_PROVIDER=yandex
export OBSIDIAN_KB_CHAT_PROVIDER=yandex
export OBSIDIAN_KB_YANDEX_FOLDER_ID=b1g...
export OBSIDIAN_KB_YANDEX_API_KEY=AQV...
export OBSIDIAN_KB_YANDEX_EMBEDDING_MODEL=text-search-doc/latest
export OBSIDIAN_KB_YANDEX_CHAT_MODEL=yandexgpt/latest

# Опционально: Dedicated instance
export OBSIDIAN_KB_YANDEX_INSTANCE_ID=your-instance-id
```

### Использование через MCP tools

```python
# Переключение на Yandex
set_provider("yandex", provider_type="embedding")
set_provider("yandex", provider_type="chat", model="yandexgpt-pro/latest")

# Тестирование провайдера
test_provider("yandex")

# Проверка здоровья
provider_health()
```

### Особенности

- **Батчинг:** Embeddings поддерживают батчинг до 100 текстов в одном запросе
- **Rate limiting:** Автоматическая обработка rate limits (429)
- **Dedicated instances:** Поддержка изолированных инстансов для production
- **Гибкость моделей:** Поддержка всех моделей из каталога AI Studio

### Преимущества

- ✅ Высокое качество моделей
- ✅ Отличная поддержка русского языка
- ✅ Быстрая работа
- ✅ Dedicated instances для изоляции
- ✅ Батчинг для эффективности

### Недостатки

- ⚠️ Платно (см. [цены](https://yandex.cloud/ru/docs/ai-studio/pricing))
- ⚠️ Требует интернет-соединение
- ⚠️ Данные обрабатываются в облаке

### Troubleshooting

**Проблема:** Ошибка аутентификации  
**Решение:** Проверьте `YANDEX_FOLDER_ID` и `YANDEX_API_KEY`

**Проблема:** Rate limit (429)  
**Решение:** Система автоматически обрабатывает rate limits, но вы можете увеличить задержки между запросами

**Проблема:** Модель не найдена  
**Решение:** Проверьте название модели в [каталоге AI Studio](https://yandex.cloud/ru/docs/ai-studio/concepts/generation/models)

---

## Сравнительная таблица

| Характеристика | Ollama | Yandex Cloud |
|----------------|--------|--------------|
| **Тип** | Локальный | Облачный |
| **Стоимость** | Бесплатно | Платно |
| **Приватность** | Полная | Облако |
| **Требует интернет** | Нет | Да |
| **Embeddings** | ✅ | ✅ |
| **Chat Completion** | ✅ | ✅ |
| **Размерность embeddings** | 768 | 256 |
| **Батчинг** | Да | Да (до 100) |
| **Rate limiting** | Нет | Да (авто) |
| **Dedicated instances** | Нет | Да |
| **Поддержка русского** | Хорошая | Отличная |
| **Статус реализации** | ✅ Полностью | ✅ Полностью |

---

## Настройка провайдеров

### Глобальная настройка

Провайдеры настраиваются через переменные окружения:

```bash
# Выбор провайдеров
export OBSIDIAN_KB_EMBEDDING_PROVIDER=ollama
export OBSIDIAN_KB_CHAT_PROVIDER=yandex

# Ollama
export OBSIDIAN_KB_OLLAMA_URL=http://localhost:11434
export OBSIDIAN_KB_OLLAMA_EMBEDDING_MODEL=nomic-embed-text
export OBSIDIAN_KB_OLLAMA_CHAT_MODEL=qwen2.5:7b-instruct

# Yandex Cloud
export OBSIDIAN_KB_YANDEX_FOLDER_ID=b1g...
export OBSIDIAN_KB_YANDEX_API_KEY=AQV...
export OBSIDIAN_KB_YANDEX_EMBEDDING_MODEL=text-search-doc/latest
export OBSIDIAN_KB_YANDEX_CHAT_MODEL=yandexgpt/latest
```

### Vault-specific настройка

Вы можете настроить разные провайдеры для разных vault'ов через ConfigManager:

```python
from obsidian_kb.config.manager import ConfigManager

config_manager = ConfigManager()

# Установка провайдера для конкретного vault'а
config_manager.set_config(
    key="provider.embedding_provider",
    value="yandex",
    vault_name="my-vault",
)

config_manager.set_config(
    key="provider.chat_provider",
    value="ollama",
    vault_name="my-vault",
)
```

---

## Переключение между провайдерами

### Через MCP tools

```python
# Переключение embedding провайдера
set_provider("yandex", provider_type="embedding")

# Переключение chat провайдера
set_provider("ollama", provider_type="chat")

# Переключение обоих провайдеров
set_provider("yandex", provider_type="both")

# Переключение для конкретного vault'а
set_provider("yandex", provider_type="embedding", vault_name="my-vault")
```

### Через переменные окружения

Измените переменные окружения и перезапустите MCP сервер:

```bash
export OBSIDIAN_KB_EMBEDDING_PROVIDER=yandex
export OBSIDIAN_KB_CHAT_PROVIDER=ollama
```

### Проверка текущего провайдера

```python
# Список всех провайдеров со статусом
list_providers()

# Проверка здоровья провайдеров
provider_health()

# Тестирование конкретного провайдера
test_provider("ollama")
```

---

## Стоимость и лимиты

### Ollama

- **Стоимость:** Бесплатно
- **Лимиты:** Нет лимитов
- **Требования:** Локальное железо (GPU рекомендуется)

### Yandex Cloud

**Embeddings:**
- `text-search-doc/latest`: ~$0.5 / 1M tokens
- `text-search-query/latest`: ~$0.5 / 1M tokens

**Chat Completion:**
- `yandexgpt/latest`: ~$2.0 / 1M tokens
- `yandexgpt-pro/latest`: ~$4.0 / 1M tokens
- `yandexgpt-lite/latest`: ~$1.0 / 1M tokens

**Лимиты:**
- Rate limits зависят от тарифа
- Автоматическая обработка rate limits (429)

> **Подробнее:** См. [цены Yandex Cloud](https://yandex.cloud/ru/docs/ai-studio/pricing)

### Оценка стоимости

Используйте MCP tool `estimate_cost` для оценки стоимости операций:

```python
# Оценка стоимости переиндексации
estimate_cost(
    operation="reindex",
    vault_name="my-vault",
    provider="yandex"
)

# Оценка стоимости обогащения
estimate_cost(
    operation="enrich",
    vault_name="my-vault",
    enrichment_type="full"
)
```

### Отчёты о затратах

Используйте MCP tool `cost_report` для анализа затрат:

```python
# Отчёт за последние 7 дней
cost_report(days=7)

# Отчёт по конкретному vault'у
cost_report(days=30, vault_name="my-vault")
```

---

## Troubleshooting

### Проблема: Провайдер недоступен

**Симптомы:**
- Ошибки подключения
- Таймауты

**Решение:**
1. Проверьте доступность провайдера:
   ```python
   provider_health()
   ```

2. Проверьте настройки:
   ```python
   test_provider("ollama")
   ```

3. Проверьте переменные окружения:
   ```bash
   echo $OBSIDIAN_KB_EMBEDDING_PROVIDER
   echo $OBSIDIAN_KB_YANDEX_API_KEY  # для Yandex
   ```

### Проблема: Неправильная размерность embeddings

**Симптомы:**
- Ошибки при индексации
- Ошибки при поиске

**Решение:**
1. Проверьте размерность текущего провайдера:
   ```python
   list_providers()
   ```

2. Переиндексируйте vault после смены провайдера:
   ```python
   reindex_vault("my-vault", confirm=True)
   ```

### Проблема: Rate limits (Yandex Cloud)

**Симптомы:**
- Ошибки 429 (Too Many Requests)
- Медленная работа

**Решение:**
1. Система автоматически обрабатывает rate limits
2. Увеличьте задержки между запросами в настройках
3. Используйте батчинг для эффективности

### Проблема: Высокая стоимость

**Симптомы:**
- Большие счета от облачных провайдеров

**Решение:**
1. Используйте Ollama для embeddings (бесплатно)
2. Используйте более дешёвые модели
3. Отключите обогащение для больших vault'ов
4. Используйте `cost_report` для анализа затрат

---

## Рекомендации по выбору провайдера

### Для разработки и тестирования

- **Embeddings:** Ollama (бесплатно, локально)
- **Chat:** Ollama (бесплатно, локально)

### Для production с небольшими объёмами

- **Embeddings:** Ollama (бесплатно) или Yandex Cloud (быстро)
- **Chat:** Yandex Cloud (хорошее качество) или Ollama (бесплатно)

### Для production с большими объёмами

- **Embeddings:** Yandex Cloud (быстро, батчинг)
- **Chat:** Yandex Cloud (dedicated instances, высокое качество)

### Для максимальной приватности

- **Embeddings:** Ollama (локально)
- **Chat:** Ollama (локально)

---

## Следующие шаги

- [INDEXING.md](INDEXING.md) — детальное описание процесса индексации
- [EXAMPLES.md](EXAMPLES.md) — примеры использования провайдеров
- [CONFIGURATION.md](CONFIGURATION.md) — конфигурация системы
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — решение проблем

