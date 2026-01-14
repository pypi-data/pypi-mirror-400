# Примеры использования

Полное руководство с примерами использования MCP tools и CLI команд obsidian-kb.

**Версия:** 0.7.0
**Дата обновления:** 2026-01-06

---

## Содержание

1. [Примеры для Indexing Tools](#примеры-для-indexing-tools)
2. [Примеры для Provider Tools](#примеры-для-provider-tools)
3. [Примеры для Quality Tools](#примеры-для-quality-tools)
4. [Комплексные сценарии](#комплексные-сценарии)
5. [Примеры для CLI команд](#примеры-для-cli-команд)

---

## Примеры для Indexing Tools

### Первичная индексация vault'а

**Сценарий:** Индексация нового vault'а с обогащением.

```python
# Через MCP tool
index_documents(
    vault_name="my-vault",
    enrichment="contextual",
    background=True
)

# Через CLI
obsidian-kb index --vault "my-vault" --enable-enrichment --enrichment-strategy contextual
```

**Результат:** Vault проиндексирован, задачи выполняются в фоне.

### Инкрементальная индексация

**Сценарий:** Индексация только изменённых файлов.

```python
# Через MCP tool (автоматически определяет изменения)
index_documents("my-vault")

# Через CLI
obsidian-kb index --vault "my-vault"
```

**Результат:** Обработаны только изменённые файлы, время индексации сокращено.

### Переиндексация с обогащением

**Сценарий:** Полная переиндексация vault'а с максимальным обогащением.

```python
# Через MCP tool (требует подтверждения)
reindex_vault(
    vault_name="my-vault",
    confirm=True,
    enrichment="full"
)

# Через CLI
obsidian-kb reindex --vault "my-vault" --force --enable-enrichment --enrichment-strategy full
```

**Результат:** Все документы переиндексированы с полным обогащением.

### Фоновое выполнение индексации

**Сценарий:** Индексация выполняется в фоне, не блокируя агента.

```python
# Добавление vault'а с автоматической индексацией в фоне
result = add_vault_to_config(
    vault_path="/path/to/vault",
    vault_name="my-vault",
    auto_index=True
)

# Команда index_vault также выполняется в фоне
result = index_vault(
    vault_name="my-vault",
    vault_path="/path/to/vault"
)
```

**Пример вывода:**
```
## Vault добавлен в конфигурацию
- **Имя:** my-vault
- **Путь:** /path/to/vault
- **Конфиг:** ~/.obsidian-kb/vaults.json

✅ **Индексация запущена в фоне**
- **ID задачи:** `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- **Статус:** pending

Используйте `get_job_status` для проверки прогресса.
```

### Мониторинг прогресса индексации

**Сценарий:** Отслеживание прогресса индексации в реальном времени.

```python
# Получение статуса всех активных задач
status = index_status(vault_name="my-vault")

# Получение статуса конкретной задачи через get_job_status
status = get_job_status(job_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")

# Получение всех задач для конкретного vault'а
status = get_job_status(vault_name="my-vault")
```

**Пример вывода:**
```
## Статус задачи: a1b2c3d4-e5f6-7890-abcd-ef1234567890
- **Vault:** my-vault
- **Операция:** index_vault
- **Статус:** running
- **Прогресс:** 45.2%
- **Создана:** 2026-01-XX 10:30:00
- **Начата:** 2026-01-XX 10:30:01

### Результаты
- **Документов обработано:** 23/51
- **Чанков создано:** 156
```

### Превью разбиения документа

**Сценарий:** Предварительный просмотр того, как документ будет разбит на чанки.

```python
# Автоматический выбор стратегии
preview = preview_chunks(
    vault_name="my-vault",
    file_path="documentation.md",
    strategy="auto"
)

# Разбиение по заголовкам
preview = preview_chunks(
    vault_name="my-vault",
    file_path="documentation.md",
    strategy="headers"
)
```

**Пример вывода:**
```
## Превью разбиения документа 'documentation.md'

### Стратегия: auto
### Количество чанков: 8

#### Чанк 1 (234 символа)
**Секция:** Введение
**Содержимое:** Добро пожаловать в obsidian-kb...

#### Чанк 2 (456 символов)
**Секция:** Установка
**Содержимое:** Для установки obsidian-kb...
```

### Обогащение конкретного документа

**Сценарий:** Обогащение одного документа без переиндексации всего vault'а.

```python
# Только context prefix для чанков
enrich_document(
    vault_name="my-vault",
    file_path="important-doc.md",
    enrichment_type="context"
)

# Только summary документа
enrich_document(
    vault_name="my-vault",
    file_path="important-doc.md",
    enrichment_type="summary"
)

# Всё обогащение
enrich_document(
    vault_name="my-vault",
    file_path="important-doc.md",
    enrichment_type="all"
)
```

---

## Примеры для Provider Tools

### Переключение провайдера

**Сценарий:** Переключение на Yandex Cloud для лучшего качества.

```python
# Переключение embedding провайдера
set_provider(
    provider_name="yandex",
    provider_type="embedding"
)

# Переключение chat провайдера
set_provider(
    provider_name="yandex",
    provider_type="chat",
    model="yandexgpt-pro/latest"
)

# Переключение обоих провайдеров
set_provider(
    provider_name="yandex",
    provider_type="both"
)

# Переключение для конкретного vault'а
set_provider(
    provider_name="ollama",
    provider_type="embedding",
    vault_name="my-vault"
)
```

### Тестирование провайдера

**Сценарий:** Проверка работоспособности провайдера перед использованием.

```python
# Тестирование Ollama
result = test_provider("ollama")

# Тестирование Yandex Cloud
result = test_provider("yandex")
```

**Пример вывода:**
```
## Тестирование провайдера 'ollama'

### Embedding провайдер
- ✅ Доступен
- Размерность: 768
- Latency: 45ms
- Модель: nomic-embed-text

### Chat провайдер
- ✅ Доступен
- Latency: 1234ms
- Модель: qwen2.5:7b-instruct
- Ответ: "Hello! I'm ready to help..."
```

### Проверка здоровья провайдеров

**Сценарий:** Проверка статуса всех провайдеров.

```python
health = provider_health()
```

**Пример вывода:**
```
## Здоровье провайдеров

### Ollama
- ✅ Available
- Embedding latency: 45ms
- Chat latency: 1234ms

### Yandex Cloud
- ✅ Available
- Embedding latency: 234ms
- Chat latency: 567ms
```

### Оценка стоимости

**Сценарий:** Оценка стоимости операций перед выполнением.

```python
# Оценка стоимости переиндексации
cost = estimate_cost(
    operation="reindex",
    vault_name="my-vault",
    provider="yandex"
)

# Оценка стоимости обогащения
cost = estimate_cost(
    operation="enrich",
    vault_name="my-vault",
    enrichment_type="full"
)
```

**Пример вывода:**
```
## Оценка стоимости операции 'reindex'

### Текущий провайдер: yandex
- **Embedding:** ~$0.50 (1000 документов × $0.0005)
- **Chat (contextual):** ~$2.00 (1000 документов × $0.002)
- **Итого:** ~$2.50

### Альтернативные провайдеры:
- **ollama:** $0.00 (бесплатно)
```

---

## Примеры для Quality Tools

### Проверка покрытия индекса

**Сценарий:** Анализ того, какие файлы проиндексированы, а какие нет.

```python
coverage = index_coverage("my-vault")
```

**Пример вывода:**
```
## Покрытие индекса для vault 'my-vault'

### Общая статистика
- **Всего файлов:** 150
- **Проиндексировано:** 142 (94.7%)
- **Ожидает индексации:** 8 (5.3%)

### По типам документов
- **type:person:** 36/36 (100%)
- **type:project:** 13/15 (86.7%)
- **type:meeting:** 45/45 (100%)

### Рекомендации
- ⚠️ 2 проекта не проиндексированы: project-x.md, project-y.md
- ✅ Все профили людей проиндексированы
```

### Тестирование качества поиска

**Сценарий:** Проверка качества поиска на тестовых запросах.

```python
result = test_retrieval(
    vault_name="my-vault",
    queries=[
        "Python async programming",
        "Как использовать asyncio",
        "профиль Иванов",
    ],
    expected_docs={
        "Python async programming": ["python-guide.md", "async-tutorial.md"],
        "Как использовать asyncio": ["asyncio-tutorial.md"],
    }
)
```

**Пример вывода:**
```
## Тестирование качества поиска

### Запрос 1: "Python async programming"
- **Top-5 результатов:** 5/5 релевантных
- **Recall@5:** 100%
- **Время ответа:** 234ms

### Запрос 2: "Как использовать asyncio"
- **Top-5 результатов:** 4/5 релевантных
- **Recall@5:** 80%
- **Время ответа:** 189ms

### Общая статистика
- **Средний Recall@5:** 90%
- **Среднее время ответа:** 211ms
```

### Аудит индекса

**Сценарий:** Поиск проблем в индексе и рекомендации по улучшению.

```python
audit = audit_index("my-vault")
```

**Пример вывода:**
```
## Аудит индекса для vault 'my-vault'

### Качество чанков
- ⚠️ 12 чанков слишком большие (>2000 символов)
- ⚠️ 5 чанков слишком маленькие (<50 символов)
- ✅ Большинство чанков оптимального размера

### Качество обогащения
- ⚠️ 23 чанка без context_prefix
- ✅ 89% чанков имеют context_prefix

### Дубликаты
- ⚠️ Найдено 3 потенциальных дубликата

### Рекомендации
1. Переиндексировать большие чанки с другой стратегией
2. Добавить context_prefix для 23 чанков
3. Проверить дубликаты на актуальность
```

### Отчёт о затратах

**Сценарий:** Анализ затрат на использование LLM за период.

```python
# Отчёт за последние 7 дней
report = cost_report(days=7)

# Отчёт по конкретному vault'у
report = cost_report(days=30, vault_name="my-vault")
```

**Пример вывода:**
```
## Отчёт о затратах за последние 7 дней

### По провайдерам
- **Ollama:** $0.00 (бесплатно)
- **Yandex Cloud:** $12.50
  - Embedding: $5.00 (10M tokens)
  - Chat: $7.50 (3.75M tokens)

### По операциям
- **Embedding:** $5.00 (индексация)
- **Enrichment:** $7.50 (contextual + summary)

### По vault'ам
- **my-vault:** $8.00
- **work-notes:** $4.50

### Итого: $12.50
```

### Отчёт о производительности

**Сценарий:** Анализ производительности поиска.

```python
performance = performance_report(days=7)
```

**Пример вывода:**
```
## Отчёт о производительности за последние 7 дней

### Метрики поиска
- **Всего запросов:** 1234
- **Среднее время ответа:** 234ms
- **P95 время ответа:** 567ms
- **P99 время ответа:** 1234ms

### По типам поиска
- **Vector search:** 567 запросов (среднее: 189ms)
- **FTS search:** 234 запросов (среднее: 45ms)
- **Hybrid search:** 433 запросов (среднее: 345ms)

### Популярные запросы
1. "Python async" (45 запросов)
2. "профиль Иванов" (23 запроса)
3. "проект X" (12 запросов)

### Запросы без результатов
- "xyz123" (5 запросов)
- "несуществующий документ" (3 запроса)
```

---

## Комплексные сценарии

### Настройка нового vault'а

**Сценарий:** Полная настройка нового vault'а с индексацией.

```python
# 1. Добавление vault'а в конфигурацию
add_vault_to_config(
    vault_path="/path/to/vault",
    vault_name="my-vault",
    auto_index=True
)

# 2. Проверка провайдеров
providers = list_providers()
health = provider_health()

# 3. Настройка провайдера для vault'а
set_provider(
    provider_name="yandex",
    provider_type="both",
    vault_name="my-vault"
)

# 4. Первичная индексация с обогащением
index_documents(
    vault_name="my-vault",
    enrichment="contextual",
    background=True
)

# 5. Мониторинг прогресса
while True:
    status = index_status(vault_name="my-vault")
    if status.status == "completed":
        break
    await asyncio.sleep(5)

# 6. Проверка покрытия
coverage = index_coverage("my-vault")
```

### Оптимизация качества поиска

**Сценарий:** Улучшение качества поиска через анализ и оптимизацию.

```python
# 1. Аудит индекса
audit = audit_index("my-vault")

# 2. Тестирование поиска
test_result = test_retrieval(
    vault_name="my-vault",
    queries=["запрос1", "запрос2"],
)

# 3. Переиндексация проблемных документов
if audit.has_issues:
    index_documents(
        vault_name="my-vault",
        paths=audit.problem_files,
        force=True,
        enrichment="full"
    )

# 4. Повторное тестирование
test_result_after = test_retrieval(
    vault_name="my-vault",
    queries=["запрос1", "запрос2"],
)
```

### Мониторинг затрат

**Сценарий:** Отслеживание и оптимизация затрат на LLM.

```python
# 1. Еженедельный отчёт о затратах
weekly_report = cost_report(days=7)

# 2. Анализ по vault'ам
for vault_name, cost in weekly_report.by_vault.items():
    print(f"{vault_name}: ${cost:.2f}")

# 3. Оценка стоимости будущих операций
future_cost = estimate_cost(
    operation="reindex",
    vault_name="my-vault"
)

# 4. Оптимизация (переключение на бесплатный провайдер)
if weekly_report.total > 50:
    set_provider("ollama", provider_type="embedding")
```

### Ежедневное обновление индекса

**Сценарий:** Автоматическое обновление индекса при изменениях.

```python
# 1. Проверка изменений (автоматически через ChangeMonitorService)
# Система автоматически отслеживает изменения и запускает индексацию

# 2. Ручная проверка статуса
status = index_status(vault_name="my-vault")

# 3. При необходимости запуск индексации
if status.has_pending_changes:
    index_documents("my-vault")

# 4. Проверка покрытия после обновления
coverage = index_coverage("my-vault")
```

---

## Примеры для CLI команд

### Базовые команды

```bash
# Поиск в vault'е
obsidian-kb search --vault "my-vault" --query "Python async"

# Поиск с фильтрами
obsidian-kb search --vault "my-vault" --query "Python tags:python created:>2024-01-01"

# Статистика vault'а
obsidian-kb stats --vault "my-vault"

# Диагностика системы
obsidian-kb doctor
```

### Управление vault'ами

```bash
# Добавление vault'а
obsidian-kb config add-vault --name "my-vault" --path "/path/to/vault"

# Список vault'ов
obsidian-kb list-vaults

# Удаление vault'а
obsidian-kb config remove-vault --name "my-vault"

# Показать конфигурацию
obsidian-kb config show
```

### Индексация

```bash
# Индексация всех vault'ов
obsidian-kb index-all

# Индексация одного vault'а
obsidian-kb index --vault "my-vault"

# Индексация с обогащением
obsidian-kb index --vault "my-vault" --enable-enrichment --enrichment-strategy contextual

# Переиндексация
obsidian-kb reindex --vault "my-vault" --force

# Переиндексация с полным обогащением
obsidian-kb reindex --vault "my-vault" --force --enable-enrichment --enrichment-strategy full
```

### Мониторинг системы

```bash
# Полная диагностика
obsidian-kb doctor

# Проверка конкретного компонента
obsidian-kb doctor --check ollama

# Проверка покрытия индекса
obsidian-kb index-coverage --vault "my-vault"

# Проверка метрик
obsidian-kb check-metrics --days 7
```

### Интеграция с Claude Desktop

```bash
# Показать конфигурацию для Claude Desktop
obsidian-kb claude-config

# Применить конфигурацию автоматически
obsidian-kb claude-config --apply

# Показать в JSON формате
obsidian-kb claude-config --json
```

### Установка сервиса

```bash
# Установка сервиса для автозапуска (macOS)
obsidian-kb install-service

# Удаление сервиса
obsidian-kb uninstall-service

# Запуск MCP сервера
obsidian-kb serve
```

---

## Советы по эффективности

### 1. Используйте фоновую индексацию

```python
# ✅ Хорошо: фоновая индексация
index_documents("my-vault", background=True)

# ❌ Плохо: синхронная индексация (блокирует MCP сервер)
index_documents("my-vault", background=False)
```

### 2. Мониторьте прогресс

```python
# ✅ Хорошо: проверка статуса
status = index_status(vault_name="my-vault")
if status.progress < 1.0:
    print(f"Прогресс: {status.progress:.1%}")

# ❌ Плохо: ожидание без проверки
await index_documents("my-vault", background=False)
```

### 3. Используйте инкрементальную индексацию

```python
# ✅ Хорошо: только изменённые файлы
index_documents("my-vault")

# ❌ Плохо: переиндексация всего vault'а
reindex_vault("my-vault", confirm=True)
```

### 4. Оптимизируйте затраты

```python
# ✅ Хорошо: оценка стоимости перед операцией
cost = estimate_cost(operation="reindex", vault_name="my-vault")
if cost.total > 10:
    print("Высокая стоимость, рассмотрите использование Ollama")

# ❌ Плохо: выполнение без оценки
reindex_vault("my-vault", confirm=True)
```

### 5. Регулярно проверяйте качество

```python
# ✅ Хорошо: регулярный аудит
audit = audit_index("my-vault")
if audit.has_issues:
    # Исправить проблемы

# ❌ Плохо: игнорирование проблем
```

---

## Следующие шаги

- [PROVIDERS.md](PROVIDERS.md) — выбор провайдера
- [INDEXING.md](INDEXING.md) — детальное описание индексации
- [USAGE.md](USAGE.md) — полное руководство по использованию
- [BEST_PRACTICES.md](BEST_PRACTICES.md) — рекомендации по эффективной работе

