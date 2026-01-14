# Установка obsidian-kb

**Версия:** 0.7.0 (Architecture & Performance Release)

## Требования

- Python 3.12+
- Ollama с моделью `nomic-embed-text` (запущена на `localhost:11434`) — для локального использования
- Или Yandex Cloud API ключи — для облачного провайдера
- macOS (Apple Silicon) — для автозапуска через launchd (опционально)
- Claude Desktop с поддержкой MCP (для использования с агентами)

---

## 1. Установка Python

### Проверка установки Python

Сначала проверьте, что Python 3.12+ установлен:

```bash
python3 --version
# Должно быть: Python 3.12.x или выше
```

### Установка Python (если не установлен)

**macOS:**
```bash
# Через Homebrew
brew install python@3.12

# Или скачайте с python.org
# https://www.python.org/downloads/
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

# Fedora
sudo dnf install python3.12 python3-pip
```

### Создание виртуального окружения

**Способ 1: Использование venv (стандартный способ)**

```bash
# Создайте виртуальное окружение
python3 -m venv .venv

# Активируйте виртуальное окружение
# На macOS/Linux:
source .venv/bin/activate

# На Windows:
# .venv\Scripts\activate
```

**Способ 2: Использование uv (рекомендуется для obsidian-kb)**

```bash
# Установите uv (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# uv автоматически создаст виртуальное окружение и установит зависимости
uv sync
```

uv автоматически:
- Создаст виртуальное окружение `.venv`
- Установит все зависимости из `pyproject.toml`
- Настроит правильную версию Python

> **Примечание:** Для obsidian-kb рекомендуется использовать `uv`, так как это упрощает управление зависимостями.

---

## 2. Установка Ollama

### macOS (Apple Silicon)

**Способ 1: Homebrew (рекомендуется)**

```bash
# Установить Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установить Ollama
brew install ollama

# Запустить Ollama как сервис (автозапуск)
brew services start ollama

# Или запустить вручную
ollama serve
```

**Способ 2: Официальный установщик**

1. Скачайте установщик с [https://ollama.ai/download](https://ollama.ai/download)
2. Установите приложение
3. Запустите Ollama из Applications

### Установка модели для embeddings

```bash
# Установить модель nomic-embed-text (рекомендуется для длинных текстов)
ollama pull nomic-embed-text

# Проверить установку
ollama list
# Должна быть видна модель nomic-embed-text
```

> **Примечание:** Модель `nomic-embed-text` обеспечивает большое контекстное окно (до 8000 токенов), что позволяет обрабатывать длинные документы без агрессивной обрезки. Размерность модели — 768 (меньше, чем у `mxbai-embed-large`, но компенсируется большим контекстом).

### Проверка работы Ollama

```bash
# Проверить версию
ollama --version

# Проверить список моделей
ollama list

# Проверить, что сервер запущен
curl http://localhost:11434/api/tags
# Должен вернуть JSON с моделями
```

### Устранение проблем с Ollama

**Ollama не найдена в PATH:**

```bash
# Проверить установку
ls -la /usr/local/bin/ollama
ls -la ~/.local/bin/ollama

# Добавить в PATH (если нужно)
export PATH="/usr/local/bin:$PATH"
# Или для постоянного добавления:
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## 3. Установка obsidian-kb

### Способ 1: Через PyPI (рекомендуется)

```bash
# Убедитесь, что виртуальное окружение активировано
source .venv/bin/activate  # macOS/Linux

# Установите через uv (рекомендуется)
uv pip install obsidian-kb

# Или через pip
pip install obsidian-kb
```

После установки команда `obsidian-kb` будет доступна в активированном виртуальном окружении.

### Способ 2: Из исходников

```bash
# Установите uv (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Клонируйте репозиторий
git clone https://github.com/mdemyanov/obsidian-kb.git
cd obsidian-kb

# Установите зависимости
uv sync
```

После установки используйте команды через `uv run`:
```bash
uv run obsidian-kb --help
```

---

## 4. Проверка установки

```bash
# Проверить версию
obsidian-kb version

# Проверить статус системы
obsidian-kb doctor
```

Команда `doctor` проверит:
- Доступность Ollama и наличие модели
- Подключение к базе данных
- Наличие vault'ов в конфигурации
- Свободное место на диске

---

## 5. Обновление

```bash
# Убедитесь, что виртуальное окружение активировано
source .venv/bin/activate

# Обновить через uv
uv pip install --upgrade obsidian-kb

# Проверить версию
obsidian-kb version
```

---

## 6. Автозапуск (macOS)

Для автоматического запуска MCP сервера:

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

> **Примечание:** Автозапуск работает только на macOS через launchd.

### Удаление сервиса перед переустановкой

Если вы переустанавливаете сервис, сначала удалите существующий:

```bash
# Через команду obsidian-kb (рекомендуется)
obsidian-kb uninstall-service

# Или вручную через launchctl
launchctl unload ~/Library/LaunchAgents/com.obsidian-kb.plist
rm ~/Library/LaunchAgents/com.obsidian-kb.plist
```

---

## Устранение проблем

### Проблема: "python3: command not found"

**Решение:**
```bash
# Проверьте, установлен ли Python
which python3

# Если не установлен, установите через пакетный менеджер
# macOS: brew install python@3.12
# Linux: sudo apt install python3.12
```

### Проблема: "No module named venv"

**Решение:**
```bash
# Установите python3-venv
# macOS: обычно уже установлен
# Linux:
sudo apt install python3.12-venv
```

### Проблема: Зависимости не устанавливаются

**Решение:**
```bash
# Обновите pip
python3 -m pip install --upgrade pip

# Попробуйте установить снова
pip install obsidian-kb
```

---

## Следующие шаги

После установки:

1. Настройте конфигурацию vault'ов (см. [CONFIGURATION.md](CONFIGURATION.md))
2. Проиндексируйте vault'ы (см. [USAGE.md](USAGE.md))
3. Настройте интеграцию с Claude Desktop (см. [MCP_INTEGRATION.md](MCP_INTEGRATION.md))

---

## Рекомендации

1. **Всегда используйте виртуальное окружение** для проектов Python
2. **Не коммитьте `.venv`** в Git (уже добавлено в `.gitignore`)
3. **Используйте `uv`** для obsidian-kb — это упрощает управление зависимостями
4. **Активируйте окружение** перед работой с проектом
5. **Обновляйте зависимости** регулярно: `uv pip install --upgrade obsidian-kb` (для установленного пакета) или `uv sync` (для режима разработки)

---

## Дополнительная информация

- [Официальная документация Python venv](https://docs.python.org/3/library/venv.html)
- [Документация uv](https://github.com/astral-sh/uv)
- [Документация Ollama](https://ollama.ai/)
- [Руководство по pip](https://pip.pypa.io/en/stable/)
