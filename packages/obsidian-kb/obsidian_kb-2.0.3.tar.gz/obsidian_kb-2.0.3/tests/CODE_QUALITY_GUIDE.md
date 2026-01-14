# Руководство по проверке качества кода

**Версия:** 1.0  
**Дата:** 2025-01-21  
**Цели:**
- Code coverage >80%
- Cyclomatic complexity <10 для всех методов
- Все линтеры проходят

---

## Установка инструментов

### Обязательные инструменты

```bash
pip install pytest pytest-cov pytest-asyncio
```

### Опциональные инструменты (для детального анализа)

```bash
pip install radon          # Для проверки cyclomatic complexity
pip install ruff          # Быстрый линтер
pip install mypy          # Проверка типов (опционально)
```

---

## Автоматизированная проверка

### Запуск скрипта проверки

```bash
cd /Users/mdemyanov/CursorProjects/obsidian-kb
python tests/check_code_quality.py
```

Скрипт автоматически:
1. Проверяет code coverage
2. Проверяет cyclomatic complexity
3. Проверяет линтеры (ruff, mypy)
4. Генерирует отчёт

---

## Ручная проверка

### 1. Code Coverage

#### Запуск тестов с coverage

```bash
pytest tests/ --cov=src/obsidian_kb --cov-report=term-missing --cov-report=html
```

#### Просмотр результатов

- **В терминале:** результаты отображаются сразу
- **HTML отчёт:** откройте `htmlcov/index.html` в браузере

#### Целевые метрики

- **Общее покрытие:** >80%
- **Критичные модули:** >90% (search, storage, service)
- **Вспомогательные модули:** >70% (utils, helpers)

### 2. Cyclomatic Complexity

#### Установка radon

```bash
pip install radon
```

#### Проверка complexity

```bash
radon cc src/obsidian_kb --min B --json
```

#### Интерпретация результатов

- **A (1-5):** Низкая сложность ✅
- **B (6-10):** Средняя сложность ✅
- **C (11-20):** Высокая сложность ⚠️
- **D (21-30):** Очень высокая сложность ❌
- **E (31+):** Критическая сложность ❌

**Цель:** Все функции должны быть уровня B или ниже (<10)

### 3. Линтеры

#### Ruff (быстрый линтер)

```bash
ruff check src/obsidian_kb
ruff check --fix src/obsidian_kb  # Автоматическое исправление
```

#### Mypy (проверка типов)

```bash
mypy src/obsidian_kb --ignore-missing-imports --no-strict-optional
```

---

## Улучшение качества кода

### Увеличение code coverage

1. **Найдите файлы с низким покрытием:**
   ```bash
   pytest --cov=src/obsidian_kb --cov-report=term-missing | grep -E "TOTAL|%"
   ```

2. **Создайте тесты для непокрытых функций:**
   - Unit-тесты для простых функций
   - Integration-тесты для сложных сценариев
   - Edge cases и error handling

3. **Проверьте покрытие конкретного файла:**
   ```bash
   pytest tests/test_specific.py --cov=src/obsidian_kb/specific_module --cov-report=term-missing
   ```

### Уменьшение cyclomatic complexity

1. **Разбейте сложные функции:**
   - Выделите логические блоки в отдельные функции
   - Используйте ранние возвраты (early returns)
   - Избегайте глубокой вложенности

2. **Пример рефакторинга:**

   **До (сложность 15):**
   ```python
   def complex_function(data):
       if condition1:
           if condition2:
               if condition3:
                   # много кода
   ```

   **После (сложность 5):**
   ```python
   def complex_function(data):
       if not condition1:
           return None
       if not condition2:
           return None
       return _process_data(data)
   
   def _process_data(data):
       # код обработки
   ```

3. **Используйте паттерны:**
   - Strategy pattern для условной логики
   - Command pattern для действий
   - Factory pattern для создания объектов

### Исправление ошибок линтера

1. **Автоматическое исправление:**
   ```bash
   ruff check --fix src/obsidian_kb
   ```

2. **Ручное исправление:**
   - Следуйте рекомендациям ruff
   - Используйте type hints для mypy
   - Следуйте PEP 8 стилю

---

## CI/CD интеграция

### GitHub Actions пример

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]"
      - run: pytest --cov=src/obsidian_kb --cov-report=xml
      - run: radon cc src/obsidian_kb --min B
      - run: ruff check src/obsidian_kb
```

---

## Метрики успеха

| Метрика | Целевое значение | Текущее | Статус |
|---------|------------------|---------|--------|
| Code Coverage | >80% | ⏳ Измерение | ⏳ |
| Cyclomatic Complexity | <10 для всех | ⏳ Измерение | ⏳ |
| Ruff errors | 0 | ⏳ Измерение | ⏳ |
| Mypy errors | 0 (опционально) | ⏳ Измерение | ⏳ |

---

## Отчёт о проблемах

Если обнаружены проблемы качества кода:

1. Задокументируйте проблемные файлы/функции
2. Укажите метрики (coverage, complexity)
3. Предложите план улучшения
4. Создайте issue в репозитории

---

## Контакты

При возникновении вопросов обращайтесь к разработчикам проекта.

