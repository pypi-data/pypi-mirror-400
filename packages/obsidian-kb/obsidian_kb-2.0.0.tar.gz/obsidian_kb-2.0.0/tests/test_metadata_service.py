"""Тесты для MetadataService (storage/metadata_service.py).

Phase 5: Тестовая инфраструктура v0.7.0
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.core.connection_manager import DBConnectionManager
from obsidian_kb.core.ttl_cache import TTLCache
from obsidian_kb.storage.metadata_service import MetadataService
from obsidian_kb.types import (
    DatabaseError,
    DocumentInfo,
    SearchResult,
    VaultNotFoundError,
    VaultStats,
)


@pytest.fixture
def mock_connection_manager():
    """Мок DBConnectionManager."""
    mock = MagicMock(spec=DBConnectionManager)
    mock.get_or_create_connection.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_cache():
    """TTLCache для тестов."""
    return TTLCache(ttl_seconds=300, max_size=1000)


@pytest.fixture
def service(mock_connection_manager, mock_cache):
    """MetadataService с моками."""
    return MetadataService(
        connection_manager=mock_connection_manager,
        document_info_cache=mock_cache,
    )


class TestMetadataServiceInit:
    """Тесты инициализации."""

    def test_with_cache(self, mock_connection_manager, mock_cache):
        """Инициализация с кэшем."""
        service = MetadataService(
            connection_manager=mock_connection_manager,
            document_info_cache=mock_cache,
        )
        assert service._connection_manager is mock_connection_manager
        assert service._document_info_cache is mock_cache

    def test_without_cache(self, mock_connection_manager):
        """Инициализация без кэша."""
        service = MetadataService(connection_manager=mock_connection_manager)
        assert service._document_info_cache is None


class TestNormalizeVaultName:
    """Тесты нормализации имени vault."""

    def test_basic_name(self, service):
        """Базовое имя vault."""
        assert service._normalize_vault_name("my_vault") == "my_vault"

    def test_special_characters(self, service):
        """Специальные символы заменяются на _."""
        result = service._normalize_vault_name("my@vault!")
        assert "@" not in result
        assert "!" not in result

    def test_multiple_underscores(self, service):
        """Множественные подчёркивания схлопываются."""
        assert service._normalize_vault_name("my___vault") == "my_vault"


class TestGetTableName:
    """Тесты получения имени таблицы."""

    def test_chunks_table(self, service):
        """Имя таблицы chunks."""
        result = service._get_table_name("my_vault", "chunks")
        assert result == "vault_my_vault_chunks"

    def test_documents_table(self, service):
        """Имя таблицы documents."""
        result = service._get_table_name("my_vault", "documents")
        assert result == "vault_my_vault_documents"

    def test_metadata_table(self, service):
        """Имя таблицы metadata."""
        result = service._get_table_name("my_vault", "metadata")
        assert result == "vault_my_vault_metadata"


class TestDictToSearchResult:
    """Тесты конвертации dict в SearchResult."""

    def test_basic_conversion(self, service):
        """Базовая конвертация."""
        row = {
            "id": "chunk_1",
            "vault_name": "vault",
            "file_path": "notes/test.md",
            "title": "Test",
            "section": "Section",
            "content": "Content",
            "tags": ["tag1"],
            "created_at": "2024-01-01T10:00:00",
            "modified_at": "2024-01-15T14:30:00",
        }
        result = service._dict_to_search_result(row, 0.85)

        assert result.chunk_id == "chunk_1"
        assert result.vault_name == "vault"
        assert result.file_path == "notes/test.md"
        assert result.title == "Test"
        assert result.score == 0.85
        assert result.created_at == datetime(2024, 1, 1, 10, 0, 0)
        assert result.modified_at == datetime(2024, 1, 15, 14, 30, 0)

    def test_missing_optional_fields(self, service):
        """Отсутствующие опциональные поля."""
        row = {
            "id": "chunk_1",
            "vault_name": "vault",
            "file_path": "notes/test.md",
            "title": "Test",
            "section": "",
            "content": "",
            "created_at": None,
            "modified_at": None,
        }
        result = service._dict_to_search_result(row, 0.5)

        assert result.created_at is None
        assert result.tags == []


class TestGetAllLinks:
    """Тесты получения всех ссылок."""

    @pytest.mark.asyncio
    async def test_basic_links(self, service):
        """Базовое получение ссылок."""
        mock_table = MagicMock()
        mock_arrow = MagicMock()
        mock_arrow.num_rows = 2
        mock_arrow.__getitem__ = lambda self, key: MagicMock(
            to_pylist=lambda: [["link1", "link2"], ["link2", "link3"]]
        )
        mock_table.to_arrow.return_value = mock_arrow

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            results = await service.get_all_links("vault")

        assert "link1" in results
        assert "link2" in results
        assert "link3" in results
        # Результат отсортирован
        assert results == sorted(results)

    @pytest.mark.asyncio
    async def test_empty_vault(self, service):
        """Пустой vault возвращает пустой список."""
        mock_table = MagicMock()
        mock_arrow = MagicMock()
        mock_arrow.num_rows = 0
        mock_table.to_arrow.return_value = mock_arrow

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            results = await service.get_all_links("vault")

        assert results == []


class TestGetAllTags:
    """Тесты получения всех тегов."""

    @pytest.mark.asyncio
    async def test_frontmatter_tags(self, service):
        """Получение frontmatter тегов."""
        mock_table = MagicMock()
        mock_arrow = MagicMock()
        mock_arrow.num_rows = 2
        mock_arrow.column_names = ["frontmatter_tags"]
        mock_arrow.__getitem__ = lambda self, key: MagicMock(
            to_pylist=lambda: [["tag1", "tag2"], ["tag2", "tag3"]]
        )
        mock_table.to_arrow.return_value = mock_arrow

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            results = await service.get_all_tags("vault", tag_type="frontmatter")

        assert "tag1" in results
        assert "tag2" in results
        assert "tag3" in results

    @pytest.mark.asyncio
    async def test_inline_tags(self, service):
        """Получение inline тегов."""
        mock_table = MagicMock()
        mock_arrow = MagicMock()
        mock_arrow.num_rows = 1
        mock_arrow.column_names = ["inline_tags"]
        mock_arrow.__getitem__ = lambda self, key: MagicMock(
            to_pylist=lambda: [["inline1", "inline2"]]
        )
        mock_table.to_arrow.return_value = mock_arrow

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            results = await service.get_all_tags("vault", tag_type="inline")

        assert "inline1" in results
        assert "inline2" in results


class TestGetVaultStats:
    """Тесты получения статистики vault."""

    @pytest.mark.asyncio
    async def test_basic_stats(self, service):
        """Базовая статистика."""
        # Мок для documents table
        mock_docs_table = MagicMock()
        mock_docs_arrow = MagicMock()
        mock_docs_arrow.num_rows = 10
        mock_docs_arrow.__getitem__ = lambda self, key: {
            "file_size": MagicMock(to_pylist=lambda: [100] * 10),
            "modified_at": MagicMock(to_pylist=lambda: ["2024-01-01T00:00:00"] * 10),
        }[key]
        mock_docs_table.to_arrow.return_value = mock_docs_arrow

        # Мок для chunks table
        mock_chunks_table = MagicMock()
        mock_chunks_arrow = MagicMock()
        mock_chunks_arrow.num_rows = 50
        mock_chunks_table.to_arrow.return_value = mock_chunks_arrow

        call_count = [0]

        async def mock_ensure(vault_name, table_type):
            call_count[0] += 1
            if table_type == "documents":
                return mock_docs_table
            elif table_type == "chunks":
                return mock_chunks_table
            else:
                # metadata table mock
                mock_meta = MagicMock()
                mock_meta_arrow = MagicMock()
                mock_meta_arrow.num_rows = 0
                mock_meta.to_arrow.return_value = mock_meta_arrow
                return mock_meta

        with patch.object(service, "_ensure_table", side_effect=mock_ensure):
            stats = await service.get_vault_stats("vault")

        assert isinstance(stats, VaultStats)
        assert stats.vault_name == "vault"
        assert stats.file_count == 10
        assert stats.chunk_count == 50


class TestListVaults:
    """Тесты получения списка vault'ов."""

    @pytest.mark.asyncio
    async def test_basic_list(self, service, mock_connection_manager):
        """Базовый список vault'ов."""
        mock_db = MagicMock()
        # Метод использует list_tables() который возвращает список
        mock_db.list_tables.return_value = [
            "vault_vault1_chunks",
            "vault_vault1_documents",
            "vault_vault2_chunks",
            "other_table",  # Не vault таблица
        ]
        mock_connection_manager.get_or_create_connection.return_value = mock_db

        vaults = await service.list_vaults()

        assert "vault1" in vaults
        assert "vault2" in vaults
        # Проверяем что дублей нет
        assert len(vaults) == len(set(vaults))

    @pytest.mark.asyncio
    async def test_empty_db(self, service, mock_connection_manager):
        """Пустая БД."""
        mock_db = MagicMock()
        mock_db.list_tables.return_value = []
        mock_connection_manager.get_or_create_connection.return_value = mock_db

        vaults = await service.list_vaults()

        assert vaults == []


