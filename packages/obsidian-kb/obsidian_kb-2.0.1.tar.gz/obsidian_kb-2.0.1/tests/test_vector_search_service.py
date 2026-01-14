"""Тесты для VectorSearchService (search/vector_search_service.py).

Phase 5: Тестовая инфраструктура v0.7.0
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.core.connection_manager import DBConnectionManager
from obsidian_kb.core.data_normalizer import DataNormalizer
from obsidian_kb.core.ttl_cache import TTLCache
from obsidian_kb.search.vector_search_service import VectorSearchService
from obsidian_kb.types import DatabaseError, SearchResult, VaultNotFoundError


@pytest.fixture
def mock_connection_manager():
    """Мок DBConnectionManager."""
    mock = MagicMock(spec=DBConnectionManager)
    mock.get_or_create_connection.return_value = MagicMock()
    return mock


@pytest.fixture
def normalizer():
    """DataNormalizer."""
    return DataNormalizer()


@pytest.fixture
def service(mock_connection_manager, normalizer):
    """VectorSearchService с моками."""
    # Кэш создаётся внутри сервиса
    return VectorSearchService(
        connection_manager=mock_connection_manager,
        normalizer=normalizer,
    )


class TestVectorSearchServiceInit:
    """Тесты инициализации."""

    def test_with_all_params(self, mock_connection_manager, normalizer):
        """Инициализация со всеми параметрами."""
        cache = TTLCache(ttl_seconds=300, max_size=1000)
        service = VectorSearchService(
            connection_manager=mock_connection_manager,
            normalizer=normalizer,
            cache=cache,
        )
        assert service._connection_manager is mock_connection_manager
        assert service._normalizer is normalizer
        assert service._document_info_cache is cache

    def test_with_defaults(self, mock_connection_manager):
        """Инициализация с дефолтными значениями."""
        service = VectorSearchService(connection_manager=mock_connection_manager)
        assert service._normalizer is not None
        assert service._document_info_cache is not None

    def test_cache_ttl(self):
        """TTL кэша по умолчанию."""
        assert VectorSearchService.DOCUMENT_CACHE_TTL_SECONDS == 300.0


class TestNormalizeVaultName:
    """Тесты нормализации имени vault."""

    def test_basic_name(self, service):
        """Базовое имя vault."""
        assert service._normalize_vault_name("my_vault") == "my_vault"

    def test_special_characters(self, service):
        """Специальные символы заменяются на _."""
        # my@vault! -> my_vault_ -> my_vault (strip _)
        assert service._normalize_vault_name("my@vault!") == "my_vault"

    def test_multiple_underscores(self, service):
        """Множественные подчёркивания схлопываются."""
        assert service._normalize_vault_name("my___vault") == "my_vault"

    def test_leading_trailing_underscores(self, service):
        """Подчёркивания по краям убираются."""
        assert service._normalize_vault_name("_vault_") == "vault"


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

    def test_default_table_type(self, service):
        """По умолчанию chunks."""
        result = service._get_table_name("my_vault")
        assert result == "vault_my_vault_chunks"


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

    def test_missing_dates(self, service):
        """Отсутствующие даты."""
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
        assert result.modified_at is not None  # Fallback to now()

    def test_invalid_date_format(self, service):
        """Неправильный формат даты."""
        row = {
            "id": "chunk_1",
            "vault_name": "vault",
            "file_path": "notes/test.md",
            "title": "Test",
            "section": "",
            "content": "",
            "created_at": "invalid-date",
            "modified_at": "also-invalid",
        }
        result = service._dict_to_search_result(row, 0.5)

        assert result.created_at is None
        assert result.modified_at is not None  # Fallback to now()


class TestInvalidateDocumentCache:
    """Тесты инвалидации кэша."""

    def test_invalidate_single_document(self, service):
        """Инвалидация одного документа."""
        cache = service._document_info_cache
        cache.set("vault::doc1", {"title": "Doc 1"})
        cache.set("vault::doc2", {"title": "Doc 2"})

        result = service.invalidate_document_cache("vault", "doc1")

        assert result == 1
        assert cache.get("vault::doc1") is None
        assert cache.get("vault::doc2") is not None

    def test_invalidate_vault(self, service):
        """Инвалидация всего vault."""
        cache = service._document_info_cache
        cache.set("vault1::doc1", {"title": "V1 Doc 1"})
        cache.set("vault1::doc2", {"title": "V1 Doc 2"})
        cache.set("vault2::doc1", {"title": "V2 Doc 1"})

        result = service.invalidate_document_cache("vault1")

        assert result == 2
        assert cache.get("vault1::doc1") is None
        assert cache.get("vault1::doc2") is None
        assert cache.get("vault2::doc1") is not None


class TestVectorSearch:
    """Тесты векторного поиска."""

    @pytest.mark.asyncio
    async def test_basic_search(self, service):
        """Базовый векторный поиск."""
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_query.limit.return_value = mock_query
        mock_query.where.return_value = mock_query

        # Создаём мок Arrow таблицы
        mock_arrow_table = MagicMock()
        mock_arrow_table.to_pylist.return_value = [
            {
                "chunk_id": "vault::file.md::0",
                "document_id": "vault::file.md",
                "vault_name": "vault",
                "section": "Intro",
                "content": "Content",
                "_distance": 0.2,
            }
        ]
        mock_query.to_arrow.return_value = mock_arrow_table
        mock_table.search.return_value = mock_query

        # Мок для _ensure_table
        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            # Мок для _get_document_info_cached
            with patch.object(
                service, "_get_document_info_cached", new_callable=AsyncMock
            ) as mock_doc_info:
                mock_doc_info.return_value = {
                    "file_path": "file.md",
                    "title": "Title",
                    "created_at": "2024-01-01T00:00:00",
                    "modified_at": "2024-01-15T00:00:00",
                }

                results = await service.vector_search(
                    vault_name="vault",
                    query_vector=[0.1, 0.2, 0.3],
                    limit=10,
                )

        assert len(results) == 1
        assert results[0].chunk_id == "vault::file.md::0"
        # score = 1 - distance = 1 - 0.2 = 0.8
        assert results[0].score == pytest.approx(0.8, rel=0.01)

    @pytest.mark.asyncio
    async def test_search_with_where(self, service):
        """Поиск с WHERE условием."""
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_query.limit.return_value = mock_query
        mock_query.where.return_value = mock_query

        mock_arrow_table = MagicMock()
        mock_arrow_table.to_pylist.return_value = []
        mock_query.to_arrow.return_value = mock_arrow_table
        mock_table.search.return_value = mock_query

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            await service.vector_search(
                vault_name="vault",
                query_vector=[0.1],
                limit=5,
                where="section = 'intro'",
            )

        mock_query.where.assert_called()

    @pytest.mark.asyncio
    async def test_search_with_document_ids(self, service):
        """Поиск с фильтром по document_ids."""
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_query.limit.return_value = mock_query
        mock_query.where.return_value = mock_query

        mock_arrow_table = MagicMock()
        mock_arrow_table.to_pylist.return_value = []
        mock_query.to_arrow.return_value = mock_arrow_table
        mock_table.search.return_value = mock_query

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            await service.vector_search(
                vault_name="vault",
                query_vector=[0.1],
                document_ids={"vault::doc1", "vault::doc2"},
            )

        # Проверяем что where был вызван с OR условием
        mock_query.where.assert_called()


class TestFTSSearch:
    """Тесты полнотекстового поиска."""

    @pytest.mark.asyncio
    async def test_basic_fts(self, service):
        """Базовый FTS поиск."""
        mock_table = MagicMock()
        mock_query = MagicMock()
        mock_query.limit.return_value = mock_query
        mock_query.where.return_value = mock_query

        mock_arrow_table = MagicMock()
        mock_arrow_table.to_pylist.return_value = [
            {
                "chunk_id": "vault::file.md::0",
                "document_id": "vault::file.md",
                "vault_name": "vault",
                "section": "Intro",
                "content": "Python programming",
                "_score": 5.0,
            }
        ]
        mock_query.to_arrow.return_value = mock_arrow_table
        mock_table.search.return_value = mock_query

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            with patch.object(
                service, "_create_fts_index", new_callable=AsyncMock
            ):
                with patch.object(
                    service, "_get_document_info_cached", new_callable=AsyncMock
                ) as mock_doc_info:
                    mock_doc_info.return_value = {
                        "file_path": "file.md",
                        "title": "Title",
                        "modified_at": "2024-01-15T00:00:00",
                    }

                    results = await service.fts_search(
                        vault_name="vault",
                        query="python",
                        limit=10,
                    )

        assert len(results) == 1
        assert results[0].chunk_id == "vault::file.md::0"
        # score = min(1.0, _score / 10.0) = min(1.0, 0.5) = 0.5
        assert results[0].score == pytest.approx(0.5, rel=0.01)


class TestHybridSearch:
    """Тесты гибридного поиска."""

    @pytest.mark.asyncio
    async def test_basic_hybrid(self, service):
        """Базовый гибридный поиск."""
        # Мок результатов векторного поиска
        vector_result = SearchResult(
            chunk_id="chunk_1",
            vault_name="vault",
            file_path="file.md",
            title="Title",
            section="",
            content="Content",
            tags=[],
            score=0.8,
            created_at=None,
            modified_at=datetime.now(),
        )

        # Мок результатов FTS поиска
        fts_result = SearchResult(
            chunk_id="chunk_2",
            vault_name="vault",
            file_path="file2.md",
            title="Title 2",
            section="",
            content="Content 2",
            tags=[],
            score=0.7,
            created_at=None,
            modified_at=datetime.now(),
        )

        with patch.object(
            service, "vector_search", new_callable=AsyncMock
        ) as mock_vector:
            mock_vector.return_value = [vector_result]

            with patch.object(
                service, "fts_search", new_callable=AsyncMock
            ) as mock_fts:
                mock_fts.return_value = [fts_result]

                results = await service.hybrid_search(
                    vault_name="vault",
                    query_vector=[0.1],
                    query_text="python",
                    limit=10,
                    alpha=0.5,
                )

        assert len(results) == 2
        # Результаты отсортированы по комбинированному score

    @pytest.mark.asyncio
    async def test_hybrid_with_overlapping_results(self, service):
        """Гибридный поиск с пересекающимися результатами."""
        # Одинаковый chunk в обоих результатах
        common_result = SearchResult(
            chunk_id="chunk_1",
            vault_name="vault",
            file_path="file.md",
            title="Title",
            section="",
            content="Content",
            tags=[],
            score=0.8,
            created_at=None,
            modified_at=datetime.now(),
        )

        with patch.object(
            service, "vector_search", new_callable=AsyncMock
        ) as mock_vector:
            mock_vector.return_value = [common_result]

            with patch.object(
                service, "fts_search", new_callable=AsyncMock
            ) as mock_fts:
                # Тот же chunk с другим score
                fts_result = SearchResult(
                    chunk_id="chunk_1",  # Тот же id
                    vault_name="vault",
                    file_path="file.md",
                    title="Title",
                    section="",
                    content="Content",
                    tags=[],
                    score=0.9,  # Другой score
                    created_at=None,
                    modified_at=datetime.now(),
                )
                mock_fts.return_value = [fts_result]

                results = await service.hybrid_search(
                    vault_name="vault",
                    query_vector=[0.1],
                    query_text="python",
                    limit=10,
                    alpha=0.5,
                )

        # Должен быть только один результат (объединённый)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_hybrid_vector_search_fails(self, service):
        """Гибридный поиск продолжает работу при ошибке vector search."""
        fts_result = SearchResult(
            chunk_id="chunk_1",
            vault_name="vault",
            file_path="file.md",
            title="Title",
            section="",
            content="Content",
            tags=[],
            score=0.7,
            created_at=None,
            modified_at=datetime.now(),
        )

        with patch.object(
            service, "vector_search", new_callable=AsyncMock
        ) as mock_vector:
            mock_vector.side_effect = DatabaseError("Vector search failed")

            with patch.object(
                service, "fts_search", new_callable=AsyncMock
            ) as mock_fts:
                mock_fts.return_value = [fts_result]

                results = await service.hybrid_search(
                    vault_name="vault",
                    query_vector=[0.1],
                    query_text="python",
                )

        # Должны получить только FTS результаты
        assert len(results) == 1
        assert results[0].chunk_id == "chunk_1"


class TestCacheDocumentInfo:
    """Тесты кэширования информации о документах."""

    @pytest.mark.asyncio
    async def test_cache_hit(self, service):
        """Попадание в кэш."""
        cache = service._document_info_cache
        doc_info = {
            "file_path": "file.md",
            "title": "Cached Title",
        }
        cache.set("vault::doc1", doc_info)

        result = await service._get_document_info_cached("vault", "doc1")

        assert result == doc_info

    @pytest.mark.asyncio
    async def test_cache_not_found_marker(self, service):
        """Кэш с маркером "не найден"."""
        cache = service._document_info_cache
        cache.set("vault::doc1", {"__not_found__": True})

        result = await service._get_document_info_cached("vault", "doc1")

        assert result is None
