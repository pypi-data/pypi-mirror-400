"""Тесты для IndexingService (storage/indexing/indexing_service.py).

Phase 5: Тестовая инфраструктура v0.7.0
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from obsidian_kb.core.connection_manager import DBConnectionManager
from obsidian_kb.storage.indexing.indexing_service import IndexingService
from obsidian_kb.types import DatabaseError, DocumentChunk, VaultNotFoundError


@pytest.fixture
def mock_connection_manager():
    """Мок DBConnectionManager."""
    mock = MagicMock(spec=DBConnectionManager)
    mock.get_or_create_connection.return_value = MagicMock()
    return mock


@pytest.fixture
def service(mock_connection_manager):
    """IndexingService с моками."""
    return IndexingService(connection_manager=mock_connection_manager)


@pytest.fixture
def sample_chunk():
    """Базовый чанк для тестов."""
    return DocumentChunk(
        id="vault::notes/test.md::0",
        vault_name="vault",
        file_path="notes/test.md",
        title="Test Document",
        section="Introduction",
        content="This is a test content.",
        tags=["python", "testing"],
        frontmatter_tags=["python"],
        inline_tags=["testing"],
        links=["related_note"],
        created_at=datetime(2024, 1, 1, 10, 0, 0),
        modified_at=datetime(2024, 1, 15, 14, 30, 0),
        metadata={"type": "note", "author": "tester"},
    )


@pytest.fixture
def sample_embedding():
    """Базовый embedding для тестов."""
    return [0.1] * 1024


class TestIndexingServiceInit:
    """Тесты инициализации."""

    def test_init(self, mock_connection_manager):
        """Базовая инициализация."""
        service = IndexingService(connection_manager=mock_connection_manager)
        assert service._connection_manager is mock_connection_manager


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

    def test_detects_table_name_as_vault_name(self, service):
        """Определение что передано имя таблицы вместо vault."""
        # Когда передаётся имя таблицы, метод исправляет vault_name и логирует ошибку
        # Результат должен быть корректным именем таблицы
        result = service._get_table_name("vault_test_chunks", "documents")
        # vault_test_chunks -> test (извлечённое vault_name) -> vault_test_documents
        assert result == "vault_test_documents"


class TestSerializeMetadata:
    """Тесты сериализации метаданных."""

    def test_basic_metadata(self, service):
        """Базовая сериализация."""
        metadata = {"title": "Test", "count": 42}
        result = service._serialize_metadata(metadata)
        assert result == {"title": "Test", "count": 42}

    def test_date_serialization(self, service):
        """Сериализация дат."""
        from datetime import date

        metadata = {"created": date(2024, 1, 15)}
        result = service._serialize_metadata(metadata)
        assert result["created"] == "2024-01-15"

    def test_nested_dict(self, service):
        """Вложенный словарь."""
        metadata = {"nested": {"key": "value"}}
        result = service._serialize_metadata(metadata)
        assert result["nested"]["key"] == "value"


class TestDetectContentType:
    """Тесты определения типа контента."""

    def test_markdown(self, service):
        """Markdown файлы."""
        assert service._detect_content_type("file.md") == "markdown"

    def test_pdf(self, service):
        """PDF файлы."""
        assert service._detect_content_type("file.pdf") == "pdf"

    def test_images(self, service):
        """Изображения."""
        assert service._detect_content_type("file.png") == "image"
        assert service._detect_content_type("file.jpg") == "image"
        assert service._detect_content_type("file.jpeg") == "image"
        assert service._detect_content_type("file.gif") == "image"
        assert service._detect_content_type("file.svg") == "image"

    def test_unknown(self, service):
        """Неизвестные типы."""
        assert service._detect_content_type("file.xyz") == "unknown"


class TestNormalizePropertyValue:
    """Тесты нормализации значений свойств."""

    def test_string(self, service):
        """Строковое значение."""
        assert service._normalize_property_value("Hello") == "hello"

    def test_number(self, service):
        """Числовое значение."""
        assert service._normalize_property_value(42) == "42"

    def test_boolean(self, service):
        """Булево значение."""
        assert service._normalize_property_value(True) == "true"
        assert service._normalize_property_value(False) == "false"

    def test_list(self, service):
        """Списочное значение."""
        result = service._normalize_property_value(["A", "B"])
        assert result == "a,b"


class TestGetPropertyType:
    """Тесты определения типа свойства."""

    def test_string(self, service):
        """Строковый тип."""
        assert service._get_property_type("hello") == "string"

    def test_number(self, service):
        """Числовой тип."""
        assert service._get_property_type(42) == "number"

    def test_boolean(self, service):
        """Булев тип."""
        assert service._get_property_type(True) == "boolean"

    def test_list(self, service):
        """Списочный тип."""
        assert service._get_property_type([1, 2, 3]) == "array"


class TestPrepareDocumentRecord:
    """Тесты подготовки записи документа."""

    def test_basic_record(self, service, sample_chunk):
        """Базовая подготовка записи."""
        record = service._prepare_document_record(sample_chunk, "vault")

        assert record["document_id"] == "vault::notes/test.md"
        assert record["vault_name"] == "vault"
        assert record["file_path"] == "notes/test.md"
        assert record["title"] == "Test Document"
        assert record["content_type"] == "markdown"

    def test_with_content_hash(self, service, sample_chunk):
        """Запись с content_hash."""
        record = service._prepare_document_record(
            sample_chunk, "vault", content_hash="abc123"
        )
        assert record["content_hash"] == "abc123"


class TestPrepareChunkRecord:
    """Тесты подготовки записи чанка."""

    def test_basic_record(self, service, sample_chunk, sample_embedding):
        """Базовая подготовка записи."""
        record = service._prepare_chunk_record(
            sample_chunk, sample_embedding, "vault::notes/test.md"
        )

        assert record["chunk_id"] == "vault::notes/test.md::0"
        assert record["document_id"] == "vault::notes/test.md"
        assert record["chunk_index"] == 0
        assert record["content"] == "This is a test content."
        assert record["vector"] == sample_embedding


class TestExtractProperties:
    """Тесты извлечения свойств."""

    def test_basic_properties(self, service, sample_chunk):
        """Базовое извлечение свойств."""
        properties = service._extract_properties(
            sample_chunk, "vault::notes/test.md", "vault"
        )

        keys = [p["property_key"] for p in properties]
        assert "type" in keys
        assert "author" in keys
        # tags не должны быть извлечены
        assert "tags" not in keys

    def test_property_values(self, service, sample_chunk):
        """Значения свойств."""
        properties = service._extract_properties(
            sample_chunk, "vault::notes/test.md", "vault"
        )

        type_prop = next(p for p in properties if p["property_key"] == "type")
        assert type_prop["property_value"] == "note"
        assert type_prop["property_type"] == "string"


class TestGetIndexParams:
    """Тесты параметров индекса."""

    def test_small_table(self, service):
        """Маленькая таблица."""
        partitions, sub_vectors = service._get_index_params(1000)
        assert partitions == 64
        assert sub_vectors == 8

    def test_medium_table(self, service):
        """Средняя таблица."""
        partitions, sub_vectors = service._get_index_params(5000)
        assert partitions == 128
        assert sub_vectors == 12

    def test_large_table(self, service):
        """Большая таблица."""
        partitions, sub_vectors = service._get_index_params(50000)
        assert partitions == 256
        assert sub_vectors == 16


class TestUpsertChunks:
    """Тесты добавления/обновления чанков."""

    @pytest.mark.asyncio
    async def test_mismatched_lengths_raises(self, service, sample_chunk):
        """Несоответствие количества чанков и embeddings."""
        with pytest.raises(ValueError) as exc_info:
            await service.upsert_chunks(
                vault_name="vault",
                chunks=[sample_chunk],
                embeddings=[[0.1], [0.2]],  # Два embedding на один chunk
            )

        assert "!=" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_chunks(self, service):
        """Пустой список чанков."""
        # Не должно вызвать ошибку
        await service.upsert_chunks(
            vault_name="vault",
            chunks=[],
            embeddings=[],
        )


class TestDeleteFile:
    """Тесты удаления файла."""

    @pytest.mark.asyncio
    async def test_basic_delete(self, service):
        """Базовое удаление файла."""
        mock_table = MagicMock()
        mock_table.delete = MagicMock()

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            await service.delete_file("vault", "notes/test.md")

        # Проверяем что delete был вызван для каждой таблицы
        assert mock_table.delete.call_count >= 1


class TestDeleteVault:
    """Тесты удаления vault."""

    @pytest.mark.asyncio
    async def test_basic_delete(self, service, mock_connection_manager):
        """Базовое удаление vault."""
        mock_db = MagicMock()
        mock_db.drop_table = MagicMock()
        mock_connection_manager.get_or_create_connection.return_value = mock_db

        await service.delete_vault("test_vault")

        # Проверяем что drop_table был вызван для каждого типа таблицы
        assert mock_db.drop_table.call_count == 4  # 4 типа таблиц


class TestGetRowCount:
    """Тесты подсчёта строк."""

    @pytest.mark.asyncio
    async def test_count_rows(self, service):
        """Использование count_rows()."""
        mock_table = MagicMock()
        mock_table.count_rows.return_value = 100

        result = await service._get_row_count(mock_table)

        assert result == 100
        mock_table.count_rows.assert_called_once()


class TestSpecialCharactersInPaths:
    """Тесты для путей со спецсимволами (апострофы, кавычки и т.д.).

    Эти тесты проверяют правильность экранирования document_id
    при DELETE операциях, что критически важно для путей вроде
    "John's Notes/meeting.md".
    """

    @pytest.fixture
    def chunk_with_apostrophe(self):
        """Чанк с апострофом в пути файла."""
        return DocumentChunk(
            id="vault::John's Notes/meeting.md::0",
            vault_name="vault",
            file_path="John's Notes/meeting.md",
            title="John's Meeting",
            section="Notes",
            content="Meeting content with John's notes.",
            tags=["meeting"],
            frontmatter_tags=["meeting"],
            inline_tags=[],
            links=[],
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            modified_at=datetime(2024, 1, 15, 14, 30, 0),
            metadata={},
        )

    @pytest.fixture
    def sample_embedding(self):
        """Базовый embedding для тестов."""
        return [0.1] * 1024

    @pytest.mark.asyncio
    async def test_upsert_with_apostrophe_in_path(
        self, service, chunk_with_apostrophe, sample_embedding
    ):
        """Тест upsert с апострофом в пути файла.

        Проверяет, что document_id правильно экранируется при DELETE
        операции перед добавлением новых данных.
        """
        mock_table = MagicMock()
        mock_table.delete = MagicMock()
        mock_table.add = MagicMock()
        mock_table.count_rows.return_value = 1
        mock_table.name = "vault_vault_chunks"

        with (
            patch.object(
                service, "_ensure_table", new_callable=AsyncMock
            ) as mock_ensure,
            patch.object(
                service, "_create_vector_index", new_callable=AsyncMock
            ),
            patch.object(
                service, "_create_fts_index", new_callable=AsyncMock
            ),
            patch.object(
                service, "_create_metadata_indexes", new_callable=AsyncMock
            ),
            patch.object(
                service, "_create_documents_indexes", new_callable=AsyncMock
            ),
            patch.object(
                service, "_create_properties_indexes", new_callable=AsyncMock
            ),
        ):
            mock_ensure.return_value = mock_table

            # Это должно работать без исключений
            await service.upsert_chunks(
                "vault", [chunk_with_apostrophe], [sample_embedding]
            )

        # Проверяем что delete был вызван с экранированным document_id
        delete_calls = mock_table.delete.call_args_list
        assert len(delete_calls) >= 1

        # Проверяем, что апостроф экранирован ('' вместо ')
        for call in delete_calls:
            where_clause = call[0][0]
            # document_id = "vault::John's Notes/meeting.md"
            # должен быть экранирован как "vault::John''s Notes/meeting.md"
            assert "John''s" in where_clause, (
                f"Апостроф должен быть экранирован в WHERE: {where_clause}"
            )

    @pytest.mark.asyncio
    async def test_delete_file_with_apostrophe(self, service):
        """Тест удаления файла с апострофом в пути.

        Проверяет, что document_id правильно экранируется при DELETE.
        """
        mock_table = MagicMock()
        mock_table.delete = MagicMock()

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            await service.delete_file("vault", "John's Notes/meeting.md")

        # Проверяем что delete был вызван с экранированным document_id
        delete_calls = mock_table.delete.call_args_list
        assert len(delete_calls) >= 1

        for call in delete_calls:
            where_clause = call[0][0]
            # Апостроф должен быть экранирован
            assert "John''s" in where_clause, (
                f"Апостроф должен быть экранирован: {where_clause}"
            )

    @pytest.mark.asyncio
    async def test_delete_file_with_double_quotes(self, service):
        """Тест удаления файла с двойными кавычками в пути."""
        mock_table = MagicMock()
        mock_table.delete = MagicMock()

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            # Двойные кавычки не требуют экранирования в SQL с одинарными кавычками
            await service.delete_file("vault", 'Note "Important".md')

        delete_calls = mock_table.delete.call_args_list
        assert len(delete_calls) >= 1

    @pytest.mark.asyncio
    async def test_delete_file_with_multiple_apostrophes(self, service):
        """Тест удаления файла с несколькими апострофами."""
        mock_table = MagicMock()
        mock_table.delete = MagicMock()

        with patch.object(
            service, "_ensure_table", new_callable=AsyncMock
        ) as mock_ensure:
            mock_ensure.return_value = mock_table

            await service.delete_file("vault", "It's John's Note's.md")

        delete_calls = mock_table.delete.call_args_list
        assert len(delete_calls) >= 1

        for call in delete_calls:
            where_clause = call[0][0]
            # Все три апострофа должны быть экранированы
            assert where_clause.count("''") == 3, (
                f"Все апострофы должны быть экранированы: {where_clause}"
            )