class TestGetDocumentsByProperty:
    """Тесты получения документов по свойству."""

    @pytest.mark.asyncio
    async def test_by_exact_value(self, service):
        """Поиск по точному значению."""
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query

        mock_arrow = MagicMock()
        mock_arrow.num_rows = 2
        mock_arrow.__getitem__ = lambda self, key: MagicMock(
            to_pylist=lambda: ["doc1", "doc2"]
        )
        mock_query.to_arrow.return_value = mock_arrow
        mock_table.search.return_value = mock_query

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            results = await service.get_documents_by_property(
                vault_name="vault",
                property_key="type",
                property_value="note",
            )

        assert "doc1" in results
        assert "doc2" in results


class TestGetDocumentProperties:
    """Тесты получения свойств документа."""

    @pytest.mark.asyncio
    async def test_basic_properties(self, service):
        """Базовое получение свойств."""
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query

        mock_arrow = MagicMock()
        mock_arrow.num_rows = 2
        mock_arrow.__getitem__ = lambda self, key: {
            "property_key": MagicMock(to_pylist=lambda: ["type", "author"]),
            "property_value": MagicMock(to_pylist=lambda: ["note", "user"]),
        }[key]
        mock_query.to_arrow.return_value = mock_arrow
        mock_table.search.return_value = mock_query

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            properties = await service.get_document_properties("vault", "doc1")

        assert properties["type"] == "note"
        assert properties["author"] == "user"


