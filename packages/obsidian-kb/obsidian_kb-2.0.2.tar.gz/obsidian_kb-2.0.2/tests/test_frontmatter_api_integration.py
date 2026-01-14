"""Integration-тесты для FrontmatterAPI (v6) с реальной БД."""

import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from obsidian_kb.service_container import ServiceContainer, reset_service_container
from obsidian_kb.types import DocumentChunk
from obsidian_kb.vault_indexer import VaultIndexer

# Импорт утилиты для индексации
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from tests.utils.indexing import index_vault_for_tests


@pytest.fixture
def temp_db():
    """Создание временной БД для тестов."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_db.lance"
        yield db_path


@pytest.fixture
def service_container(temp_db):
    """Создание контейнера сервисов для тестов."""
    reset_service_container()
    container = ServiceContainer(db_path=temp_db)
    yield container
    try:
        import asyncio
        asyncio.run(container.cleanup())
    except Exception:
        pass
    reset_service_container()


@pytest.fixture
def test_vault_with_frontmatter():
    """Создание тестового vault'а с разнообразным frontmatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir) / "test_vault"
        vault_path.mkdir()
        
        # Файл с типом person
        (vault_path / "person1.md").write_text(
            """---
type: person
name: Иван Иванов
role: developer
team: backend
status: active
created: 2024-01-01
tags: [person, developer]
---

# Иван Иванов

Разработчик команды.
""",
            encoding="utf-8",
        )
        
        # Файл с типом person (другой)
        (vault_path / "person2.md").write_text(
            """---
type: person
name: Петр Петров
role: manager
team: frontend
status: active
created: 2024-02-01
tags: [person, manager]
---

# Петр Петров

Менеджер проекта.
""",
            encoding="utf-8",
        )
        
        # Файл с типом task
        (vault_path / "task1.md").write_text(
            """---
type: task
title: Реализовать API
status: in-progress
priority: high
assignee: Иван Иванов
created: 2024-03-01
tags: [task, api]
---

# Реализовать API

Описание задачи.
""",
            encoding="utf-8",
        )
        
        # Файл с типом task (другой статус)
        (vault_path / "task2.md").write_text(
            """---
type: task
title: Написать тесты
status: done
priority: medium
assignee: Петр Петров
created: 2024-03-15
tags: [task, tests]
---

# Написать тесты

Описание задачи.
""",
            encoding="utf-8",
        )
        
        # Файл без frontmatter
        (vault_path / "note.md").write_text(
            """# Простая заметка

Без frontmatter.
""",
            encoding="utf-8",
        )
        
        yield vault_path


@pytest_asyncio.fixture(scope="session")
async def indexed_vault_session(tmp_path_factory):
    """Session-scoped фикстура для проиндексированного vault'а.
    
    Индексация выполняется один раз для всех тестов в сессии.
    """
    import asyncio
    
    # Создаём временную БД для сессии
    db_path = tmp_path_factory.mktemp("session_db") / "test_db.lance"
    
    # Создаём тестовый vault
    vault_path = tmp_path_factory.mktemp("session_vault") / "test_vault"
    vault_path.mkdir()
    
    # Создаём тестовые файлы (копируем логику из test_vault_with_frontmatter)
    (vault_path / "person1.md").write_text(
        """---
type: person
name: Иван Иванов
role: developer
team: backend
status: active
created: 2024-01-01
tags: [person, developer]
---

# Иван Иванов

Разработчик команды.
""",
        encoding="utf-8",
    )
    
    (vault_path / "person2.md").write_text(
        """---
type: person
name: Петр Петров
role: manager
team: frontend
status: active
created: 2024-02-01
tags: [person, manager]
---

# Петр Петров

Менеджер проекта.
""",
        encoding="utf-8",
    )
    
    (vault_path / "task1.md").write_text(
        """---
type: task
title: Реализовать API
status: in-progress
priority: high
assignee: Иван Иванов
created: 2024-03-01
tags: [task, api]
---

# Реализовать API

Описание задачи.
""",
        encoding="utf-8",
    )
    
    (vault_path / "task2.md").write_text(
        """---
type: task
title: Написать тесты
status: done
priority: medium
assignee: Петр Петров
created: 2024-03-15
tags: [task, tests]
---

# Написать тесты

Описание задачи.
""",
        encoding="utf-8",
    )
    
    (vault_path / "note.md").write_text(
        """# Простая заметка

Без frontmatter.
""",
        encoding="utf-8",
    )
    
    # Инициализируем сервисы
    reset_service_container()
    services = ServiceContainer(db_path=db_path)
    
    try:
        # Индексируем vault один раз для всей сессии
        vault_name = "test_vault"
        result = await index_vault_for_tests(
            services,
            vault_path,
            vault_name,
        )
        
        yield vault_name, vault_path, services
        
    finally:
        await services.cleanup()
        reset_service_container()


