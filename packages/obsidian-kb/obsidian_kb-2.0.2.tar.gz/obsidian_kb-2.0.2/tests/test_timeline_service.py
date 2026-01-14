"""Unit-тесты для TimelineService (v6 Phase 4)."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.services.timeline_service import TimelineService
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
def timeline_service(mock_service_container, mock_db_manager):
    """TimelineService с моками."""
    mock_service_container.db_manager = mock_db_manager
    
    with patch("obsidian_kb.services.timeline_service.get_service_container", return_value=mock_service_container):
        service = TimelineService()
        return service


class TestTimelineService:
    """Тесты для TimelineService."""

    @pytest.mark.asyncio
    async def test_timeline_basic(self, timeline_service, mock_db_manager):
        """Базовый тест timeline."""
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1",
                "created_at": datetime.now() - timedelta(days=5),
                "modified_at": datetime.now() - timedelta(days=2)
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2",
                "created_at": datetime.now() - timedelta(days=10),
                "modified_at": datetime.now() - timedelta(days=1)
            }
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = []
        
        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "documents":
                return documents_table
            elif table_name == "document_properties":
                return properties_table
            return MagicMock()
        
        mock_db_manager._ensure_table = ensure_table
        
        results = await timeline_service.timeline(
            vault_name="test_vault",
            doc_type=None,
            date_field="created",
            after=None,
            before=None,
            limit=50
        )
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert all("file_path" in doc for doc in results)
        assert all("title" in doc for doc in results)

    @pytest.mark.asyncio
    async def test_timeline_with_date_filter(self, timeline_service, mock_db_manager):
        """Timeline с фильтром по дате."""
        now = datetime.now()
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1",
                "created_at": now - timedelta(days=5),
                "modified_at": now - timedelta(days=2)
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2",
                "created_at": now - timedelta(days=15),
                "modified_at": now - timedelta(days=10)
            }
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = []
        
        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "documents":
                return documents_table
            elif table_name == "document_properties":
                return properties_table
            return MagicMock()
        
        mock_db_manager._ensure_table = ensure_table
        
        # Фильтр: документы созданные за последние 7 дней
        after_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        results = await timeline_service.timeline(
            vault_name="test_vault",
            doc_type=None,
            date_field="created",
            after=after_date,
            before=None,
            limit=50
        )
        
        assert isinstance(results, list)
        # Должен остаться только doc1 (создан 5 дней назад)
        assert len(results) == 1
        assert results[0]["file_path"] == "doc1.md"

    @pytest.mark.asyncio
    async def test_timeline_with_relative_date(self, timeline_service, mock_db_manager):
        """Timeline с относительной датой."""
        now = datetime.now()
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1",
                "created_at": now - timedelta(days=5),
                "modified_at": now - timedelta(days=2)
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2",
                "created_at": now - timedelta(days=15),
                "modified_at": now - timedelta(days=10)
            }
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = []
        
        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "documents":
                return documents_table
            elif table_name == "document_properties":
                return properties_table
            return MagicMock()
        
        mock_db_manager._ensure_table = ensure_table
        
        # Используем относительную дату "last_week"
        results = await timeline_service.timeline(
            vault_name="test_vault",
            doc_type=None,
            date_field="created",
            after="last_week",
            before=None,
            limit=50
        )
        
        assert isinstance(results, list)
        # Должен остаться только doc1 (создан 5 дней назад, что меньше недели)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_recent_changes(self, timeline_service, mock_db_manager):
        """Тест recent_changes.

        Note: Код ожидает даты как timestamp (int/float) или строки,
        не как datetime объекты напрямую.
        """
        now = datetime.now()
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1",
                "created_at": (now - timedelta(days=3)).timestamp(),
                "modified_at": (now - timedelta(days=3)).timestamp(),
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2",
                "created_at": (now - timedelta(days=10)).timestamp(),
                "modified_at": (now - timedelta(days=2)).timestamp(),
            },
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data

        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = []

        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "documents":
                return documents_table
            elif table_name == "document_properties":
                return properties_table
            return MagicMock()

        mock_db_manager._ensure_table = ensure_table

        result = await timeline_service.recent_changes(
            vault_name="test_vault", days=7, doc_type=None
        )

        assert isinstance(result, dict)
        assert "created" in result
        assert "modified" in result
        assert "total" in result
        assert result["total"] == len(result["created"]) + len(result["modified"])
        # doc1 создан 3 дня назад (входит в период)
        assert len(result["created"]) >= 1
        # doc2 изменён 2 дня назад (входит в период, но не создан)
        assert len(result["modified"]) >= 1

    @pytest.mark.asyncio
    async def test_recent_changes_with_doc_type(self, timeline_service, mock_db_manager):
        """Recent changes с фильтром по типу.

        Note: Код ожидает даты как timestamp (int/float) или строки.
        """
        now = datetime.now()
        documents_table = MagicMock()
        docs_data = [
            {
                "document_id": "doc1",
                "file_path": "doc1.md",
                "title": "Document 1",
                "created_at": (now - timedelta(days=3)).timestamp(),
                "modified_at": (now - timedelta(days=3)).timestamp(),
            },
            {
                "document_id": "doc2",
                "file_path": "doc2.md",
                "title": "Document 2",
                "created_at": (now - timedelta(days=10)).timestamp(),
                "modified_at": (now - timedelta(days=2)).timestamp(),
            },
        ]
        documents_table.to_arrow.return_value.to_pylist.return_value = docs_data

        properties_table = MagicMock()
        props_data = [
            {"document_id": "doc1", "property_key": "type", "property_value": "note"},
            {"document_id": "doc2", "property_key": "type", "property_value": "task"},
        ]
        properties_table.to_arrow.return_value.to_pylist.return_value = props_data

        async def ensure_table(vault_name: str, table_name: str):
            if table_name == "documents":
                return documents_table
            elif table_name == "document_properties":
                return properties_table
            return MagicMock()

        mock_db_manager._ensure_table = ensure_table

        result = await timeline_service.recent_changes(
            vault_name="test_vault", days=7, doc_type="note"
        )

        assert isinstance(result, dict)
        # Должен остаться только doc1 (type=note)
        assert len(result["created"]) == 1
        assert result["created"][0]["file_path"] == "doc1.md"

    @pytest.mark.asyncio
    async def test_timeline_vault_not_found(self, timeline_service, mock_db_manager):
        """Timeline для несуществующего vault'а."""
        mock_db_manager._ensure_table = AsyncMock(side_effect=VaultNotFoundError("Vault not found"))
        
        with pytest.raises(VaultNotFoundError):
            await timeline_service.timeline(
                vault_name="nonexistent_vault",
                doc_type=None
            )

    @pytest.mark.asyncio
    async def test_parse_date_relative(self, timeline_service):
        """Парсинг относительных дат."""
        # Тестируем приватный метод через публичный API
        now = datetime.now()
        
        # last_week
        last_week = timeline_service._parse_date("last_week")
        assert last_week is not None
        assert (now - last_week).days <= 7
        
        # last_month
        last_month = timeline_service._parse_date("last_month")
        assert last_month is not None
        assert (now - last_month).days <= 30
        
        # ISO формат
        iso_date = timeline_service._parse_date("2024-12-01")
        assert iso_date is not None
        assert iso_date.year == 2024
        assert iso_date.month == 12
        assert iso_date.day == 1

