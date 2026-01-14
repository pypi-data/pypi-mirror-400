"""Unit-тесты для GraphQueryService (v6 Phase 4)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.interfaces import ConnectedDocument, GraphQueryResult
from obsidian_kb.services.graph_query_service import GraphQueryService
from obsidian_kb.types import VaultNotFoundError


@pytest.fixture
def mock_service_container():
    """Мок ServiceContainer."""
    container = MagicMock()
    container.db_manager = MagicMock()
    return container


@pytest.fixture
def mock_db_manager():
    """Мок LanceDBManager."""
    manager = MagicMock()
    manager._ensure_table = AsyncMock(return_value=MagicMock())
    return manager


@pytest.fixture
def graph_query_service(mock_service_container, mock_db_manager):
    """GraphQueryService с моками."""
    mock_service_container.db_manager = mock_db_manager
    
    with patch("obsidian_kb.services.graph_query_service.get_service_container", return_value=mock_service_container):
        service = GraphQueryService()
        return service


class TestGraphQueryService:
    """Тесты для GraphQueryService."""

    @pytest.mark.asyncio
    async def test_find_connected_outgoing(self, graph_query_service, mock_db_manager):
        """Поиск исходящих связей."""
        # Настраиваем моки
        chunks_table = MagicMock()
        chunks_data = [
            {
                "document_id": "doc1",
                "links": ["doc2", "doc3"]
            },
            {
                "document_id": "doc2",
                "links": []
            },
            {
                "document_id": "doc3",
                "links": []
            }
        ]
        chunks_table.to_arrow.return_value.to_pylist.return_value = chunks_data
        
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1"
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2"
            },
            {
                "document_id": "doc3",
                "file_path": "doc3.md",
                "title": "Document 3"
            }
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data
        
        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "chunks":
                return chunks_table
            elif table_name == "documents":
                return documents_table
            return MagicMock()
        
        mock_db_manager._ensure_table = ensure_table
        
        result = await graph_query_service.find_connected(
            vault_name="test_vault",
            document_path="doc1.md",
            direction="outgoing",
            depth=1,
            limit=50
        )
        
        assert isinstance(result, GraphQueryResult)
        assert result.center_document == "doc1.md"
        assert result.total_outgoing == 2
        assert len(result.connected) == 2
        assert all(doc.direction == "outgoing" for doc in result.connected)

    @pytest.mark.asyncio
    async def test_find_connected_incoming(self, graph_query_service, mock_db_manager):
        """Поиск входящих связей."""
        chunks_table = MagicMock()
        chunks_data = [
            {
                "document_id": "doc1",
                "links": []
            },
            {
                "document_id": "doc2",
                "links": ["doc1"]
            },
            {
                "document_id": "doc3",
                "links": ["doc1"]
            }
        ]
        chunks_table.to_arrow.return_value.to_pylist.return_value = chunks_data
        
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1"
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2"
            },
            {
                "document_id": "doc3",
                "file_path": "doc3.md",
                "title": "Document 3"
            }
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data
        
        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "chunks":
                return chunks_table
            elif table_name == "documents":
                return documents_table
            return MagicMock()
        
        mock_db_manager._ensure_table = ensure_table
        
        result = await graph_query_service.find_connected(
            vault_name="test_vault",
            document_path="doc1.md",
            direction="incoming",
            depth=1,
            limit=50
        )
        
        assert isinstance(result, GraphQueryResult)
        assert result.center_document == "doc1.md"
        assert result.total_incoming == 2
        assert len(result.connected) == 2
        assert all(doc.direction == "incoming" for doc in result.connected)

    @pytest.mark.asyncio
    async def test_find_orphans(self, graph_query_service, mock_db_manager):
        """Поиск orphan документов."""
        chunks_table = MagicMock()
        chunks_data = [
            {
                "document_id": "doc1",
                "links": ["doc2"]
            },
            {
                "document_id": "doc2",
                "links": []
            }
        ]
        chunks_table.to_arrow.return_value.to_pylist.return_value = chunks_data
        
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1"
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2"
            },
            {
                "document_id": "doc3",
                "file_path": "doc3.md",
                "title": "Document 3"
            }
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = []
        
        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "chunks":
                return chunks_table
            elif table_name == "documents":
                return documents_table
            elif table_name == "document_properties":
                return properties_table
            return MagicMock()
        
        mock_db_manager._ensure_table = ensure_table
        
        orphans = await graph_query_service.find_orphans(
            vault_name="test_vault",
            doc_type=None
        )
        
        assert isinstance(orphans, list)
        # doc3 не имеет входящих ссылок
        assert "doc3.md" in orphans

    @pytest.mark.asyncio
    async def test_find_broken_links(self, graph_query_service, mock_db_manager):
        """Поиск битых ссылок."""
        chunks_table = MagicMock()
        chunks_data = [
            {
                "document_id": "doc1",
                "links": ["doc2", "nonexistent"]
            }
        ]
        chunks_table.to_arrow.return_value.to_pylist.return_value = chunks_data
        
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1"
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2"
            }
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data
        
        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "chunks":
                return chunks_table
            elif table_name == "documents":
                return documents_table
            return MagicMock()
        
        mock_db_manager._ensure_table = ensure_table
        
        broken_links = await graph_query_service.find_broken_links(
            vault_name="test_vault"
        )
        
        assert isinstance(broken_links, list)
        assert len(broken_links) == 1
        assert broken_links[0][0] == "doc1.md"
        assert broken_links[0][1] == "nonexistent"

    @pytest.mark.asyncio
    async def test_get_backlinks(self, graph_query_service, mock_db_manager):
        """Получение backlinks."""
        # Используем find_connected с direction="incoming"
        chunks_table = MagicMock()
        chunks_data = [
            {
                "document_id": "doc1",
                "links": []
            },
            {
                "document_id": "doc2",
                "links": ["doc1"]
            }
        ]
        chunks_table.to_arrow.return_value.to_pylist.return_value = chunks_data
        
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1"
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2"
            }
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data
        
        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "chunks":
                return chunks_table
            elif table_name == "documents":
                return documents_table
            return MagicMock()
        
        mock_db_manager._ensure_table = ensure_table
        
        backlinks = await graph_query_service.get_backlinks(
            vault_name="test_vault",
            document_path="doc1.md"
        )
        
        assert isinstance(backlinks, list)
        assert len(backlinks) == 1
        assert backlinks[0].direction == "incoming"
        assert backlinks[0].file_path == "doc2.md"

    @pytest.mark.asyncio
    async def test_find_connected_vault_not_found(self, graph_query_service, mock_db_manager):
        """Поиск связей в несуществующем vault'е."""
        mock_db_manager._ensure_table = AsyncMock(side_effect=VaultNotFoundError("Vault not found"))
        
        with pytest.raises(VaultNotFoundError):
            await graph_query_service.find_connected(
                vault_name="nonexistent_vault",
                document_path="doc.md"
            )

    @pytest.mark.asyncio
    async def test_find_connected_document_not_found(self, graph_query_service, mock_db_manager):
        """Поиск связей для несуществующего документа."""
        chunks_table = MagicMock()
        chunks_table.to_arrow.return_value.to_pylist.return_value = []
        
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = []
        
        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "chunks":
                return chunks_table
            elif table_name == "documents":
                return documents_table
            return MagicMock()
        
        mock_db_manager._ensure_table = ensure_table
        
        result = await graph_query_service.find_connected(
            vault_name="test_vault",
            document_path="nonexistent.md",
            direction="both"
        )
        
        assert result.total_incoming == 0
        assert result.total_outgoing == 0
        assert len(result.connected) == 0