@pytest_asyncio.fixture
async def indexed_vault(indexed_vault_session):
    """Проиндексированный vault для тестов (использует session-scoped).
    
    Эта фикстура использует уже проиндексированный vault из session-scoped фикстуры.
    Использует тот же ServiceContainer для доступа к данным.
    """
    vault_name, vault_path, services = indexed_vault_session
    
    # Используем тот же ServiceContainer из session-scoped фикстуры
    # Это позволяет переиспользовать индексацию и данные
    yield vault_name, vault_path, services


@pytest.mark.asyncio
async def test_indexing_works(indexed_vault_session):
    """Отдельный тест индексации vault'а.
    
    Проверяет, что индексация работает корректно.
    """
    vault_name, vault_path, services = indexed_vault_session
    
    vault_stats = await services.db_manager.get_vault_stats(vault_name)
    
    assert vault_stats.file_count > 0, "Должны быть проиндексированы файлы"
    assert vault_stats.chunk_count > 0, "Должны быть созданы чанки"
    assert len(vault_stats.tags) > 0, "Должны быть найдены теги"


@pytest.mark.asyncio
class TestFrontmatterAPIIntegration:
    """Integration-тесты для FrontmatterAPI с реальной БД."""

    async def test_get_frontmatter_existing_file(
        self, indexed_vault
    ):
        """Получение frontmatter существующего файла."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        result = await api.get_frontmatter(vault_name, "person1.md")
        
        assert result is not None
        assert result["type"] == "person"
        assert result["name"] == "Иван Иванов"
        assert result["role"] == "developer"
        assert result["status"] == "active"

    async def test_get_frontmatter_nonexistent_file(
        self, indexed_vault
    ):
        """Получение frontmatter несуществующего файла."""
        vault_name, _, services = indexed_vault
        api = services.frontmatter_api
        
        result = await api.get_frontmatter(vault_name, "nonexistent.md")
        
        assert result is None

    async def test_get_schema_all_documents(
        self, indexed_vault, service_container
    ):
        """Получение схемы всех документов."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        schema = await api.get_schema(vault_name)
        
        assert schema.vault_name == vault_name
        assert schema.total_documents > 0
        assert len(schema.fields) > 0
        
        # Проверяем наличие ожидаемых полей
        assert "type" in schema.fields
        assert "status" in schema.fields
        assert "role" in schema.fields or "priority" in schema.fields
        
        # Проверяем структуру FieldInfo
        from obsidian_kb.types import FieldInfo
        type_field = schema.fields["type"]
        assert isinstance(type_field, FieldInfo)
        assert type_field.field_name == "type"
        assert type_field.document_count > 0
        assert len(type_field.unique_values) > 0

    async def test_get_schema_with_doc_type_filter(
        self, indexed_vault, service_container
    ):
        """Получение схемы с фильтром по типу документа."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        schema = await api.get_schema(vault_name, doc_type="person")
        
        assert schema.vault_name == vault_name
        assert schema.doc_type_filter == "person"
        assert schema.total_documents >= 2  # person1.md и person2.md
        
        # Проверяем, что поля относятся к типу person
        if "role" in schema.fields:
            assert schema.fields["role"].document_count >= 2
        if "team" in schema.fields:
            assert schema.fields["team"].document_count >= 2

    async def test_list_by_property_with_value(
        self, indexed_vault, service_container
    ):
        """Поиск документов по свойству с конкретным значением."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        results = await api.list_by_property(vault_name, "status", "active")
        
        assert len(results) >= 2  # person1 и person2
        
        # Проверяем структуру результатов
        for doc in results:
            assert "document_id" in doc
            assert "file_path" in doc
            assert "title" in doc
            assert doc.get("file_path") in ["person1.md", "person2.md"]

    async def test_list_by_property_without_value(
        self, indexed_vault, service_container
    ):
        """Поиск документов по свойству без указания значения."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        results = await api.list_by_property(vault_name, "status", limit=10)
        
        assert len(results) > 0
        
        # Проверяем, что все результаты имеют поле status
        for doc in results:
            assert "file_path" in doc

    async def test_aggregate_by_property(
        self, indexed_vault, service_container
    ):
        """Агрегация по свойству."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        result = await api.aggregate_by_property(vault_name, "status")
        
        assert result.property_key == "status"
        assert result.total_documents > 0
        
        # Проверяем наличие ожидаемых значений
        assert "active" in result.values
        assert result.values["active"] >= 2  # person1 и person2
        
        if "in-progress" in result.values:
            assert result.values["in-progress"] >= 1  # task1
        
        if "done" in result.values:
            assert result.values["done"] >= 1  # task2

    async def test_aggregate_by_property_with_doc_type(
        self, indexed_vault, service_container
    ):
        """Агрегация по свойству с фильтром по типу документа."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        # Агрегация по status для типа task
        result = await api.aggregate_by_property(vault_name, "status", doc_type="task")
        
        assert result.property_key == "status"
        assert result.total_documents >= 2  # task1 и task2
        
        # Проверяем значения статусов для задач
        if "in-progress" in result.values:
            assert result.values["in-progress"] >= 1
        if "done" in result.values:
            assert result.values["done"] >= 1

    async def test_get_property_values(
        self, indexed_vault, service_container
    ):
        """Получение уникальных значений свойства."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        result = await api.get_property_values(vault_name, "status", limit=10)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Проверяем формат: список кортежей (значение, количество)
        for value, count in result:
            assert isinstance(value, str)
            assert isinstance(count, int)
            assert count > 0
        
        # Проверяем сортировку по убыванию количества
        if len(result) > 1:
            assert result[0][1] >= result[1][1]

    async def test_get_property_values_limit(
        self, indexed_vault, service_container
    ):
        """Получение уникальных значений с ограничением."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        result = await api.get_property_values(vault_name, "status", limit=1)
        
        assert len(result) <= 1

    async def test_get_schema_field_types(
        self, indexed_vault, service_container
    ):
        """Проверка определения типов полей в схеме."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        schema = await api.get_schema(vault_name)
        
        # Проверяем, что типы полей определены корректно
        for field_name, field_info in schema.fields.items():
            assert field_info.field_type in ["string", "list", "date", "number", "boolean"]
            assert field_info.document_count > 0
            assert field_info.unique_count > 0
            assert field_info.nullable_count >= 0

    async def test_get_schema_common_patterns(
        self, indexed_vault, service_container
    ):
        """Проверка поиска частых комбинаций полей."""
        vault_name, vault_path, services = indexed_vault
        api = services.frontmatter_api
        
        schema = await api.get_schema(vault_name)
        
        # Проверяем, что common_patterns - это список строк
        assert isinstance(schema.common_patterns, list)
        for pattern in schema.common_patterns:
            assert isinstance(pattern, str)
            assert " + " in pattern  # Формат "field1 + field2"

