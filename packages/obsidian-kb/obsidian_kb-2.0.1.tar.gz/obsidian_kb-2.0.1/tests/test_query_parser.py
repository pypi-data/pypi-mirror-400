"""Тесты для query_parser.py (v4)."""

import pytest
from datetime import datetime

from obsidian_kb.query_parser import ParsedQuery, QueryParser


def test_parse_simple_query():
    """Тест парсинга простого запроса без фильтров."""
    parsed = QueryParser.parse("Python async programming")
    
    # Нормализация приводит к lowercase
    assert parsed.text_query == "python async programming"
    assert parsed.tags is None
    assert parsed.date_filters is None
    assert parsed.doc_type is None
    assert not parsed.has_filters()


def test_parse_tags_single():
    """Тест парсинга одного тега."""
    parsed = QueryParser.parse("Python tags:python")
    
    # Нормализация приводит к lowercase
    assert parsed.text_query == "python"
    assert parsed.tags == ["python"]
    assert parsed.has_filters()


def test_parse_tags_multiple():
    """Тест парсинга нескольких тегов."""
    parsed = QueryParser.parse("async programming tags:python async")
    
    assert parsed.text_query == "async programming"
    assert set(parsed.tags) == {"python", "async"}  # Порядок может быть разным
    assert parsed.has_filters()


@pytest.mark.parametrize("query,expected_field,expected_op,expected_date", [
    ("created:2024-01-01", "created", "=", datetime(2024, 1, 1).date()),
    ("modified:2024-12-01", "modified", "=", datetime(2024, 12, 1).date()),
    ("created:>2024-01-01", "created", ">", datetime(2024, 1, 1).date()),
    ("created:>=2024-01-01", "created", ">=", datetime(2024, 1, 1).date()),
    ("created:<2024-12-31", "created", "<", datetime(2024, 12, 31).date()),
    ("created:<=2024-12-31", "created", "<=", datetime(2024, 12, 31).date()),
])
def test_parse_date_variations(query, expected_field, expected_op, expected_date):
    """Тест парсинга различных форматов дат."""
    parsed = QueryParser.parse(query)
    
    assert parsed.date_filters is not None
    assert expected_field in parsed.date_filters
    # В v4 date_filters нормализуется в формат с after/before для удобства использования
    date_filter = parsed.date_filters[expected_field]
    assert isinstance(date_filter, dict)
    
    # Проверяем нормализованный формат
    if expected_op == "=":
        # Для равенства используется диапазон
        assert "after" in date_filter
        assert "before" in date_filter
        assert date_filter["after"].date() == expected_date
        assert date_filter["before"].date() == expected_date
    elif expected_op in [">", ">="]:
        assert "after" in date_filter
        assert date_filter["after"].date() == expected_date
        assert date_filter.get("after_exclusive", False) == (expected_op == ">")
    elif expected_op in ["<", "<="]:
        assert "before" in date_filter
        assert date_filter["before"].date() == expected_date
        assert date_filter.get("before_exclusive", False) == (expected_op == "<")
    
    assert parsed.has_filters()


def test_parse_doc_type():
    """Тест парсинга типа документа с нормализацией."""
    parsed = QueryParser.parse("type:Протокол")
    
    assert parsed.text_query == ""
    # Тип должен быть нормализован (lowercase)
    assert parsed.doc_type == "протокол"
    assert parsed.has_filters()


def test_parse_combined_filters():
    """Тест парсинга комбинированных фильтров."""
    parsed = QueryParser.parse("Python tags:python async created:>2024-01-01 type:протокол")
    
    # Нормализация приводит к lowercase, фильтры удаляются
    assert "python" in parsed.text_query.lower() or parsed.text_query == ""
    assert set(parsed.tags) == {"python", "async"}  # Порядок может быть разным
    assert parsed.date_filters is not None
    assert "created" in parsed.date_filters
    assert parsed.doc_type == "протокол"
    assert parsed.has_filters()


@pytest.mark.asyncio
async def test_build_where_clause_tags():
    """Тест построения WHERE условия для тегов."""
    from unittest.mock import AsyncMock
    
    # Tags требуют db_manager и vault_name для фильтрации через frontmatter_tags
    mock_db = AsyncMock()
    mock_db.get_documents_by_tags.return_value = {"doc1", "doc2"}
    
    parsed = ParsedQuery(text_query="test", tags=["python", "async"])
    where, doc_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=mock_db,
        vault_name="test_vault",
    )
    
    # С db_manager tags обрабатываются через двухэтапный запрос
    assert doc_ids is not None
    assert where is None or where == ""


@pytest.mark.asyncio
async def test_build_where_clause_date():
    """Тест построения WHERE условия для дат.
    
    Примечание: Date filters теперь применяются через двухэтапный запрос,
    а не через WHERE clause для chunks. Поэтому они не должны быть в WHERE.
    """
    parsed = ParsedQuery(
        text_query="test",
        date_filters={
            "created": {"op": ">=", "value": datetime(2024, 1, 1)},
            "modified": {"op": "<=", "value": datetime(2024, 12, 31)},
        }
    )
    where, doc_ids = await QueryParser.build_where_clause(parsed)
    
    # Date filters теперь не в WHERE clause (применяются через двухэтапный запрос)
    assert where is None or "created_at" not in where
    assert doc_ids is None


@pytest.mark.asyncio
async def test_build_where_clause_doc_type():
    """Тест построения WHERE условия для типа документа (v4, fallback на metadata)."""
    parsed = ParsedQuery(text_query="test", doc_type="протокол")
    where, doc_ids = await QueryParser.build_where_clause(parsed)
    
    assert where is not None
    # В v4 без db_manager используется fallback на metadata_json
    assert "metadata_json" in where
    assert doc_ids is None or doc_ids == set()


