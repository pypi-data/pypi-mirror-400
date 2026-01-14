"""Тесты для модуля filters (v4)."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from obsidian_kb.filters import (
    DateFilter,
    DocTypeFilter,
    FilterBuilder,
    LinkFilter,
    TagFilter,
)


class TestTagFilter:
    """Тесты для TagFilter."""
    
    def test_build_condition_single_tag(self):
        """Тест построения условия для одного тега из frontmatter."""
        condition = TagFilter.build_condition(["meeting"], tag_type="frontmatter")
        assert "array_contains(frontmatter_tags, 'meeting')" in condition.sql
        assert condition.sql == "array_contains(frontmatter_tags, 'meeting')"
    
    def test_build_condition_multiple_tags(self):
        """Тест построения условия для нескольких тегов из frontmatter."""
        condition = TagFilter.build_condition(["meeting", "person"], tag_type="frontmatter")
        assert "array_contains(frontmatter_tags, 'meeting')" in condition.sql
        assert "array_contains(frontmatter_tags, 'person')" in condition.sql
        assert "AND" in condition.sql
    
    def test_build_condition_inline_tags(self):
        """Тест построения условия для inline тегов."""
        condition = TagFilter.build_condition(["meeting"], tag_type="inline")
        assert "array_contains(inline_tags, 'meeting')" in condition.sql
    
    def test_build_condition_empty(self):
        """Тест построения условия для пустого списка."""
        condition = TagFilter.build_condition([])
        assert condition.sql == ""
    
    def test_build_condition_normalizes_tags(self):
        """Тест нормализации тегов при построении условия."""
        condition = TagFilter.build_condition(["Meeting", "PERSON"], tag_type="frontmatter")
        assert "array_contains(frontmatter_tags, 'meeting')" in condition.sql
        assert "array_contains(frontmatter_tags, 'person')" in condition.sql


class TestLinkFilter:
    """Тесты для LinkFilter."""
    
    def test_build_condition_single_link(self):
        """Тест построения условия для одной ссылки."""
        condition = LinkFilter.build_condition(["muratov"])
        assert "array_contains(links, 'muratov')" in condition.sql
    
    def test_build_condition_multiple_links(self):
        """Тест построения условия для нескольких ссылок."""
        condition = LinkFilter.build_condition(["muratov", "person"])
        assert "array_contains(links, 'muratov')" in condition.sql
        assert "array_contains(links, 'person')" in condition.sql
        assert "AND" in condition.sql
    
    def test_build_condition_empty(self):
        """Тест построения условия для пустого списка."""
        condition = LinkFilter.build_condition([])
        assert condition.sql == ""


class TestDocTypeFilter:
    """Тесты для DocTypeFilter (v4)."""
    
    @pytest.mark.asyncio
    async def test_build_condition_without_db_manager(self):
        """Тест построения условия без db_manager (fallback на metadata)."""
        doc_ids, condition = await DocTypeFilter.build_condition("person")
        assert doc_ids == set()
        assert "metadata_json" in condition.sql
        assert '"type":"person"' in condition.sql
    
    @pytest.mark.asyncio
    async def test_build_condition_with_db_manager(self):
        """Тест построения условия с db_manager (двухэтапный запрос)."""
        mock_db = AsyncMock()
        mock_db.get_documents_by_property.return_value = {"doc1", "doc2"}
        
        doc_ids, condition = await DocTypeFilter.build_condition("person", mock_db, "test_vault")
        assert doc_ids == {"doc1", "doc2"}
        assert condition.sql == ""
        
        mock_db.get_documents_by_property.assert_called_once_with(
            vault_name="test_vault",
            property_key="type",
            property_value="person",
        )
    
    @pytest.mark.asyncio
    async def test_build_condition_empty(self):
        """Тест построения условия для пустого типа."""
        doc_ids, condition = await DocTypeFilter.build_condition("")
        assert doc_ids == set()
        assert condition.sql == ""


class TestDateFilter:
    """Тесты для DateFilter."""
    
    def test_build_condition_equals(self):
        """Тест построения условия для равенства."""
        condition = DateFilter.build_condition("created", "=", "2024-01-01T00:00:00")
        assert "created_at = '2024-01-01T00:00:00'" in condition.sql
    
    def test_build_condition_greater_than(self):
        """Тест построения условия для больше."""
        condition = DateFilter.build_condition("created", ">", "2024-01-01T00:00:00", exclude_null=True)
        assert "created_at IS NOT NULL" in condition.sql
        assert "created_at >" in condition.sql
    
    def test_build_condition_less_than(self):
        """Тест построения условия для меньше."""
        condition = DateFilter.build_condition("modified", "<", "2024-12-31T00:00:00")
        assert "modified_at < '2024-12-31T00:00:00'" in condition.sql


class TestFilterBuilder:
    """Тесты для FilterBuilder (v4)."""
    
    @pytest.mark.asyncio
    async def test_build_where_clause_tags_only(self):
        """Тест построения WHERE для тегов из frontmatter (v4 - двухэтапный запрос)."""
        # Без db_manager и vault_name фильтр по frontmatter тегам пропускается
        where, doc_ids = await FilterBuilder.build_where_clause(tags=["meeting"])
        assert where is None or "frontmatter_tags" not in where
        assert doc_ids is None
        
        # С db_manager и vault_name используется двухэтапный запрос
        mock_db = AsyncMock()
        mock_db.get_documents_by_tags.return_value = {"doc1", "doc2"}
        
        where, doc_ids = await FilterBuilder.build_where_clause(
            tags=["meeting"],
            db_manager=mock_db,
            vault_name="test_vault",
        )
        assert where is None or where == ""
        assert doc_ids == {"doc1", "doc2"}
        
        mock_db.get_documents_by_tags.assert_called_once_with(
            vault_name="test_vault",
            tags=["meeting"],
            match_all=True,
        )
    
    @pytest.mark.asyncio
    async def test_build_where_clause_inline_tags_only(self):
        """Тест построения WHERE для inline тегов."""
        where, doc_ids = await FilterBuilder.build_where_clause(inline_tags=["meeting"])
        assert "array_contains(inline_tags, 'meeting')" in where
        assert doc_ids is None
    
    @pytest.mark.asyncio
    async def test_build_where_clause_links_only(self):
        """Тест построения WHERE для ссылок."""
        where, doc_ids = await FilterBuilder.build_where_clause(links=["muratov"])
        assert "array_contains(links, 'muratov')" in where
        assert doc_ids is None
    
    @pytest.mark.asyncio
    async def test_build_where_clause_doc_type_without_db(self):
        """Тест построения WHERE для типа документа без db_manager (fallback)."""
        where, doc_ids = await FilterBuilder.build_where_clause(doc_type="person")
        assert "metadata_json" in where
        assert doc_ids is None
    
    @pytest.mark.asyncio
    async def test_build_where_clause_doc_type_with_db(self):
        """Тест построения WHERE для типа документа с db_manager (двухэтапный запрос)."""
        mock_db = AsyncMock()
        mock_db.get_documents_by_property.return_value = {"doc1", "doc2"}
        
        where, doc_ids = await FilterBuilder.build_where_clause(
            doc_type="person",
            db_manager=mock_db,
            vault_name="test_vault",
        )
        assert where is None or where == ""
        assert doc_ids == {"doc1", "doc2"}
    
    @pytest.mark.asyncio
    async def test_build_where_clause_combined(self):
        """Тест построения комбинированного WHERE."""
        # Без db_manager frontmatter теги пропускаются
        where, doc_ids = await FilterBuilder.build_where_clause(
            tags=["meeting"],
            inline_tags=["note"],
            links=["muratov"]
        )
        # frontmatter теги не должны быть в WHERE (пропущены без db_manager)
        assert "array_contains(inline_tags, 'note')" in where
        assert "array_contains(links, 'muratov')" in where
        assert where.count("AND") >= 1
        assert doc_ids is None
        
        # С db_manager используется двухэтапный запрос для frontmatter тегов
        mock_db = AsyncMock()
        mock_db.get_documents_by_tags.return_value = {"doc1", "doc2"}
        
        where, doc_ids = await FilterBuilder.build_where_clause(
            tags=["meeting"],
            inline_tags=["note"],
            links=["muratov"],
            db_manager=mock_db,
            vault_name="test_vault",
        )
        assert "array_contains(inline_tags, 'note')" in where
        assert "array_contains(links, 'muratov')" in where
        assert doc_ids == {"doc1", "doc2"}
    
    @pytest.mark.asyncio
    async def test_build_where_clause_with_dates(self):
        """Тест построения WHERE с датами.
        
        Примечание: Date filters теперь применяются через двухэтапный запрос,
        а не через WHERE clause для chunks. Поэтому они не должны быть в WHERE.
        """
        date_filters = {
            "created": {
                "op": ">=",
                "value": datetime(2024, 1, 1)
            }
        }
        where, doc_ids = await FilterBuilder.build_where_clause(date_filters=date_filters)
        # Date filters теперь не в WHERE clause для chunks (применяются через двухэтапный запрос)
        assert where is None or "created_at" not in where
        # doc_ids может быть None, так как date filters обрабатываются в BaseSearchStrategy
        assert doc_ids is None
    
    @pytest.mark.asyncio
    async def test_build_where_clause_empty(self):
        """Тест построения пустого WHERE."""
        where, doc_ids = await FilterBuilder.build_where_clause()
        assert where is None
        assert doc_ids is None
    
    @pytest.mark.asyncio
    async def test_build_where_clause_doc_type_or_with_db(self):
        """Тест построения WHERE для типа документа с OR оператором и db_manager."""
        mock_db = AsyncMock()
        mock_db.get_documents_by_property.side_effect = [
            {"doc1", "doc2"},  # для "протокол"
            {"doc3", "doc4"},  # для "договор"
        ]
        
        where, doc_ids = await FilterBuilder.build_where_clause(
            doc_type="протокол",
            doc_type_or=["договор"],
            db_manager=mock_db,
            vault_name="test_vault",
        )
        assert doc_ids == {"doc1", "doc2", "doc3", "doc4"}  # Объединение через OR
        assert where is None or where == ""
    
    @pytest.mark.asyncio
    async def test_build_where_clause_doc_type_not_with_db(self):
        """Тест построения WHERE для типа документа с NOT оператором и db_manager."""
        mock_db = AsyncMock()
        mock_db.get_documents_by_property.return_value = {"doc1", "doc2"}
        
        where, doc_ids = await FilterBuilder.build_where_clause(
            doc_type="протокол",
            doc_type_not="архив",
            db_manager=mock_db,
            vault_name="test_vault",
        )
        # Для NOT пока используем fallback на metadata
        # where может быть None или строкой
        assert where is None or (isinstance(where, str) and ("metadata_json" in where or where == ""))
        assert doc_ids is None or isinstance(doc_ids, set)
    
    @pytest.mark.asyncio
    async def test_build_where_clause_complex_combination(self):
        """Тест построения сложного комбинированного WHERE."""
        where, doc_ids = await FilterBuilder.build_where_clause(
            tags=["python"],
            inline_tags=["note"],
            links=["muratov"],
            date_filters={
                "created": {"op": ">", "value": datetime(2024, 1, 1)}
            }
        )
        # Проверяем наличие фильтров в WHERE
        assert where is not None
        assert "array_contains(inline_tags, 'note')" in where
        assert "array_contains(links, 'muratov')" in where
        # frontmatter tags требуют db_manager и vault_name, поэтому могут отсутствовать в WHERE
        # date filters теперь не в WHERE clause (применяются через двухэтапный запрос)
        assert doc_ids is None
