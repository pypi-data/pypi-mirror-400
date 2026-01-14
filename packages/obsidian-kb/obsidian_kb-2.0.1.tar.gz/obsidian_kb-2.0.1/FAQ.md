# FAQ: Часто задаваемые вопросы

## Общие вопросы

### Что такое obsidian-kb?

obsidian-kb — это MCP-сервер для семантического поиска по Obsidian vault'ам. Он индексирует ваши заметки и предоставляет быстрый поиск через Model Context Protocol для использования с агентами (Claude Desktop, Cursor и др.).

### Зачем это нужно?

Если вы используете Obsidian для хранения знаний и хотите, чтобы ИИ-агенты могли искать информацию в ваших заметках и использовать её для ответов, obsidian-kb решает эту задачу.

### Какие требования?

- Python 3.12+
- Ollama с моделью `nomic-embed-text`
- Obsidian vault'ы с заметками

## Установка и настройка

### Как установить obsidian-kb?

```bash
# Установите uv (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установите obsidian-kb
uv pip install obsidian-kb
```

Подробнее: [INSTALLATION.md](INSTALLATION.md)

### Как настроить Ollama?

1. Установите Ollama: https://ollama.ai
2. Загрузите модель embeddings:
   ```bash
   ollama pull nomic-embed-text
   ```
3. Убедитесь, что Ollama запущен:
   ```bash
   ollama serve
   ```

