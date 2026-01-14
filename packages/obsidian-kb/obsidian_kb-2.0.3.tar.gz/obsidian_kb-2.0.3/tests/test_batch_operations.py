"""Unit-тесты для BatchOperations (v6 Phase 5)."""

import csv
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.services.batch_operations import BatchOperations
from obsidian_kb.types import VaultNotFoundError


@pytest.fixture
def mock_service_container():
    """Мок ServiceContainer."""
    container = MagicMock()
    container.db_manager = MagicMock()
    container.frontmatter_api = MagicMock()
    return container


@pytest.fixture
def mock_db_manager():
    """Мок LanceDBManager."""
    manager = MagicMock()
    manager._ensure_table = AsyncMock(return_value=MagicMock())
    return manager


@pytest.fixture
def batch_operations(mock_service_container, mock_db_manager):
    """BatchOperations с моками."""
    mock_service_container.db_manager = mock_db_manager
    
    with patch("obsidian_kb.service_container.get_service_container", return_value=mock_service_container):
        ops = BatchOperations()
        # Принудительно устанавливаем мок db_manager
        ops._services = mock_service_container
        return ops


class TestBatchOperations:
    """Тесты для BatchOperations."""

    @pytest.mark.asyncio
    async def test_export_to_csv_empty_vault(self, batch_operations, mock_db_manager):
        """Экспорт пустого vault'а."""
        # Создаём моки для пустых таблиц
        documents_table = MagicMock()
        arrow_mock = MagicMock()
        arrow_mock.to_pylist.return_value = []  # Пустой список документов
        documents_table.to_arrow.return_value = arrow_mock
        
        properties_table = MagicMock()
        arrow_mock_props = MagicMock()
        arrow_mock_props.to_pylist.return_value = []  # Пустой список свойств
        properties_table.to_arrow.return_value = arrow_mock_props
        
        # Настраиваем мок для _ensure_table
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        csv_path = await batch_operations.export_to_csv("empty_vault")
        
        assert csv_path.endswith(".csv")
        assert Path(csv_path).exists()
        
        # Проверяем содержимое файла
        with open(csv_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Для пустого vault должен быть заголовок "No documents found" или пустой CSV
            assert "No documents found" in content or len(content.strip()) == 0
        
        # Удаляем временный файл
        if Path(csv_path).exists():
            Path(csv_path).unlink()

    @pytest.mark.asyncio
    async def test_export_to_csv_with_documents(self, batch_operations, mock_db_manager):
        """Экспорт vault'а с документами."""
        # Подготовка данных
        documents = [
            {
                "document_id": "doc1",
                "vault_name": "test_vault",
                "file_path": "file1.md",
                "title": "File 1",
                "chunk_count": 1,
                "content_type": "markdown",
                "created_at": "2024-01-01T00:00:00",
                "modified_at": "2024-01-01T00:00:00",
                "file_size": 100,
                "file_name": "file1",
                "file_extension": ".md",
                "file_path_full": "/tmp/test_vault/file1.md",
            },
            {
                "document_id": "doc2",
                "vault_name": "test_vault",
                "file_path": "file2.md",
                "title": "File 2",
                "chunk_count": 1,
                "content_type": "markdown",
                "created_at": "2024-01-01T00:00:00",
                "modified_at": "2024-01-01T00:00:00",
                "file_size": 100,
                "file_name": "file2",
                "file_extension": ".md",
                "file_path_full": "/tmp/test_vault/file2.md",
            },
        ]
        
        properties = [
            {"document_id": "doc1", "property_key": "type", "property_value": "person"},
            {"document_id": "doc1", "property_key": "role", "property_value": "CTO"},
            {"document_id": "doc2", "property_key": "type", "property_value": "person"},
        ]
        
        # Настраиваем моки правильно
        documents_table = MagicMock()
        arrow_mock_docs = MagicMock()
        arrow_mock_docs.to_pylist.return_value = documents
        documents_table.to_arrow.return_value = arrow_mock_docs
        
        properties_table = MagicMock()
        arrow_mock_props = MagicMock()
        arrow_mock_props.to_pylist.return_value = properties
        properties_table.to_arrow.return_value = arrow_mock_props
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        csv_path = await batch_operations.export_to_csv("test_vault")
        
        assert csv_path.endswith(".csv")
        assert Path(csv_path).exists()
        
        # Проверяем содержимое CSV
        with open(csv_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Проверяем, что CSV содержит заголовки и данные
            assert "title" in content.lower() or "document_id" in content.lower()
            # Если есть данные, проверяем их
            if "No documents found" not in content:
                reader = csv.DictReader(content.splitlines())
                rows = list(reader)
                assert len(rows) >= 2, f"Ожидалось минимум 2 строки, получено {len(rows)}"
        
        # Удаляем временный файл
        if Path(csv_path).exists():
            Path(csv_path).unlink()

    @pytest.mark.asyncio
    async def test_export_to_csv_with_doc_type_filter(self, batch_operations, mock_db_manager):
        """Экспорт с фильтром по типу документа."""
        documents = [
            {
                "document_id": "doc1",
                "vault_name": "test_vault",
                "file_path": "person1.md",
                "title": "Person 1",
            },
            {
                "document_id": "doc2",
                "vault_name": "test_vault",
                "file_path": "task1.md",
                "title": "Task 1",
            },
        ]
        
        properties = [
            {"document_id": "doc1", "property_key": "type", "property_value": "person"},
            {"document_id": "doc2", "property_key": "type", "property_value": "task"},
        ]
        
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = documents
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = properties
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        csv_path = await batch_operations.export_to_csv("test_vault", doc_type="person")
        
        assert csv_path.endswith(".csv")
        
        # Проверяем, что экспортирован только один документ
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["type"] == "person"
        
        Path(csv_path).unlink()

    @pytest.mark.asyncio
    async def test_export_to_csv_with_fields(self, batch_operations, mock_db_manager):
        """Экспорт с указанными полями."""
        documents = [
            {
                "document_id": "doc1",
                "vault_name": "test_vault",
                "file_path": "file1.md",
                "title": "File 1",
            },
        ]
        
        properties = [
            {"document_id": "doc1", "property_key": "type", "property_value": "person"},
            {"document_id": "doc1", "property_key": "role", "property_value": "CTO"},
        ]
        
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = documents
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = properties
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        csv_path = await batch_operations.export_to_csv("test_vault", fields="title,type,role")
        
        # Проверяем, что экспортированы только указанные поля
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert set(rows[0].keys()) == {"title", "type", "role"}
        
        Path(csv_path).unlink()

    @pytest.mark.asyncio
    async def test_export_to_csv_custom_path(self, batch_operations, mock_db_manager):
        """Экспорт в указанный путь."""
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = []
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = []
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            custom_path = tmp.name
        
        try:
            csv_path = await batch_operations.export_to_csv("test_vault", output_path=custom_path)
            
            assert csv_path == custom_path
            assert Path(csv_path).exists()
        finally:
            if Path(custom_path).exists():
                Path(custom_path).unlink()

    @pytest.mark.asyncio
    async def test_export_to_csv_vault_not_found(self, batch_operations, mock_db_manager):
        """Экспорт из несуществующего vault'а."""
        mock_db_manager._ensure_table = AsyncMock(side_effect=VaultNotFoundError("Vault not found"))
        
        with pytest.raises(VaultNotFoundError):
            await batch_operations.export_to_csv("nonexistent_vault")

    @pytest.mark.asyncio
    async def test_compare_schemas_single_vault(self, batch_operations, mock_service_container):
        """Сравнение схем одного vault'а."""
        from obsidian_kb.types import FieldInfo, FrontmatterSchema
        
        schema = FrontmatterSchema(
            vault_name="vault1",
            total_documents=10,
            doc_type_filter=None,
            fields={
                "type": FieldInfo(
                    field_name="type",
                    field_type="string",
                    unique_values=["person", "task"],
                    unique_count=2,
                    document_count=10,
                    nullable_count=0,
                    example_documents=["doc1", "doc2"],
                ),
                "role": FieldInfo(
                    field_name="role",
                    field_type="string",
                    unique_values=["CTO", "Manager"],
                    unique_count=2,
                    document_count=5,
                    nullable_count=5,
                    example_documents=["doc1"],
                ),
            },
            common_patterns=[],
        )
        
        mock_service_container.frontmatter_api.get_schema = AsyncMock(return_value=schema)
        
        result = await batch_operations.compare_schemas(["vault1"])
        
        assert "common_fields" in result
        assert "unique_fields" in result
        assert "vault_stats" in result
        assert result["vault_stats"]["vault1"] == 10
        assert len(result["common_fields"]) == 2  # type и role

    @pytest.mark.asyncio
    async def test_compare_schemas_multiple_vaults(self, batch_operations, mock_service_container):
        """Сравнение схем нескольких vault'ов."""
        from obsidian_kb.types import FieldInfo, FrontmatterSchema
        
        schema1 = FrontmatterSchema(
            vault_name="vault1",
            total_documents=10,
            doc_type_filter=None,
            fields={
                "type": FieldInfo(
                    field_name="type",
                    field_type="string",
                    unique_values=["person"],
                    unique_count=1,
                    document_count=10,
                    nullable_count=0,
                    example_documents=["doc1"],
                ),
                "role": FieldInfo(
                    field_name="role",
                    field_type="string",
                    unique_values=["CTO"],
                    unique_count=1,
                    document_count=5,
                    nullable_count=5,
                    example_documents=["doc1"],
                ),
            },
            common_patterns=[],
        )
        
        schema2 = FrontmatterSchema(
            vault_name="vault2",
            total_documents=5,
            doc_type_filter=None,
            fields={
                "type": FieldInfo(
                    field_name="type",
                    field_type="string",
                    unique_values=["task"],
                    unique_count=1,
                    document_count=5,
                    nullable_count=0,
                    example_documents=["doc2"],
                ),
                "status": FieldInfo(
                    field_name="status",
                    field_type="string",
                    unique_values=["done"],
                    unique_count=1,
                    document_count=3,
                    nullable_count=2,
                    example_documents=["doc2"],
                ),
            },
            common_patterns=[],
        )
        
        mock_service_container.frontmatter_api.get_schema = AsyncMock(
            side_effect=[schema1, schema2]
        )
        
        result = await batch_operations.compare_schemas(["vault1", "vault2"])
        
        assert "common_fields" in result
        assert "unique_fields" in result
        assert "vault_stats" in result
        
        # type - общее поле
        assert "type" in result["common_fields"]
        
        # role - уникальное для vault1
        assert "role" in result["unique_fields"]["vault1"]
        
        # status - уникальное для vault2
        assert "status" in result["unique_fields"]["vault2"]
        
        assert result["vault_stats"]["vault1"] == 10
        assert result["vault_stats"]["vault2"] == 5

    @pytest.mark.asyncio
    async def test_compare_schemas_no_common_fields(self, batch_operations, mock_service_container):
        """Сравнение vault'ов без общих полей."""
        from obsidian_kb.types import FieldInfo, FrontmatterSchema
        
        schema1 = FrontmatterSchema(
            vault_name="vault1",
            total_documents=10,
            doc_type_filter=None,
            fields={
                "field1": FieldInfo(
                    field_name="field1",
                    field_type="string",
                    unique_values=["value1"],
                    unique_count=1,
                    document_count=10,
                    nullable_count=0,
                    example_documents=["doc1"],
                ),
            },
            common_patterns=[],
        )
        
        schema2 = FrontmatterSchema(
            vault_name="vault2",
            total_documents=5,
            doc_type_filter=None,
            fields={
                "field2": FieldInfo(
                    field_name="field2",
                    field_type="string",
                    unique_values=["value2"],
                    unique_count=1,
                    document_count=5,
                    nullable_count=0,
                    example_documents=["doc2"],
                ),
            },
            common_patterns=[],
        )
        
        mock_service_container.frontmatter_api.get_schema = AsyncMock(
            side_effect=[schema1, schema2]
        )
        
        result = await batch_operations.compare_schemas(["vault1", "vault2"])
        
        assert len(result["common_fields"]) == 0
        assert "field1" in result["unique_fields"]["vault1"]
        assert "field2" in result["unique_fields"]["vault2"]

    @pytest.mark.asyncio
    async def test_compare_schemas_vault_not_found(self, batch_operations, mock_service_container):
        """Сравнение с несуществующим vault'ом."""
        mock_service_container.frontmatter_api.get_schema = AsyncMock(
            side_effect=VaultNotFoundError("Vault not found")
        )
        
        with pytest.raises(VaultNotFoundError):
            await batch_operations.compare_schemas(["nonexistent_vault"])

