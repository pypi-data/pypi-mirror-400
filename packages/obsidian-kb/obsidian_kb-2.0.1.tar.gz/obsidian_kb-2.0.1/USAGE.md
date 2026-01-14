# Использование obsidian-kb

## Типовой путь пользователя

1. **Установка** → см. [INSTALLATION.md](INSTALLATION.md)
2. **Настройка** → см. [CONFIGURATION.md](CONFIGURATION.md)
3. **Добавление vault** → `obsidian-kb config add-vault`
4. **Индексирование** → `obsidian-kb index-all`
5. **Использование** → через агента (MCP) или CLI

## Индексирование

### Первичное индексирование

```bash
# Индексировать все vault'ы из конфига
obsidian-kb index-all

# Индексировать конкретный vault
obsidian-kb index --vault "my-vault" --path "/path/to/vault"
```

### Инкрементальное индексирование

При повторном запуске `index-all` система автоматически использует инкрементальный режим — обрабатываются только изменённые файлы (ускорение до 10x).

### Автоматическое отслеживание изменений

```bash
# Отслеживать все vault'ы из конфига
obsidian-kb watch

# Отслеживать конкретный vault
obsidian-kb watch --vault "my-vault"

# С настройкой задержки (в секундах)
obsidian-kb watch --debounce 3.0
```

Команда `watch` отслеживает изменения файлов в реальном времени и автоматически обновляет индекс.

### Переиндексирование

```bash
# Переиндексировать vault из конфига
obsidian-kb reindex --vault "my-vault"

# Переиндексировать с подтверждением
obsidian-kb reindex --vault "my-vault" --force
```

## Поиск через CLI

### Базовый поиск

```bash
# Простой поиск
obsidian-kb search --vault "my-vault" --query "Python async"

# Поиск с указанием типа
obsidian-kb search --vault "my-vault" --query "Python" --type hybrid

# Ограничение количества результатов
obsidian-kb search --vault "my-vault" --query "Python" --limit 5
```

### Расширенный поиск

```bash
# Поиск по тегам
obsidian-kb search --vault "my-vault" --query "Python tags:python async"

# Поиск по датам
obsidian-kb search --vault "my-vault" --query "created:>2024-01-01 modified:<2024-12-31"

# Поиск по типу документа
obsidian-kb search --vault "my-vault" --query "type:протокол"

# Поиск по связанным заметкам (wikilinks)
obsidian-kb search --vault "my-vault" --query "links:Python"

# Комбинированный поиск
obsidian-kb search --vault "my-vault" --query "Python tags:python created:>2024-01-01 type:guide links:Flask"
```

> **Подробная документация:** См. [ADVANCED_SEARCH.md](ADVANCED_SEARCH.md)

### Экспорт результатов

```bash
# Экспорт в JSON
obsidian-kb search --vault "my-vault" --query "Python" --export results.json --format json

# Экспорт в Markdown
obsidian-kb search --vault "my-vault" --query "Python" --export results.md --format markdown

# Экспорт в CSV
obsidian-kb search --vault "my-vault" --query "Python" --export results.csv --format csv
```

## Использование через агента (MCP)

После настройки Claude Desktop (см. [MCP_INTEGRATION.md](MCP_INTEGRATION.md)) агент получает доступ к инструментам:

### Основные инструменты

**`search_vault`** — поиск в одном vault'е
```
search_vault("my-vault", "Python async programming")
search_vault("my-vault", "Python tags:python async", limit=5)
```

**`search_multi_vault`** — поиск по нескольким vault'ам
```
search_multi_vault(["vault1", "vault2"], "Python async")
```

**`list_vaults`** — список проиндексированных vault'ов

**`vault_stats`** — статистика vault'а
```
vault_stats("my-vault")
```

### Управление индексацией

**`index_vault`** — инкрементальное индексирование
```
index_vault("my-vault", "/path/to/vault")
```

**`reindex_vault`** — полная переиндексация
```
reindex_vault("my-vault", "/path/to/vault")
```

**`delete_vault`** — удалить vault из индекса
```
delete_vault("old-vault")
```

### Управление конфигурацией

**`add_vault_to_config`** — добавить vault в конфигурацию
```
add_vault_to_config("/path/to/vault", "my-vault")
add_vault_to_config("/path/to/vault")  # имя определится автоматически
```

**`check_vault_in_config`** — проверить наличие vault в конфиге
```
check_vault_in_config(vault_path="/path/to/vault")
check_vault_in_config(vault_name="my-vault")
```

**`list_configured_vaults`** — список настроенных vault'ов

### Диагностика и метрики

**`system_health`** — диагностика системы

**`get_metrics`** — метрики использования
```
get_metrics(days=30, limit=20)
```

## Статистика и диагностика

### Статистика vault'а

```bash
obsidian-kb stats --vault "my-vault"
```

Показывает:
- Количество файлов и чанков
- Размер индекса
- Список тегов
- Даты создания/модификации

### Диагностика системы

```bash
# Полная проверка системы
obsidian-kb doctor

# JSON вывод для автоматизации
obsidian-kb doctor --json

# Проверка конкретного компонента
obsidian-kb doctor --check ollama
obsidian-kb doctor --check lancedb
obsidian-kb doctor --check vaults
obsidian-kb doctor --check disk
```

Проверяет:
- Доступность Ollama и наличие модели
- Подключение к базе данных
- Доступность vault'ов
- Свободное место на диске
- Использование памяти и CPU
- Производительность БД

### Метрики использования

```bash
# Просмотр метрик за последние 7 дней
obsidian-kb metrics

# За последние 30 дней
obsidian-kb metrics --days 30

# Экспорт метрик
obsidian-kb metrics --export metrics.json --format json
obsidian-kb metrics --export metrics.csv --format csv
```

## Управление сервисом (macOS)

```bash
# Установить автозапуск
obsidian-kb install-service

# Проверить статус
obsidian-kb service-status

# Перезапустить сервис
obsidian-kb restart-service

# Удалить автозапуск
obsidian-kb uninstall-service
```

## Следующие шаги

- **Интеграция с агентами:** [MCP_INTEGRATION.md](MCP_INTEGRATION.md) — примеры использования MCP инструментов
- **Рекомендации:** [BEST_PRACTICES.md](BEST_PRACTICES.md) — эффективная работа с агентами
- **FAQ:** [FAQ.md](FAQ.md) — часто задаваемые вопросы
- **Оптимизация поиска:** [SEARCH_OPTIMIZATION.md](SEARCH_OPTIMIZATION.md)
- **Решение проблем:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

