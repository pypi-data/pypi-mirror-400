# Yandex Cloud провайдеры

Поддержка Yandex Cloud AI Studio для embeddings и chat completion.

## Доступные модели

### Chat Completion (YandexChatProvider)

Поддерживаются все модели из каталога Yandex Cloud AI Studio:

- **yandexgpt/latest** - основная модель YandexGPT (по умолчанию)
- **yandexgpt-lite/latest** - легкая версия для быстрых ответов
- **yandexgpt-pro/latest** - продвинутая версия с улучшенным качеством
- Другие модели из каталога AI Studio

Также поддерживаются **dedicated instances** для изолированных инстансов:

- Формат: `gpt://{folder_id}/yandexgpt/{instance_id}`
- Укажите `instance_id` при создании провайдера

**Документация:**
- [Модели генерации](https://yandex.cloud/ru/docs/ai-studio/concepts/generation/models)
- [Dedicated instances](https://yandex.cloud/ru/docs/ai-studio/concepts/generation/dedicated-instance)

### Embeddings (YandexEmbeddingProvider)

Поддерживаются модели embeddings:

- **text-search-doc/latest** - для документов (256 dimensions, по умолчанию)
- **text-search-query/latest** - для поисковых запросов (256 dimensions)

**Документация:**
- [Embeddings](https://yandex.cloud/ru/docs/ai-studio/concepts/embeddings)
- [Pricing](https://yandex.cloud/ru/docs/ai-studio/pricing)

## Конфигурация

### Переменные окружения

```bash
# Выбор провайдера
export OBSIDIAN_KB_EMBEDDING_PROVIDER=yandex
export OBSIDIAN_KB_CHAT_PROVIDER=yandex

# Обязательные параметры
export OBSIDIAN_KB_YANDEX_FOLDER_ID=b1g...
export OBSIDIAN_KB_YANDEX_API_KEY=AQV...

# Модели (опционально)
export OBSIDIAN_KB_YANDEX_EMBEDDING_MODEL=text-search-doc/latest
export OBSIDIAN_KB_YANDEX_CHAT_MODEL=yandexgpt/latest

# Dedicated instance (опционально)
export OBSIDIAN_KB_YANDEX_INSTANCE_ID=your-instance-id
```

### Использование в коде

```python
from obsidian_kb.providers.factory import ProviderFactory

# Chat provider со стандартной моделью
chat_provider = ProviderFactory.get_chat_provider(
    provider_name="yandex",
    folder_id="b1g...",
    api_key="AQV...",
    model="yandexgpt-pro/latest",  # Используем продвинутую модель
)

# Chat provider с dedicated instance
chat_provider = ProviderFactory.get_chat_provider(
    provider_name="yandex",
    folder_id="b1g...",
    api_key="AQV...",
    instance_id="your-instance-id",  # Dedicated instance
)

# Embedding provider
embedding_provider = ProviderFactory.get_embedding_provider(
    provider_name="yandex",
    folder_id="b1g...",
    api_key="AQV...",
    model="text-search-query/latest",  # Для поисковых запросов
)
```

## Особенности

- **Батчинг**: Embeddings поддерживают батчинг до 100 текстов в одном запросе
- **Rate limiting**: Автоматическая обработка rate limits (429)
- **Dedicated instances**: Поддержка изолированных инстансов для production
- **Гибкость моделей**: Поддержка всех моделей из каталога AI Studio

