"""Unit-тесты для DocumentRepository."""

from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from obsidian_kb.storage.document_repository import DocumentRepository
from obsidian_kb.types import Document, DocumentInfo, DocumentChunk


@pytest.fixture
def mock_db_manager():
    """Мок LanceDBManager."""
    manager = MagicMock()
    manager.get_document_info = AsyncMock(return_value=None)
    manager.get_documents_by_property = AsyncMock(return_value=set())
    manager.get_documents_by_tags = AsyncMock(return_value=set())
    manager.get_document_properties = AsyncMock(return_value={})
    manager._ensure_table = AsyncMock(return_value=MagicMock())
    manager._get_db = MagicMock(return_value=MagicMock())
    manager.get_chunks_by_document = AsyncMock(return_value=[])
    return manager


@pytest.fixture
def document_repository(mock_db_manager):
    """DocumentRepository с моком db_manager."""
    return DocumentRepository(mock_db_manager)


def create_doc_info(
    document_id: str,
    vault_name: str,
    file_path: str,
    title: str,
    chunk_count: int = 1,
) -> DocumentInfo:
    """Фабрика для создания DocumentInfo с правильными полями."""
    return DocumentInfo(
        document_id=document_id,
        vault_name=vault_name,
        file_path=file_path,
        file_path_full=f"/test/{vault_name}/{file_path}",
        file_name=Path(file_path).name,
        file_extension=Path(file_path).suffix,
        content_type="markdown",
        title=title,
        created_at=datetime(2024, 1, 1),
        modified_at=datetime(2024, 1, 2),
        file_size=1000,
        chunk_count=chunk_count,
    )


