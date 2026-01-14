"""SearchHelp MCP Tool implementation."""

from typing import Any

from obsidian_kb.mcp.base import InputSchema, MCPTool


class SearchHelpTool(MCPTool):
    """Tool to display search syntax help."""

    @property
    def name(self) -> str:
        return "search_help"

    @property
    def description(self) -> str:
        return """Справка по синтаксису поиска в obsidian-kb.

Returns:
    Справка по синтаксису поиска в markdown формате с примерами:
    - Базовый поиск
    - Фильтры по тегам, типам, датам
    - OR и NOT операторы
    - Комбинирование фильтров"""

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        """Return search syntax help."""
        return """# Справка по синтаксису поиска

## Базовый поиск

```
search_vault("vault-name", "Python async")
```

## Фильтры

### Теги (AND по умолчанию)
```
tags:python
tags:python async
tags:python,async,test
```

### Теги с OR оператором
```
tags:python OR tags:javascript
tags:python OR tags:javascript OR tags:typescript
```

### Теги с NOT оператором
```
tags:python NOT tags:deprecated
tags:python NOT tags:archived
```

### Тип документа
```
type:протокол
type:договор
```

### Тип документа с OR
```
type:протокол OR type:договор
```

### Тип документа с NOT
```
type:протокол NOT type:архив
```

### Даты
```
created:2024-01-01
created:>2024-01-01
created:>=2024-01-01
modified:2024-12-31
```

### Связанные заметки (wikilinks)
```
links:Python
links:Python OR links:Flask
links:Python NOT links:deprecated
```

## Комбинирование фильтров

Все фильтры можно комбинировать:

```
Python tags:python OR tags:javascript type:протокол created:>2024-01-01
tags:python NOT tags:deprecated type:документ
```

## Автодополнение

Используйте инструменты для получения списков:
- `list_tags(vault_name)` - список всех тегов
- `list_doc_types(vault_name)` - список типов документов
- `list_links(vault_name)` - список wikilinks

## Примеры

```python
# Поиск с OR
search_vault("vault", "tags:python OR tags:javascript")

# Поиск с NOT
search_vault("vault", "tags:python NOT tags:deprecated")

# Комбинация
search_vault("vault", "type:протокол tags:python OR tags:javascript created:>2024-01-01")
```
"""
