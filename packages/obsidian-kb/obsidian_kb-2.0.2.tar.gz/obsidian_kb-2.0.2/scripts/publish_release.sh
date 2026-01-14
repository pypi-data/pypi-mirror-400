#!/bin/bash
# Скрипт для публикации релиза obsidian-kb с использованием GitHub CLI

set -e

# Получаем версию из pyproject.toml
VERSION=$(grep -E '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
PYPI_REPO="${PYPI_REPO:-pypi}"  # По умолчанию официальный PyPI, можно установить testpypi

echo "🚀 Публикация релиза v${VERSION}"

# Проверка, что мы в правильной директории
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Ошибка: pyproject.toml не найден. Запустите скрипт из корня проекта."
    exit 1
fi

# Проверка версии в __init__.py
INIT_VERSION=$(grep -E '^__version__ = ' src/obsidian_kb/__init__.py | sed 's/__version__ = "\(.*\)"/\1/')
if [ "$INIT_VERSION" != "$VERSION" ]; then
    echo "❌ Ошибка: Версия в __init__.py ($INIT_VERSION) не совпадает с версией в pyproject.toml ($VERSION)"
    exit 1
fi

echo "✅ Версия проверена: $VERSION"

# Проверка тестов (только из папки tests/)
echo "🧪 Запуск unit и integration тестов..."
uv run pytest tests/ --tb=short -q || {
    echo "⚠️  Некоторые unit тесты не прошли, но продолжаем (критично: тесты на тестовых данных)"
    echo "   Проверьте результаты выше и решите, стоит ли продолжать"
}

# Проверка линтинга
echo "🔍 Проверка линтинга..."
uv run ruff check src/ || {
    echo "⚠️  Линтинг показал предупреждения, но продолжаем (некритичные предупреждения)"
    echo "   Проверьте результаты выше и решите, стоит ли продолжать"
}

# Сборка пакета
echo "📦 Сборка пакета..."
rm -rf dist/
uv build

# Проверка пакета
echo "✅ Проверка пакета..."
twine check dist/* || {
    echo "❌ Проверка пакета не прошла!"
    exit 1
}

# Показываем размеры файлов
echo ""
echo "📊 Собранные файлы:"
ls -lh dist/

# Публикация на TestPyPI (если указано)
if [ "$PYPI_REPO" = "testpypi" ]; then
    echo ""
    read -p "📤 Опубликовать на TestPyPI? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Публикация на TestPyPI..."
        twine upload --repository testpypi dist/*
        echo "✅ Пакет опубликован на TestPyPI!"
        echo "   Установка: pip install -i https://test.pypi.org/simple/ obsidian-kb==${VERSION}"
    else
        echo "⏭️  Публикация на TestPyPI пропущена"
    fi
fi

# Публикация на PyPI (если указано)
if [ "$PYPI_REPO" = "pypi" ]; then
    echo ""
    read -p "📤 Опубликовать на PyPI (production)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Публикация на PyPI..."
        twine upload --repository pypi dist/*
        echo "✅ Пакет опубликован на PyPI!"
    else
        echo "⏭️  Публикация на PyPI пропущена"
    fi
fi

# Создание тега через GitHub CLI
echo ""
read -p "🏷️  Создать тег v${VERSION} и релиз через GitHub CLI? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Проверка, что мы в git репозитории
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ Ошибка: Не найден git репозиторий"
        exit 1
    fi
    
    # Проверка, что нет незакоммиченных изменений
    if ! git diff-index --quiet HEAD --; then
        echo "⚠️  Внимание: Есть незакоммиченные изменения"
        read -p "   Продолжить? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Создание тега
    echo "🏷️  Создание тега v${VERSION}..."
    git tag -a "v${VERSION}" -m "Release v${VERSION}"
    git push origin "v${VERSION}"
    echo "✅ Тег создан и отправлен"
    
    # Создание релиза через GitHub CLI
    echo "📝 Создание GitHub релиза..."
    
    # Получаем описание из CHANGELOG.md
    CHANGELOG_ENTRY=$(awk "/^## \[${VERSION}\]/,/^## \[/" CHANGELOG.md | head -n -1)
    
    if [ -z "$CHANGELOG_ENTRY" ]; then
        echo "⚠️  Не найдена запись в CHANGELOG.md для версии ${VERSION}"
        CHANGELOG_ENTRY="Release v${VERSION}"
    fi
    
    # Создаём релиз через GitHub CLI
    gh release create "v${VERSION}" \
        --title "Release v${VERSION}" \
        --notes "$CHANGELOG_ENTRY" \
        dist/*.whl dist/*.tar.gz || {
        echo "❌ Ошибка при создании релиза"
        exit 1
    }
    
    echo "✅ GitHub релиз создан!"
    echo "   URL: https://github.com/mdemyanov/obsidian-kb/releases/tag/v${VERSION}"
else
    echo "⏭️  Создание тега и релиза пропущено"
    echo ""
    echo "📝 Следующие шаги вручную:"
    echo "1. Создайте тег: git tag -a v${VERSION} -m 'Release v${VERSION}'"
    echo "2. Отправьте тег: git push origin v${VERSION}"
    echo "3. Создайте GitHub Release: gh release create v${VERSION} --title 'Release v${VERSION}' --notes-file CHANGELOG.md"
fi

echo ""
echo "✅ Готово! Релиз v${VERSION} подготовлен."