class TestGetDocumentInfo:
    """Тесты получения информации о документе."""

    @pytest.mark.asyncio
    async def test_basic_info(self, service):
        """Базовое получение информации."""
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query

        mock_arrow = MagicMock()
        mock_arrow.num_rows = 1
        mock_arrow.column_names = [
            "document_id",
            "vault_name",
            "file_path",
            "file_path_full",
            "file_name",
            "file_extension",
            "content_type",
            "title",
            "created_at",
            "modified_at",
            "file_size",
            "chunk_count",
        ]
        mock_arrow.__getitem__ = lambda self, key: [
            MagicMock(
                as_py=lambda: {
                    "document_id": "vault::file.md",
                    "vault_name": "vault",
                    "file_path": "file.md",
                    "file_path_full": "/path/to/file.md",
                    "file_name": "file.md",
                    "file_extension": ".md",
                    "content_type": "markdown",
                    "title": "Title",
                    "created_at": "2024-01-01T00:00:00",
                    "modified_at": "2024-01-15T00:00:00",
                    "file_size": 1000,
                    "chunk_count": 5,
                }[key]
            )
        ]
        mock_query.to_arrow.return_value = mock_arrow
        mock_table.search.return_value = mock_query

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            info = await service.get_document_info("vault", "vault::file.md")

        assert isinstance(info, DocumentInfo)
        assert info.document_id == "vault::file.md"
        assert info.title == "Title"

    @pytest.mark.asyncio
    async def test_not_found(self, service):
        """Документ не найден."""
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query

        mock_arrow = MagicMock()
        mock_arrow.num_rows = 0
        mock_query.to_arrow.return_value = mock_arrow
        mock_table.search.return_value = mock_query

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            info = await service.get_document_info("vault", "vault::nonexistent.md")

        assert info is None


class TestGetDocumentsByTags:
    """Тесты получения документов по тегам."""

    @pytest.mark.asyncio
    async def test_match_all(self, service):
        """Поиск с условием AND."""
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query

        mock_arrow = MagicMock()
        mock_arrow.num_rows = 1
        mock_arrow.__getitem__ = lambda self, key: MagicMock(
            to_pylist=lambda: ["doc1"]
        )
        mock_query.to_arrow.return_value = mock_arrow
        mock_table.search.return_value = mock_query

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            results = await service.get_documents_by_tags(
                vault_name="vault",
                tags=["python", "testing"],
                match_all=True,
            )

        assert "doc1" in results

    @pytest.mark.asyncio
    async def test_empty_tags(self, service):
        """Пустой список тегов возвращает пустой результат."""
        results = await service.get_documents_by_tags(
            vault_name="vault",
            tags=[],
        )

        assert results == set()


class TestCaching:
    """Тесты кэширования."""

    @pytest.mark.asyncio
    async def test_cache_hit(self, service, mock_cache):
        """Попадание в кэш."""
        doc_info = {
            "file_path": "file.md",
            "title": "Cached Title",
        }
        mock_cache.set("vault::doc1", doc_info)

        result = await service._get_document_info_cached("vault", "doc1")

        assert result == doc_info

    @pytest.mark.asyncio
    async def test_cache_not_found_marker(self, service, mock_cache):
        """Кэш с маркером "не найден"."""
        mock_cache.set("vault::doc1", {"__not_found__": True})

        result = await service._get_document_info_cached("vault", "doc1")

        assert result is None

    @pytest.mark.asyncio
    async def test_no_cache(self, mock_connection_manager):
        """Работа без кэша."""
        service = MetadataService(connection_manager=mock_connection_manager)

        # Мок для _get_document_info_uncached
        with patch.object(
            service, "_get_document_info_uncached", new_callable=AsyncMock
        ) as mock_uncached:
            mock_uncached.return_value = {"file_path": "file.md"}

            result = await service._get_document_info_cached("vault", "doc1")

        assert result == {"file_path": "file.md"}
        mock_uncached.assert_called_once()