class TestDocumentRepository:
    """Тесты для DocumentRepository."""

    @pytest.mark.asyncio
    async def test_get_not_found(self, document_repository, mock_db_manager):
        """Получение несуществующего документа."""
        mock_db_manager.get_document_info = AsyncMock(return_value=None)

        result = await document_repository.get("test", "test::file.md")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_found(self, document_repository, mock_db_manager):
        """Получение существующего документа."""
        doc_info = create_doc_info(
            document_id="test::file.md",
            vault_name="test",
            file_path="file.md",
            title="Test File",
            chunk_count=3,
        )
        mock_db_manager.get_document_info = AsyncMock(return_value=doc_info)
        mock_db_manager.get_document_properties = AsyncMock(return_value={"type": "guide"})

        result = await document_repository.get("test", "test::file.md")

        assert result is not None
        assert isinstance(result, Document)
        assert result.document_id == "test::file.md"
        assert result.title == "Test File"

    @pytest.mark.asyncio
    async def test_get_many(self, document_repository, mock_db_manager):
        """Получение нескольких документов."""
        doc_info1 = create_doc_info(
            document_id="test::file1.md",
            vault_name="test",
            file_path="file1.md",
            title="File 1",
        )
        doc_info2 = create_doc_info(
            document_id="test::file2.md",
            vault_name="test",
            file_path="file2.md",
            title="File 2",
        )

        async def get_doc_info_side_effect(vault_name: str, document_id: str):
            if document_id == "test::file1.md":
                return doc_info1
            elif document_id == "test::file2.md":
                return doc_info2
            return None

        mock_db_manager.get_document_info = AsyncMock(side_effect=get_doc_info_side_effect)
        mock_db_manager.get_document_properties = AsyncMock(return_value={})

        results = await document_repository.get_many("test", {"test::file1.md", "test::file2.md"})

        assert len(results) == 2
        assert all(isinstance(doc, Document) for doc in results)
        assert {doc.document_id for doc in results} == {"test::file1.md", "test::file2.md"}

    @pytest.mark.asyncio
    async def test_get_many_with_errors(self, document_repository, mock_db_manager):
        """Получение нескольких документов с ошибками."""
        doc_info = create_doc_info(
            document_id="test::file1.md",
            vault_name="test",
            file_path="file1.md",
            title="File 1",
        )

        async def get_doc_info_side_effect(vault_name: str, document_id: str):
            if document_id == "test::file1.md":
                return doc_info
            elif document_id == "test::file2.md":
                raise Exception("Error")
            return None

        mock_db_manager.get_document_info = AsyncMock(side_effect=get_doc_info_side_effect)
        mock_db_manager.get_document_properties = AsyncMock(return_value={})

        results = await document_repository.get_many("test", {"test::file1.md", "test::file2.md"})

        assert len(results) == 1
        assert results[0].document_id == "test::file1.md"

    @pytest.mark.asyncio
    async def test_find_by_property(self, document_repository, mock_db_manager):
        """Поиск по свойству."""
        mock_db_manager.get_documents_by_property = AsyncMock(return_value={"test::file1.md", "test::file2.md"})

        result = await document_repository.find_by_property("test", "type", "guide")

        assert result == {"test::file1.md", "test::file2.md"}
        mock_db_manager.get_documents_by_property.assert_called_once_with(
            vault_name="test",
            property_key="type",
            property_value="guide",
        )

    @pytest.mark.asyncio
    async def test_find_by_tags_match_all(self, document_repository, mock_db_manager):
        """Поиск по тегам (match_all=True)."""
        mock_db_manager.get_documents_by_tags = AsyncMock(return_value={"test::file1.md"})

        result = await document_repository.find_by_tags("test", ["python", "async"], match_all=True)

        assert result == {"test::file1.md"}
        mock_db_manager.get_documents_by_tags.assert_called_once_with(
            vault_name="test",
            tags=["python", "async"],
            match_all=True,
        )

    @pytest.mark.asyncio
    async def test_find_by_tags_match_any(self, document_repository, mock_db_manager):
        """Поиск по тегам (match_all=False)."""
        mock_db_manager.get_documents_by_tags = AsyncMock(return_value={"test::file1.md", "test::file2.md"})

        result = await document_repository.find_by_tags("test", ["python", "async"], match_all=False)

        assert len(result) == 2
        mock_db_manager.get_documents_by_tags.assert_called_once_with(
            vault_name="test",
            tags=["python", "async"],
            match_all=False,
        )

    @pytest.mark.asyncio
    async def test_find_by_date_range(self, document_repository, mock_db_manager):
        """Поиск по диапазону дат."""
        import pyarrow as pa

        # Мокаем таблицу documents через to_arrow (как в реальной реализации)
        mock_table = MagicMock()
        mock_arrow_table = pa.table({
            "document_id": ["test::file1.md", "test::file2.md"],
        })
        mock_table.search.return_value.where.return_value.to_arrow.return_value = mock_arrow_table

        mock_db_manager._ensure_table = AsyncMock(return_value=mock_table)
        mock_db_manager._get_db = MagicMock()

        after = datetime(2024, 1, 1)
        before = datetime(2024, 12, 31)

        result = await document_repository.find_by_date_range("test", "created_at", after=after, before=before)

        assert len(result) == 2
        assert "test::file1.md" in result
        assert "test::file2.md" in result

    @pytest.mark.asyncio
    async def test_get_content_from_file(self, document_repository, mock_db_manager, tmp_path):
        """Получение контента из файла."""
        # Создаём временный файл
        test_file = tmp_path / "file.md"
        test_file.write_text("# Test File\n\nContent here", encoding="utf-8")

        doc_info = create_doc_info(
            document_id="test::file.md",
            vault_name="test",
            file_path=str(test_file),
            title="Test File",
        )
        # Перезаписываем file_path_full на реальный путь
        doc_info = DocumentInfo(
            document_id=doc_info.document_id,
            vault_name=doc_info.vault_name,
            file_path=str(test_file),
            file_path_full=str(test_file),
            file_name=doc_info.file_name,
            file_extension=doc_info.file_extension,
            content_type=doc_info.content_type,
            title=doc_info.title,
            created_at=doc_info.created_at,
            modified_at=doc_info.modified_at,
            file_size=doc_info.file_size,
            chunk_count=doc_info.chunk_count,
        )
        mock_db_manager.get_document_info = AsyncMock(return_value=doc_info)

        content = await document_repository.get_content("test", "test::file.md")
        assert "# Test File\n\nContent here" in content

    @pytest.mark.asyncio
    async def test_get_content_from_chunks(self, document_repository, mock_db_manager):
        """Получение контента из чанков когда файл не существует."""
        import pyarrow as pa

        # Создаём doc_info с несуществующим файлом (file_path_full)
        doc_info = DocumentInfo(
            document_id="test::file.md",
            vault_name="test",
            file_path="file.md",
            file_path_full="/nonexistent/path/file.md",  # Несуществующий путь
            file_name="file.md",
            file_extension=".md",
            content_type="markdown",
            title="Test File",
            created_at=datetime(2024, 1, 1),
            modified_at=datetime(2024, 1, 2),
            file_size=1000,
            chunk_count=2,
        )
        mock_db_manager.get_document_info = AsyncMock(return_value=doc_info)

        # Мокаем таблицу chunks через to_arrow (как в реальной реализации)
        mock_chunks_table = MagicMock()
        mock_arrow_table = pa.table({
            "chunk_id": ["test::file.md::0", "test::file.md::1"],
            "document_id": ["test::file.md", "test::file.md"],
            "content": ["First chunk", "Second chunk"],
            "chunk_index": [0, 1],
        })
        mock_chunks_table.search.return_value.where.return_value.to_arrow.return_value = mock_arrow_table

        mock_db_manager._ensure_table = AsyncMock(return_value=mock_chunks_table)
        mock_db_manager._get_db = MagicMock()

        content = await document_repository.get_content("test", "test::file.md")
        assert "First chunk" in content
        assert "Second chunk" in content

    @pytest.mark.asyncio
    async def test_get_properties(self, document_repository, mock_db_manager):
        """Получение свойств документа."""
        mock_db_manager.get_document_properties = AsyncMock(return_value={"type": "guide", "status": "published"})

        properties = await document_repository.get_properties("test", "test::file.md")

        assert properties == {"type": "guide", "status": "published"}
        mock_db_manager.get_document_properties.assert_called_once_with("test", "test::file.md")
