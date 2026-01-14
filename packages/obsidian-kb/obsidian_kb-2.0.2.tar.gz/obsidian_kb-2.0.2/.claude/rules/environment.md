# Правила окружения для obsidian-kb

## Виртуальная среда

**ВАЖНО:** Все тесты и Python код должны запускаться через виртуальную среду проекта.

### Запуск тестов
```bash
# Правильно - через venv
.venv/bin/pytest tests/ -v

# НЕ использовать без venv
# pytest tests/  # НЕПРАВИЛЬНО
# python -m pytest  # НЕПРАВИЛЬНО
```

### Запуск Python скриптов
```bash
# Правильно
.venv/bin/python -c "..."
.venv/bin/python script.py

# НЕ использовать системный Python
# python script.py  # НЕПРАВИЛЬНО
```

### Проверка импортов
```bash
.venv/bin/python -c "from obsidian_kb.module import Class; print('OK')"
```

## Тестирование

- Все 745 тестов должны проходить после каждого изменения
- Запускать тесты после каждого рефакторинга
- Использовать `-x` для остановки при первой ошибке: `.venv/bin/pytest tests/ -x -q`
- Для быстрой проверки: `.venv/bin/pytest tests/ -x -q 2>&1 | tail -15`

## Структура проекта

```
src/obsidian_kb/
├── core/                  # Базовые абстракции (TTLCache, DataNormalizer, DBConnectionManager)
├── storage/builders/      # Построители записей (ChunkRecordBuilder, DocumentRecordBuilder)
├── providers/             # LLM провайдеры (BaseProvider, Ollama, Yandex)
├── enrichment/strategies/ # Стратегии обогащения (BaseEnrichmentStrategy)
└── lance_db.py            # God Object для рефакторинга в Phase 3
```

## Дорожная карта

См. `ROADMAP_v0.7.0.md` для текущего статуса и планов.
