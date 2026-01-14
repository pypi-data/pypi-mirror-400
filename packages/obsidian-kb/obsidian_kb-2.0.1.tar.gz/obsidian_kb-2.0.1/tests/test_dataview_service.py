"""Unit-тесты для DataviewService (v6 Phase 2)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.interfaces import DataviewQuery, DataviewResult
from obsidian_kb.query.where_parser import WhereCondition
from obsidian_kb.services.dataview_service import DataviewService


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
def dataview_service(mock_service_container, mock_db_manager):
    """DataviewService с моками."""
    mock_service_container.db_manager = mock_db_manager
    
    with patch(
        "obsidian_kb.services.dataview_service.get_service_container",
        return_value=mock_service_container,
    ):
        service = DataviewService()
        return service


@pytest.fixture
def sample_documents():
    """Примерные документы для тестов."""
    return [
        {
            "document_id": "doc1",
            "file_path": "doc1.md",
            "title": "Document 1",
            "type": "task",
            "status": "done",
            "priority": 5,
            "created_at": datetime(2024, 1, 1),
        },
        {
            "document_id": "doc2",
            "file_path": "doc2.md",
            "title": "Document 2",
            "type": "task",
            "status": "pending",
            "priority": 3,
            "created_at": datetime(2024, 1, 2),
        },
        {
            "document_id": "doc3",
            "file_path": "person.md",
            "title": "Person",
            "type": "person",
            "role": "manager",
            "created_at": datetime(2024, 1, 3),
        },
    ]


@pytest.fixture
def sample_properties():
    """Примерные свойства для тестов."""
    return [
        {"document_id": "doc1", "property_key": "type", "property_value": "task"},
        {"document_id": "doc1", "property_key": "status", "property_value": "done"},
        {"document_id": "doc1", "property_key": "priority", "property_value": "5"},
        {"document_id": "doc2", "property_key": "type", "property_value": "task"},
        {"document_id": "doc2", "property_key": "status", "property_value": "pending"},
        {"document_id": "doc2", "property_key": "priority", "property_value": "3"},
        {"document_id": "doc3", "property_key": "type", "property_value": "person"},
        {"document_id": "doc3", "property_key": "role", "property_value": "manager"},
    ]


class TestDataviewService:
    """Тесты для DataviewService."""

    @pytest.mark.asyncio
    async def test_query_all_documents(
        self, dataview_service, mock_db_manager, sample_documents, sample_properties
    ):
        """Запрос всех документов."""
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = sample_documents
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = sample_properties
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        query = DataviewQuery(select=["*"], limit=10)
        result = await dataview_service.query("test_vault", query)
        
        assert isinstance(result, DataviewResult)
        assert result.total_count == 3
        assert len(result.documents) == 3
        assert result.query_time_ms >= 0

    @pytest.mark.asyncio
    async def test_query_select_fields(
        self, dataview_service, mock_db_manager, sample_documents, sample_properties
    ):
        """Запрос с выбором конкретных полей."""
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = sample_documents
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = sample_properties
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        query = DataviewQuery(select=["title", "status"], limit=10)
        result = await dataview_service.query("test_vault", query)
        
        assert result.total_count == 3
        assert all("title" in doc for doc in result.documents)
        assert all("status" in doc or doc.get("status") is None for doc in result.documents)

    @pytest.mark.asyncio
    async def test_query_from_type(
        self, dataview_service, mock_db_manager, sample_documents, sample_properties
    ):
        """Запрос с фильтром по типу."""
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = sample_documents
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = sample_properties
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        query = DataviewQuery(select=["*"], from_type="task", limit=10)
        result = await dataview_service.query("test_vault", query)
        
        assert result.total_count == 2
        assert all(doc.get("type") == "task" for doc in result.documents)

    @pytest.mark.asyncio
    async def test_query_from_path(
        self, dataview_service, mock_db_manager, sample_documents, sample_properties
    ):
        """Запрос с фильтром по пути."""
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = sample_documents
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = sample_properties
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        query = DataviewQuery(select=["*"], from_path="doc", limit=10)
        result = await dataview_service.query("test_vault", query)
        
        assert result.total_count == 2
        assert all(doc.get("file_path", "").startswith("doc") for doc in result.documents)

    @pytest.mark.asyncio
    async def test_query_where_condition(
        self, dataview_service, mock_db_manager, sample_documents, sample_properties
    ):
        """Запрос с WHERE условием."""
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = sample_documents
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = sample_properties
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        query = DataviewQuery(
            select=["*"],
            where=[WhereCondition("status", "=", "done", "AND")],
            limit=10,
        )
        result = await dataview_service.query("test_vault", query)
        
        assert result.total_count == 1
        assert result.documents[0].get("status") == "done"

    @pytest.mark.asyncio
    async def test_query_sort_by(
        self, dataview_service, mock_db_manager, sample_documents, sample_properties
    ):
        """Запрос с сортировкой."""
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = sample_documents

        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = sample_properties

        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])

        query = DataviewQuery(select=["*"], sort_by="priority", sort_order="desc", limit=10)
        result = await dataview_service.query("test_vault", query)

        assert result.total_count == 3
        # Проверяем, что сортировка применена
        # Примечание: priority может быть int или str после merge с properties
        priorities = []
        for doc in result.documents:
            p = doc.get("priority")
            if p is not None:
                priorities.append(int(p) if isinstance(p, (int, str)) and str(p).isdigit() else 0)
            else:
                priorities.append(0)
        assert priorities == sorted(priorities, reverse=True)

    @pytest.mark.asyncio
    async def test_query_limit(
        self, dataview_service, mock_db_manager, sample_documents, sample_properties
    ):
        """Запрос с лимитом."""
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = sample_documents
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = sample_properties
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        query = DataviewQuery(select=["*"], limit=2)
        result = await dataview_service.query("test_vault", query)
        
        assert len(result.documents) == 2
        assert result.total_count == 2

    @pytest.mark.asyncio
    async def test_query_string_parsing(self, dataview_service):
        """Парсинг SQL-like строки."""
        query = dataview_service.parse_query(
            "SELECT title, status FROM type:task WHERE status != done SORT BY priority DESC LIMIT 10"
        )
        
        assert query.select == ["title", "status"]
        assert query.from_type == "task"
        assert query.where is not None
        assert len(query.where) == 1
        assert query.where[0].field == "status"
        assert query.where[0].operator == "!="
        assert query.where[0].value == "done"
        assert query.sort_by == "priority"
        assert query.sort_order == "desc"
        assert query.limit == 10

    @pytest.mark.asyncio
    async def test_query_string_minimal(self, dataview_service):
        """Минимальный запрос."""
        query = dataview_service.parse_query("SELECT *")
        
        assert query.select == ["*"]
        assert query.from_type is None
        assert query.where is None
        assert query.sort_by is None
        assert query.limit == 50  # default

    @pytest.mark.asyncio
    async def test_query_string_from_path(self, dataview_service):
        """Запрос с FROM path."""
        query = dataview_service.parse_query("SELECT * FROM path:Projects")
        
        assert query.from_path == "Projects"
        assert query.from_type is None

    @pytest.mark.asyncio
    async def test_query_string_asc_sort(self, dataview_service):
        """Запрос с сортировкой ASC."""
        query = dataview_service.parse_query("SELECT * SORT BY title ASC")
        
        assert query.sort_by == "title"
        assert query.sort_order == "asc"

    @pytest.mark.asyncio
    async def test_query_string_execution(
        self, dataview_service, mock_db_manager, sample_documents, sample_properties
    ):
        """Выполнение запроса из строки."""
        documents_table = MagicMock()
        documents_table.to_arrow.return_value.to_pylist.return_value = sample_documents
        
        properties_table = MagicMock()
        properties_table.to_arrow.return_value.to_pylist.return_value = sample_properties
        
        mock_db_manager._ensure_table = AsyncMock(side_effect=[documents_table, properties_table])
        
        result = await dataview_service.query_string(
            "test_vault", "SELECT * FROM type:task WHERE status != done"
        )
        
        assert isinstance(result, DataviewResult)
        assert result.total_count >= 0

    @pytest.mark.asyncio
    async def test_query_error_handling(self, dataview_service, mock_db_manager):
        """Обработка ошибок при запросе."""
        mock_db_manager._ensure_table = AsyncMock(side_effect=Exception("Database error"))
        
        query = DataviewQuery(select=["*"], limit=10)
        result = await dataview_service.query("test_vault", query)
        
        assert isinstance(result, DataviewResult)
        assert result.total_count == 0
        assert len(result.documents) == 0
        assert result.query_time_ms == 0

    @pytest.mark.asyncio
    async def test_query_to_string(self, dataview_service):
        """Преобразование запроса в строку."""
        query = DataviewQuery(
            select=["title", "status"],
            from_type="task",
            where=[WhereCondition("status", "=", "done", "AND")],
            sort_by="priority",
            sort_order="desc",
            limit=10,
        )
        
        query_str = dataview_service._query_to_string(query)
        
        assert "SELECT" in query_str
        assert "title" in query_str
        assert "status" in query_str
        assert "FROM type:task" in query_str
        assert "WHERE" in query_str
        assert "SORT BY priority DESC" in query_str
        assert "LIMIT 10" in query_str

