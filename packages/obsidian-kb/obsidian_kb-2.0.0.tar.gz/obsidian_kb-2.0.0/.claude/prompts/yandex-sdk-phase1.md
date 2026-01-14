# Промпт: Фаза 1 - Интеграция Yandex Cloud ML SDK

## Контекст

Прочитай техническое задание в `TASK_YANDEX_SDK_INTEGRATION.md`. Нужно выполнить **Фазу 1** — рефакторинг Yandex Chat провайдера на использование официального SDK.

## Текущая проблема

Yandex Chat провайдер сломан (HTTP 400 для всех моделей). Нужно заменить прямые HTTP запросы на `yandex-cloud-ml-sdk`.

## Задачи

1. **Добавить зависимость** `yandex-cloud-ml-sdk>=0.17.0` в `pyproject.toml`

2. **Создать файл** `src/obsidian_kb/providers/provider_config.py`:
   - Dataclass `ProviderConfig` с настройками производительности
   - Пресеты для `ollama` и `yandex` (разные лимиты параллелизма)
   - Функция `get_provider_config(provider_name)`

3. **Рефакторинг** `src/obsidian_kb/providers/yandex/chat_provider.py`:
   - Заменить aiohttp на `AsyncYCloudML` из SDK
   - Сохранить интерфейс `IChatCompletionProvider` (методы `complete`, `health_check`, свойства `name`, `model`)
   - Использовать `ProviderConfig` для semaphore и timeout
   - Обработка ошибок через существующие исключения (`ProviderError`, `ProviderTimeoutError`, etc.)

4. **Обновить** `src/obsidian_kb/providers/__init__.py` — добавить экспорт `ProviderConfig`

5. **Написать тесты** в `tests/unit/providers/yandex/test_chat_provider_sdk.py`:
   - Mock для `AsyncYCloudML`
   - Тесты `complete()` и `health_check()`
   - Тесты обработки ошибок

6. **Запустить все тесты**: `.venv/bin/pytest tests/ -v`

## Важные детали

- **НЕ трогать** `YandexEmbeddingProvider` — он работает
- **НЕ трогать** `LLMEnrichmentService` — это Фаза 2
- Сохранить обратную совместимость с параметром `instance_id`
- SDK сам определяет endpoint (Foundation Models vs OpenAI-compatible) по имени модели

## Формат модели для SDK

SDK принимает короткое имя модели:
```python
model = sdk.models.completions('qwen3-235b-a22b-fp8/latest')
model = sdk.models.completions('yandexgpt/latest')
```

SDK сам формирует правильный URI (`gpt://{folder_id}/...`).

## Проверка результата

После выполнения должен работать:
```python
# Через MCP
set_provider("yandex", provider_type="chat", model="qwen3-235b-a22b-fp8/latest")
test_provider("yandex")
# Ожидаемый результат: Chat: ✅ ...ms
```

## Ограничения

- Все 745 тестов должны проходить после изменений
- Использовать `.venv/bin/pytest` для запуска тестов
- Не создавать новые файлы кроме указанных
