"""Unit-тесты для FrontmatterAPI (v6)."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.services.frontmatter_api import FrontmatterAPI
from obsidian_kb.types import (
    FrontmatterSchema,
    PropertyAggregation,
    VaultNotFoundError,
)


@pytest.fixture
def mock_db_manager():
    """Мок LanceDBManager."""
    manager = MagicMock()
    manager._ensure_table = AsyncMock(return_value=MagicMock())
    return manager


@pytest.fixture
def mock_service_container(mock_db_manager):
    """Мок ServiceContainer."""
    container = MagicMock()
    container.db_manager = mock_db_manager
    return container


@pytest.fixture
def frontmatter_api(mock_service_container):
    """FrontmatterAPI с моками.

    Передаём services напрямую в конструктор чтобы избежать проблем с patch.
    """
    # Передаём services напрямую в конструктор
    api = FrontmatterAPI(services=mock_service_container)
    return api


class TestFrontmatterAPI:
    """Тесты для FrontmatterAPI."""

    @pytest.mark.asyncio
    async def test_get_frontmatter_not_found(self, frontmatter_api, mock_db_manager):
        """Получение frontmatter несуществующего файла."""
        metadata_table = MagicMock()
        metadata_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = []
        mock_db_manager._ensure_table = AsyncMock(return_value=metadata_table)
        
        result = await frontmatter_api.get_frontmatter("test_vault", "nonexistent.md")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_frontmatter_found(self, frontmatter_api, mock_db_manager):
        """Получение frontmatter существующего файла."""
        frontmatter_data = {"type": "person", "name": "Иван Иванов", "role": "CTO"}
        metadata_table = MagicMock()
        metadata_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = [
            {"metadata_json": json.dumps(frontmatter_data)}
        ]
        mock_db_manager._ensure_table = AsyncMock(return_value=metadata_table)
        
        result = await frontmatter_api.get_frontmatter("test_vault", "person.md")
        
        assert result is not None
        assert result == frontmatter_data
        assert result["type"] == "person"
        assert result["name"] == "Иван Иванов"

    @pytest.mark.asyncio
    async def test_get_frontmatter_invalid_json(self, frontmatter_api, mock_db_manager):
        """Получение frontmatter с невалидным JSON."""
        metadata_table = MagicMock()
        metadata_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = [
            {"metadata_json": "invalid json"}
        ]
        mock_db_manager._ensure_table = AsyncMock(return_value=metadata_table)
        
        result = await frontmatter_api.get_frontmatter("test_vault", "file.md")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_frontmatter_vault_not_found(self, frontmatter_api, mock_db_manager):
        """Получение frontmatter из несуществующего vault'а."""
        mock_db_manager._ensure_table = AsyncMock(side_effect=VaultNotFoundError("Vault not found"))
        
        with pytest.raises(VaultNotFoundError):
            await frontmatter_api.get_frontmatter("nonexistent_vault", "file.md")

    @pytest.mark.asyncio
    async def test_get_schema_empty_vault(self, frontmatter_api, mock_db_manager):
        """Получение схемы пустого vault'а."""
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = []
        documents_table = MagicMock()
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=lambda vault, table_type: {
            "document_properties": properties_table,
            "documents": documents_table,
        }[table_type])
        
        schema = await frontmatter_api.get_schema("test_vault")
        
        assert schema.vault_name == "test_vault"
        assert schema.total_documents == 0
        assert len(schema.fields) == 0
        assert schema.doc_type_filter is None

    @pytest.mark.asyncio
    async def test_get_schema_with_fields(self, frontmatter_api, mock_db_manager):
        """Получение схемы vault'а с полями."""
        properties_data = [
            {"document_id": "doc1", "property_key": "type", "property_value": "person"},
            {"document_id": "doc1", "property_key": "name", "property_value": "Иван"},
            {"document_id": "doc2", "property_key": "type", "property_value": "person"},
            {"document_id": "doc2", "property_key": "name", "property_value": "Петр"},
        ]
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = properties_data
        documents_table = MagicMock()
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=lambda vault, table_type: {
            "document_properties": properties_table,
            "documents": documents_table,
        }[table_type])
        
        schema = await frontmatter_api.get_schema("test_vault")
        
        assert schema.vault_name == "test_vault"
        assert schema.total_documents == 2
        assert "type" in schema.fields
        assert "name" in schema.fields
        assert schema.fields["type"].document_count == 2
        assert schema.fields["name"].document_count == 2

    @pytest.mark.asyncio
    async def test_get_schema_with_doc_type_filter(self, frontmatter_api, mock_db_manager):
        """Получение схемы с фильтром по типу документа."""
        # Данные для всех документов
        all_properties = [
            {"document_id": "doc1", "property_key": "type", "property_value": "person"},
            {"document_id": "doc1", "property_key": "name", "property_value": "Иван"},
            {"document_id": "doc2", "property_key": "type", "property_value": "task"},
            {"document_id": "doc2", "property_key": "status", "property_value": "done"},
        ]
        
        # Результат поиска по типу
        type_results = [
            {"document_id": "doc1", "property_key": "type", "property_value": "person"},
        ]
        
        properties_table = MagicMock()
        properties_table.search.return_value.where.return_value.to_list.return_value = type_results
        properties_table.to_arrow.return_value.to_pylist.return_value = all_properties
        documents_table = MagicMock()
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=lambda vault, table_type: {
            "document_properties": properties_table,
            "documents": documents_table,
        }[table_type])
        
        schema = await frontmatter_api.get_schema("test_vault", doc_type="person")
        
        assert schema.doc_type_filter == "person"
        assert schema.total_documents == 1
        assert "name" in schema.fields
        assert "status" not in schema.fields  # Должен быть отфильтрован

    @pytest.mark.asyncio
    async def test_list_by_property_empty(self, frontmatter_api, mock_db_manager):
        """Поиск документов по свойству - пустой результат."""
        properties_table = MagicMock()
        properties_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = []
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = []
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=lambda vault, table_type: {
            "document_properties": properties_table,
            "documents": documents_table,
        }[table_type])
        
        results = await frontmatter_api.list_by_property("test_vault", "status", "done")
        
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_list_by_property_with_value(self, frontmatter_api, mock_db_manager):
        """Поиск документов по свойству с конкретным значением."""
        properties_data = [
            {"document_id": "doc1", "property_key": "status", "property_value": "done"},
            {"document_id": "doc2", "property_key": "status", "property_value": "done"},
        ]
        
        documents_data = [
            {
                "document_id": "doc1",
                "file_path": "file1.md",
                "title": "File 1",
                "created_at": datetime(2024, 1, 1),
                "modified_at": datetime(2024, 1, 2),
            },
            {
                "document_id": "doc2",
                "file_path": "file2.md",
                "title": "File 2",
                "created_at": datetime(2024, 1, 3),
                "modified_at": datetime(2024, 1, 4),
            },
        ]
        
        properties_table = MagicMock()
        properties_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = properties_data
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = documents_data
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=lambda vault, table_type: {
            "document_properties": properties_table,
            "documents": documents_table,
        }[table_type])
        
        results = await frontmatter_api.list_by_property("test_vault", "status", "done")

        assert len(results) == 2
        # Порядок результатов не гарантирован (используется set для doc_ids)
        doc_ids = {r["document_id"] for r in results}
        file_paths = {r["file_path"] for r in results}
        assert doc_ids == {"doc1", "doc2"}
        assert file_paths == {"file1.md", "file2.md"}

    @pytest.mark.asyncio
    async def test_list_by_property_without_value(self, frontmatter_api, mock_db_manager):
        """Поиск документов по свойству без указания значения."""
        properties_data = [
            {"document_id": "doc1", "property_key": "status", "property_value": "done"},
            {"document_id": "doc2", "property_key": "status", "property_value": "pending"},
        ]
        
        documents_data = [
            {
                "document_id": "doc1",
                "file_path": "file1.md",
                "title": "File 1",
                "created_at": datetime(2024, 1, 1),
                "modified_at": datetime(2024, 1, 2),
            },
        ]
        
        properties_table = MagicMock()
        properties_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = properties_data
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = documents_data
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=lambda vault, table_type: {
            "document_properties": properties_table,
            "documents": documents_table,
        }[table_type])
        
        results = await frontmatter_api.list_by_property("test_vault", "status", limit=10)
        
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_aggregate_by_property(self, frontmatter_api, mock_db_manager):
        """Агрегация по свойству."""
        properties_data = [
            {"document_id": "doc1", "property_key": "status", "property_value": "done"},
            {"document_id": "doc2", "property_key": "status", "property_value": "done"},
            {"document_id": "doc3", "property_key": "status", "property_value": "pending"},
            {"document_id": "doc4", "property_key": "status", "property_value": ""},
        ]
        
        properties_table = MagicMock()
        properties_table.search.return_value.where.return_value.to_list.return_value = properties_data
        
        mock_db_manager._ensure_table = AsyncMock(return_value=properties_table)
        
        result = await frontmatter_api.aggregate_by_property("test_vault", "status")
        
        assert isinstance(result, PropertyAggregation)
        assert result.property_key == "status"
        assert result.total_documents == 4
        assert result.values["done"] == 2
        assert result.values["pending"] == 1
        assert result.null_count == 1

    @pytest.mark.asyncio
    async def test_aggregate_by_property_with_doc_type(self, frontmatter_api, mock_db_manager):
        """Агрегация по свойству с фильтром по типу документа."""
        all_properties = [
            {"document_id": "doc1", "property_key": "status", "property_value": "done"},
            {"document_id": "doc2", "property_key": "status", "property_value": "pending"},
        ]
        
        type_properties = [
            {"document_id": "doc1", "property_key": "type", "property_value": "task"},
        ]
        
        properties_table = MagicMock()
        # Первый вызов - поиск по status
        # Второй вызов - поиск по type
        properties_table.search.return_value.where.return_value.to_list.side_effect = [
            all_properties,  # Поиск по status
            type_properties,  # Поиск по type
        ]
        
        mock_db_manager._ensure_table = AsyncMock(return_value=properties_table)
        
        result = await frontmatter_api.aggregate_by_property("test_vault", "status", doc_type="task")
        
        assert result.property_key == "status"
        # После фильтрации по типу должно остаться только doc1
        assert result.total_documents == 1

    @pytest.mark.asyncio
    async def test_get_property_values(self, frontmatter_api, mock_db_manager):
        """Получение уникальных значений свойства."""
        properties_data = [
            {"document_id": "doc1", "property_key": "status", "property_value": "done"},
            {"document_id": "doc2", "property_key": "status", "property_value": "done"},
            {"document_id": "doc3", "property_key": "status", "property_value": "pending"},
        ]
        
        properties_table = MagicMock()
        properties_table.search.return_value.where.return_value.to_list.return_value = properties_data
        
        mock_db_manager._ensure_table = AsyncMock(return_value=properties_table)
        
        result = await frontmatter_api.get_property_values("test_vault", "status", limit=10)
        
        assert isinstance(result, list)
        assert len(result) == 2
        # Сортировка по убыванию количества
        assert result[0][0] == "done"
        assert result[0][1] == 2
        assert result[1][0] == "pending"
        assert result[1][1] == 1

    @pytest.mark.asyncio
    async def test_get_property_values_limit(self, frontmatter_api, mock_db_manager):
        """Получение уникальных значений с ограничением."""
        properties_data = [
            {"document_id": f"doc{i}", "property_key": "status", "property_value": f"status{i}"}
            for i in range(10)
        ]
        
        properties_table = MagicMock()
        properties_table.search.return_value.where.return_value.to_list.return_value = properties_data
        
        mock_db_manager._ensure_table = AsyncMock(return_value=properties_table)
        
        result = await frontmatter_api.get_property_values("test_vault", "status", limit=5)
        
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_get_frontmatter_sql_injection_protection(self, frontmatter_api, mock_db_manager):
        """Защита от SQL инъекций в file_path."""
        metadata_table = MagicMock()
        metadata_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = []
        mock_db_manager._ensure_table = AsyncMock(return_value=metadata_table)
        
        # Попытка SQL инъекции
        malicious_path = "file'; DROP TABLE documents; --"
        
        result = await frontmatter_api.get_frontmatter("test_vault", malicious_path)
        
        # Должен обработать корректно (экранирование)
        assert result is None
        # Проверяем, что экранирование было применено
        call_args = metadata_table.search.return_value.where.call_args[0][0]
        assert "''" in call_args or "'" not in call_args or malicious_path.replace("'", "''") in call_args