Подробнее: [INSTALLATION.md](INSTALLATION.md#2-установка-ollama)

### Как добавить vault в конфигурацию?

```bash
obsidian-kb config add-vault --name "my-vault" --path "/path/to/vault"
```

Или через агента:
```python
add_vault_to_config("/path/to/vault", "my-vault", auto_index=True)
```

### Как проиндексировать vault?

```bash
# Все vault'ы из конфига
obsidian-kb index-all

# Конкретный vault
obsidian-kb index --vault "my-vault" --path "/path/to/vault"
```

Или через агента:
```python
index_vault("my-vault", "/path/to/vault")
```

## Работа с агентами

### Как подключить к Claude Desktop?

```bash
# Автоматическая настройка
obsidian-kb claude-config --apply

# Перезапустите Claude Desktop
```

Подробнее: [MCP_INTEGRATION.md](MCP_INTEGRATION.md)

### Агент не видит инструменты поиска. Что делать?

1. Проверьте конфигурацию Claude Desktop:
   ```bash
   obsidian-kb claude-config
   ```

2. Убедитесь, что MCP сервер запущен:
   ```bash
   obsidian-kb doctor
   ```

3. Проверьте логи Claude Desktop (в настройках)

4. Перезапустите Claude Desktop

Подробнее: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Как агент использует инструменты поиска?

Агент автоматически получает доступ к инструментам после настройки. Просто попросите агента найти что-то:

```
Найди информацию о Python async в моих заметках
```

Агент автоматически вызовет `search_vault("my-vault", "Python async")`.

### Можно ли использовать с другими агентами?

Да, obsidian-kb работает с любыми системами, поддерживающими MCP протокол:
- Claude Desktop
- Cursor IDE
- Другие MCP-совместимые агенты

## Поиск

### Как работает поиск?

obsidian-kb использует гибридный поиск:
- **Векторный поиск** — семантическое сравнение (похожие по смыслу)
- **Полнотекстовый поиск** — точные совпадения слов
- **Гибридный** — комбинация обоих (по умолчанию)

### Как улучшить качество поиска?

1. **Используйте фильтры:**
   ```python
   search_vault("my-vault", "Python tags:python async")
   ```

2. **Включите оптимизатор:**
   ```bash
   export OBSIDIAN_KB_ENABLE_SEARCH_OPTIMIZER=true
   export OBSIDIAN_KB_ENABLE_RERANK=true
   ```

3. **Используйте теги в заметках** — они улучшают точность поиска

Подробнее: [SEARCH_OPTIMIZATION.md](SEARCH_OPTIMIZATION.md)

### Как искать по тегам?

Используйте фильтр `tags:`:
```python
search_vault("my-vault", "Python tags:python async")
```

Теги можно указывать:
- В тексте: `#python`
- В frontmatter: `tags: [python, async]`

### Как искать по датам?

Используйте фильтры `created:` и `modified:`:
```python
# Созданные после 1 января 2024
search_vault("my-vault", "created:>2024-01-01")

# Обновлённые в последний месяц
search_vault("my-vault", "modified:>2024-12-01")
```

### Как искать по типу документа?

Используйте фильтр `type:`:
```python
search_vault("my-vault", "type:протокол")
```

Тип определяется из frontmatter: `type: протокол`

### Как искать по связанным заметкам?

Используйте фильтр `links:`:
```python
search_vault("my-vault", "links:Flask App")
```

Находит заметки, которые ссылаются на указанную через `[[Flask App]]`.

### Можно ли искать в нескольких vault'ах одновременно?

Да, используйте `search_multi_vault`:
```python
search_multi_vault(["vault1", "vault2"], "Python async")
```

### Почему поиск медленный?

1. **Проверьте Ollama** — убедитесь, что он запущен и доступен
2. **Используйте фильтры** — они ускоряют поиск
3. **Ограничьте количество результатов** — `limit=5-10` обычно достаточно
4. **Проверьте размер vault'а** — большие vault'ы индексируются дольше

## Индексация

### Сколько времени занимает индексация?

Зависит от размера vault'а:
- Небольшой vault (100-500 файлов): 1-5 минут
- Средний vault (500-2000 файлов): 5-15 минут
- Большой vault (2000+ файлов): 15-60 минут

При повторной индексации используется инкрементальный режим (только изменённые файлы) — ускорение до 10x.

### Нужно ли переиндексировать после изменений?

Нет, есть два способа автоматического обновления:

1. **Инкрементальная индексация:**
   ```bash
   obsidian-kb index-all  # Автоматически обновит только изменённые файлы
   ```

2. **Автоматическое отслеживание:**
   ```bash
   obsidian-kb watch  # Отслеживает изменения в реальном времени
   ```

### Как работает инкрементальная индексация?

Система отслеживает, какие файлы были изменены, и обрабатывает только их. Это ускоряет повторную индексацию в 10-50 раз.

### Можно ли исключить файлы из индексации?

Да, создайте файл `.obsidian-kb-ignore` в корне vault'а:
```
# Игнорировать временные файлы
*.tmp
*.swp

# Игнорировать папки
node_modules/
.git/
```

Подробнее: [USAGE.md](USAGE.md)

## Производительность

### Сколько памяти использует obsidian-kb?

Зависит от размера индекса:
- Небольшой vault: ~50-100 MB
- Средний vault: ~100-500 MB
- Большой vault: ~500 MB - 2 GB

### Как ускорить поиск?

1. **Включите кэширование:**
   ```bash
   export OBSIDIAN_KB_ENABLE_SEARCH_OPTIMIZER=true
   ```

2. **Используйте фильтры** — они сужают область поиска

3. **Ограничьте количество результатов** — `limit=5-10`

4. **Используйте инкрементальную индексацию** — не переиндексируйте всё каждый раз

### Почему Ollama недоступна?

1. Проверьте, что Ollama запущен:
   ```bash
   ollama serve
   ```

2. Проверьте доступность:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. Проверьте модель:
   ```bash
   ollama list
   # Должна быть nomic-embed-text
   ```

Если Ollama недоступна, система автоматически переключится на полнотекстовый поиск (FTS).

## Проблемы и решения

### Ошибка "Vault not found"

1. Проверьте, что vault добавлен в конфигурацию:
   ```bash
   obsidian-kb config list-vaults
   ```

2. Проверьте путь к vault'у:
   ```bash
   obsidian-kb config show-vault "my-vault"
   ```

3. Убедитесь, что vault проиндексирован:
   ```bash
   obsidian-kb index --vault "my-vault"
   ```

### Ошибка "Ollama connection error"

1. Убедитесь, что Ollama запущен:
   ```bash
   ollama serve
   ```

2. Проверьте URL Ollama (по умолчанию `http://localhost:11434`)

3. Проверьте модель:
   ```bash
   ollama pull nomic-embed-text
   ```

Система автоматически переключится на FTS поиск, если Ollama недоступна.

### Поиск не находит заметки

1. **Проверьте индексацию:**
   ```bash
   obsidian-kb stats --vault "my-vault"
   ```

2. **Переиндексируйте:**
   ```bash
   obsidian-kb reindex --vault "my-vault"
   ```

3. **Проверьте фильтры** — возможно, они слишком строгие

4. **Используйте более общий запрос** — семантический поиск работает лучше с естественными запросами

### Результаты поиска нерелевантны

1. **Включите оптимизатор:**
   ```bash
   export OBSIDIAN_KB_ENABLE_SEARCH_OPTIMIZER=true
   export OBSIDIAN_KB_ENABLE_RERANK=true
   ```

2. **Используйте фильтры** для уточнения поиска

3. **Используйте более конкретные запросы**

4. **Проверьте качество заметок** — хорошо структурированные заметки дают лучшие результаты

Подробнее: [SEARCH_OPTIMIZATION.md](SEARCH_OPTIMIZATION.md)

## Настройка и оптимизация

### Как настроить оптимизацию для агентов?

Добавьте в переменные окружения:
```bash
export OBSIDIAN_KB_ENABLE_SEARCH_OPTIMIZER=true
export OBSIDIAN_KB_ENABLE_RERANK=true
export OBSIDIAN_KB_ENABLE_FEATURE_RANKING=true
export OBSIDIAN_KB_ADAPTIVE_ALPHA=true
```

Подробнее: [AGENT_OPTIMIZATION_SUMMARY.md](AGENT_OPTIMIZATION_SUMMARY.md)

### Как изменить размер чанков?

В конфигурации (через переменные окружения):
```bash
export OBSIDIAN_KB_CHUNK_SIZE=2000
export OBSIDIAN_KB_CHUNK_OVERLAP=250
```

### Как изменить вес гибридного поиска?

```bash
export OBSIDIAN_KB_HYBRID_ALPHA=0.7
```

`alpha=0.7` означает 70% векторного поиска, 30% полнотекстового.

## Дополнительные вопросы

### Поддерживаются ли другие форматы файлов?

Да, поддерживаются:
- Markdown (`.md`)
- PDF (`.pdf`)
- DOCX (`.docx`)

### Можно ли использовать с другими базами знаний?

obsidian-kb специально разработан для Obsidian vault'ов, но может работать с любыми директориями, содержащими markdown-файлы.

### Как получить помощь?

1. Проверьте документацию: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Запустите диагностику: `obsidian-kb doctor`
3. Проверьте логи: `obsidian-kb serve` (для отладки)

### Как внести вклад в проект?

См. [CONTRIBUTING.md](CONTRIBUTING.md)

## Миграция на схему v4

### Что такое схема v4?

**Версия 0.2.0+** использует новую схему базы данных v4 с нормализованной структурой. Вместо одной таблицы теперь используется 4 таблицы:
- `documents` — метаданные документов
- `chunks` — чанки с текстом и векторами
- `document_properties` — свойства документов из frontmatter (типы, авторы и т.д.)
- `metadata` — полный frontmatter в JSON формате

### Нужно ли переиндексировать vault'ы после обновления?

**Да**, после обновления до версии 0.2.0+ необходимо переиндексировать все vault'ы:

```bash
# Переиндексация одного vault'а
obsidian-kb reindex --vault "my-vault" --force

# Переиндексация всех vault'ов
obsidian-kb index-all
```

### Что происходит при переиндексации?

1. Старые таблицы v3 удаляются
2. Создаются новые таблицы v4
3. Файлы индексируются заново с новой структурой
4. **Исходные файлы остаются на диске** — данные не теряются

### Преимущества схемы v4

- **Лучшая производительность** — двухэтапные запросы для фильтрации по свойствам
- **Масштабируемость** — работает быстро даже с миллионами чанков
- **Гибкость** — поддержка произвольных свойств из frontmatter без изменения схемы
- **Эффективные индексы** — индексы на свойствах документов для быстрого поиска

### Ошибка "Cannot perform full text search unless an INVERTED index has been created"

Эта ошибка исправлена в версии **0.2.6+**. FTS индекс теперь создается автоматически при первом поиске, если его нет. Если вы видите эту ошибку:

1. Обновите obsidian-kb до версии 0.2.6+:
   ```bash
   uv pip install --upgrade obsidian-kb
   ```

2. Выполните поиск — индекс создастся автоматически

3. Или переиндексируйте vault:
   ```bash
   obsidian-kb reindex --vault "my-vault" --force
   ```

