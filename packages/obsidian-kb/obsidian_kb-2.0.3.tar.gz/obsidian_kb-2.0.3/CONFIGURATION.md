# Конфигурация obsidian-kb

## Настройка vault'ов

### Добавление vault'а

```bash
# Добавить vault в конфигурацию (автоматически проиндексируется)
obsidian-kb config add-vault --name "my-vault" --path "/path/to/vault"

# Показать текущую конфигурацию
obsidian-kb config show
```

Конфигурация сохраняется в `~/.obsidian-kb/vaults.json`:

```json
{
  "vaults": [
    {
      "name": "my-vault",
      "path": "/Users/username/Obsidian/my-vault"
    }
  ]
}
```

### Управление vault'ами

```bash
# Удалить vault из конфигурации
obsidian-kb config remove-vault --name "my-vault"

# Список проиндексированных vault'ов
obsidian-kb list-vaults
```

## Игнорирование файлов

Создайте файл `.obsidian-kb-ignore` в корне vault'а для исключения файлов из индексации. Формат аналогичен `.gitignore`:

```gitignore
# Временные файлы
*.tmp
*.temp
*.swp

# Игнорировать директорию
node_modules/
.temp/

# Игнорировать конкретный файл
private-notes.md

# Но не игнорировать важный файл (отрицание)
!important.tmp
```

**Поддерживаемые паттерны:**
- `*.ext` — все файлы с расширением `.ext`
- `dir/` — директория `dir` и всё внутри
- `**/temp/**` — директория `temp` в любом месте пути
- `!pattern` — отрицание (отменяет игнорирование)

**Паттерны по умолчанию** (применяются автоматически):
- Временные файлы: `*.tmp`, `*.temp`, `*.swp`, `*.bak`
- Системные файлы: `.DS_Store`, `Thumbs.db`
- Директории зависимостей: `node_modules/`, `.git/`
- Python окружения: `.venv/`, `venv/`, `__pycache__/`

## Переменные окружения

Все настройки можно переопределить через переменные окружения с префиксом `OBSIDIAN_KB_`:

```bash
# Пути
export OBSIDIAN_KB_DB_PATH="/custom/path/to/lancedb"
export OBSIDIAN_KB_VAULTS_CONFIG="/custom/path/to/vaults.json"

# Ollama
export OBSIDIAN_KB_OLLAMA_URL="http://localhost:11434"
export OBSIDIAN_KB_EMBEDDING_MODEL="nomic-embed-text"
export OBSIDIAN_KB_EMBEDDING_DIMENSIONS=768
export OBSIDIAN_KB_EMBEDDING_TIMEOUT=10  # Таймаут для получения embeddings (в секундах)

# Индексирование
export OBSIDIAN_KB_CHUNK_SIZE=2000
export OBSIDIAN_KB_CHUNK_OVERLAP=250
export OBSIDIAN_KB_BATCH_SIZE=32
export OBSIDIAN_KB_MAX_WORKERS=10

# Поиск
export OBSIDIAN_KB_DEFAULT_SEARCH_TYPE="hybrid"
export OBSIDIAN_KB_HYBRID_ALPHA=0.7

# Оптимизация поиска
export OBSIDIAN_KB_ENABLE_SEARCH_OPTIMIZER=true
export OBSIDIAN_KB_ENABLE_RERANK=true
export OBSIDIAN_KB_ENABLE_QUERY_EXPANSION=false
export OBSIDIAN_KB_ENABLE_FEATURE_RANKING=true
export OBSIDIAN_KB_ADAPTIVE_ALPHA=true

# Обработка больших файлов
export OBSIDIAN_KB_MAX_FILE_SIZE=52428800        # 50 MB
export OBSIDIAN_KB_MAX_FILE_SIZE_STREAMING=10485760  # 10 MB
```

## Настройки по умолчанию

- **База данных**: `~/.obsidian-kb/lancedb`
- **Конфиг vault'ов**: `~/.obsidian-kb/vaults.json`
- **Ollama URL**: `http://localhost:11434`
- **Модель embeddings**: `nomic-embed-text`
- **Размерность embeddings**: 768
- **Таймаут embeddings**: 10 секунд (оптимизировано для быстрого поиска)
- **Размер чанка**: 2000 символов
- **Перекрытие чанков**: 250 символов
- **Размер батча**: 32
- **Тип поиска**: `hybrid`
- **Вес векторного поиска (hybrid)**: 0.7
- **Максимальный размер файла**: 50 MB
- **Порог потоковой обработки**: 10 MB

## Оптимизация для агентов

Для использования с агентами (Claude, Cursor) рекомендуется:

```bash
# Включить оптимизатор поиска
export OBSIDIAN_KB_ENABLE_SEARCH_OPTIMIZER=true

# Включить re-ranking (улучшает точность)
export OBSIDIAN_KB_ENABLE_RERANK=true

# Отключить query expansion (агенты сами уточняют)
export OBSIDIAN_KB_ENABLE_QUERY_EXPANSION=false

# Включить feature-based ranking
export OBSIDIAN_KB_ENABLE_FEATURE_RANKING=true

# Использовать адаптивный alpha
export OBSIDIAN_KB_ADAPTIVE_ALPHA=true
```

> **Подробнее:** См. [SEARCH_OPTIMIZATION.md](SEARCH_OPTIMIZATION.md) и [SEARCH_OPTIMIZATION_GUIDE.md](SEARCH_OPTIMIZATION_GUIDE.md)

