# Решение проблем

## Диагностика

Начните с проверки статуса системы:

```bash
obsidian-kb doctor
```

Команда проверит все компоненты и покажет проблемы.

## Типичные проблемы

### Ollama недоступна

**Симптомы:** Ошибки при индексировании или поиске, сообщение "Ollama connection error"

**Решение:**
```bash
# Проверить статус
brew services list | grep ollama

# Запустить Ollama
brew services start ollama

# Проверить доступность
curl http://localhost:11434/api/tags

# Проверить наличие модели
ollama list
# Должна быть видна модель nomic-embed-text
```

Если модель отсутствует:
```bash
ollama pull nomic-embed-text
```

### Vault не найден

**Симптомы:** Ошибка "VaultNotFoundError" при поиске

**Решение:**
```bash
# Проверить список проиндексированных vault'ов
obsidian-kb list-vaults

# Проверить конфигурацию
obsidian-kb config show

# Переиндексировать vault
obsidian-kb index-all
```

### Агент не видит инструменты

**Симптомы:** В Claude Desktop нет инструментов obsidian-kb

**Решение:**

1. Проверьте конфигурацию Claude Desktop:
```bash
obsidian-kb claude-config
```

2. Примените конфигурацию:
```bash
obsidian-kb claude-config --apply
```

3. Перезапустите Claude Desktop

4. Проверьте логи Claude Desktop (если доступны)

5. Запустите MCP сервер вручную для отладки:
```bash
obsidian-kb serve
```

### Проблемы с парсингом frontmatter

**Симптомы:** Предупреждения в логах о неудачном парсинге YAML

**Причина:** Obsidian шаблоны типа `{{date:YYYY-MM-DD}}` не являются валидным YAML

**Решение:** ✅ **Исправлено** — система автоматически обрабатывает шаблоны Obsidian. Если парсинг всё же не удаётся, система пропускает некорректный frontmatter и продолжает работу.

### Пробелы в именах vault'ов

**Примечание:** Vault'ы с пробелами в именах (например, "Naumen CTO") автоматически нормализуются для использования в базе данных. Это не влияет на работу системы.

### Ошибка "Repository not found" при установке через Homebrew

**Симптомы:**
```
Error: Failure while executing; `git clone https://github.com/mdemyanov/homebrew-obsidian-kb ...` exited with 128.
remote: Repository not found.
```

**Решение:**

**Вариант 1: Установка из локальной формулы**
```bash
git clone https://github.com/mdemyanov/obsidian-kb.git
cd obsidian-kb
brew install --build-from-source Formula/obsidian-kb.rb
```

**Вариант 2: Установка через PyPI**
```bash
uv pip install obsidian-kb
```

**Вариант 3: Установка из исходников**
```bash
git clone https://github.com/mdemyanov/obsidian-kb.git
cd obsidian-kb
uv sync
```

### Валидация конфигурации

**Симптомы:** Ошибки при запуске или индексировании, связанные с конфигурацией vault'ов

**Решение:**
```bash
# Проверить конфигурацию
obsidian-kb config show

# Валидация выполняется автоматически при:
# - Запуске MCP сервера
# - Выполнении команды index-all
# - Добавлении нового vault через config add-vault
```

Система автоматически проверяет:
- Существование путей к vault'ам
- Доступность vault'ов на чтение
- Корректность JSON конфигурации
- Доступность директории базы данных на запись

### Проблемы с сервисом (macOS)

**Симптомы:** Сервис не запускается или работает некорректно

**Решение:**
```bash
# Проверить статус
obsidian-kb service-status

# Перезапустить сервис
obsidian-kb restart-service

# Проверить логи
cat /tmp/obsidian-kb.error.log
cat /tmp/obsidian-kb.log
```

Если проблемы продолжаются:
```bash
# Удалить сервис
obsidian-kb uninstall-service

# Переустановить
obsidian-kb install-service
```

### Медленный поиск

**Симптомы:** Поиск выполняется долго (> 1 секунды)

**Возможные причины:**
- Ollama работает медленно
- База данных не оптимизирована
- Слишком много результатов

**Решение:**
```bash
# Проверить статус Ollama
obsidian-kb doctor --check ollama

# Ограничить количество результатов
obsidian-kb search --vault "my-vault" --query "..." --limit 5

# Проверить производительность БД
obsidian-kb doctor --check performance
```

### Проблемы с индексацией

**Симптомы:** Файлы не индексируются или индексируются некорректно

**Решение:**
```bash
# Проверить, не игнорируются ли файлы
# Проверьте файл .obsidian-kb-ignore в корне vault'а

# Переиндексировать vault
obsidian-kb reindex --vault "my-vault" --force

# Проверить логи
obsidian-kb index-all --verbose
```

## Получение помощи

1. **Проверьте документацию:**
   - [INSTALLATION.md](INSTALLATION.md) — установка
   - [CONFIGURATION.md](CONFIGURATION.md) — настройка
   - [USAGE.md](USAGE.md) — использование
   - [MCP_INTEGRATION.md](MCP_INTEGRATION.md) — интеграция с агентами

2. **Запустите диагностику:**
   ```bash
   obsidian-kb doctor
   ```

3. **Проверьте логи:**
   ```bash
   # Логи сервиса (macOS)
   cat /tmp/obsidian-kb.error.log
   cat /tmp/obsidian-kb.log
   ```

4. **Создайте issue на GitHub** с информацией:
   - Версия obsidian-kb (`obsidian-kb version`)
   - Результат `obsidian-kb doctor`
   - Описание проблемы
   - Шаги для воспроизведения