@pytest.mark.asyncio
async def test_build_where_clause_doc_type_with_db():
    """Тест построения WHERE условия для типа документа с db_manager (двухэтапный запрос)."""
    from unittest.mock import AsyncMock
    
    mock_db = AsyncMock()
    mock_db.get_documents_by_property.return_value = {"doc1", "doc2"}
    
    parsed = ParsedQuery(text_query="test", doc_type="протокол")
    where, doc_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=mock_db,
        vault_name="test_vault",
    )
    
    assert doc_ids == {"doc1", "doc2"}
    assert where is None or where == ""
    
    mock_db.get_documents_by_property.assert_called_once_with(
        vault_name="test_vault",
        property_key="type",
        property_value="протокол",
    )


@pytest.mark.asyncio
async def test_build_where_clause_combined():
    """Тест построения WHERE условия для комбинированных фильтров."""
    from unittest.mock import AsyncMock
    
    mock_db = AsyncMock()
    mock_db.get_documents_by_tags.return_value = {"doc1", "doc2"}
    mock_db.get_documents_by_property.return_value = {"doc1"}
    
    parsed = ParsedQuery(
        text_query="test",
        tags=["python"],
        date_filters={"created": {"op": ">", "value": datetime(2024, 1, 1)}},
        doc_type="протокол"
    )
    where, doc_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=mock_db,
        vault_name="test_vault",
    )
    
    # Tags и doc_type обрабатываются через двухэтапный запрос с db_manager
    # Date filters также через двухэтапный запрос
    assert doc_ids is not None or where is not None
    # Если есть where, проверяем наличие metadata_json для doc_type (fallback)
    if where:
        assert "metadata_json" in where  # Fallback для doc_type


@pytest.mark.asyncio
async def test_build_where_clause_no_filters():
    """Тест построения WHERE условия без фильтров."""
    parsed = ParsedQuery(text_query="test")
    where, doc_ids = await QueryParser.build_where_clause(parsed)
    
    assert where is None
    assert doc_ids is None


@pytest.mark.asyncio
async def test_build_where_clause_type_and_tags_combination():
    """Тест построения WHERE для комбинации type и tags."""
    from unittest.mock import AsyncMock
    
    mock_db = AsyncMock()
    mock_db.get_documents_by_tags.return_value = {"doc1", "doc2"}
    mock_db.get_documents_by_property.return_value = {"doc1"}
    
    parsed = QueryParser.parse("type:project tags:ecosystem")
    
    assert parsed.doc_type == "project"
    assert "ecosystem" in parsed.tags
    
    where, doc_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=mock_db,
        vault_name="test_vault",
    )
    # С db_manager tags и doc_type обрабатываются через двухэтапный запрос
    assert doc_ids is not None or where is not None


@pytest.mark.asyncio
async def test_build_where_clause_links():
    """Тест построения WHERE условия для связанных заметок."""
    parsed = ParsedQuery(text_query="test", links=["Note1", "path/to/Note2"])
    where, doc_ids = await QueryParser.build_where_clause(parsed)
    
    assert where is not None
    assert "array_contains(links, 'note1')" in where
    assert "array_contains(links, 'note2')" in where
    assert "AND" in where
    assert doc_ids is None


@pytest.mark.asyncio
async def test_build_where_clause_tags_or():
    """Тест построения WHERE для тегов с OR оператором."""
    from unittest.mock import AsyncMock
    
    mock_db = AsyncMock()
    mock_db.get_documents_by_tags.return_value = {"doc1", "doc2"}
    
    parsed = QueryParser.parse("tags:python OR tags:javascript")
    
    assert parsed.tags == ["python"]
    assert parsed.tags_or == ["javascript"]
    
    where, doc_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=mock_db,
        vault_name="test_vault",
    )
    # С db_manager tags обрабатываются через двухэтапный запрос
    assert doc_ids is not None
    assert where is None or where == ""


@pytest.mark.asyncio
async def test_build_where_clause_tags_not():
    """Тест построения WHERE для тегов с NOT оператором."""
    from unittest.mock import AsyncMock
    
    mock_db = AsyncMock()
    mock_db.get_documents_by_tags.return_value = {"doc1", "doc2"}
    
    parsed = QueryParser.parse("tags:python NOT tags:deprecated")
    
    assert parsed.tags == ["python"]
    assert parsed.tags_not == ["deprecated"]
    
    where, doc_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=mock_db,
        vault_name="test_vault",
    )
    # С db_manager tags обрабатываются через двухэтапный запрос
    # NOT теги могут использовать fallback на metadata
    assert doc_ids is not None or where is not None


@pytest.mark.asyncio
async def test_build_where_clause_type_or_with_db():
    """Тест построения WHERE для типа документа с OR оператором и db_manager."""
    from unittest.mock import AsyncMock
    
    mock_db = AsyncMock()
    mock_db.get_documents_by_property.side_effect = [
        {"doc1", "doc2"},  # для "протокол"
        {"doc3", "doc4"},  # для "договор"
    ]
    
    parsed = QueryParser.parse("type:протокол OR type:договор")
    
    assert parsed.doc_type == "протокол"
    assert parsed.doc_type_or == ["договор"]
    
    where, doc_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=mock_db,
        vault_name="test_vault",
    )
    
    assert doc_ids == {"doc1", "doc2", "doc3", "doc4"}  # Объединение через OR
    assert where is None or where == ""
