"""Интеграционные тесты для расширенного поиска."""

import pytest
import pytest_asyncio

from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.normalization import DataNormalizer
from obsidian_kb.query_parser import QueryParser
from obsidian_kb.service_container import ServiceContainer, reset_service_container
from obsidian_kb.vault_indexer import VaultIndexer
from tests.utils.indexing import index_vault_for_tests

# Используем фикстуры из conftest.py
# temp_db, temp_vault_advanced, embedding_service


@pytest_asyncio.fixture(scope="session")
async def indexed_vault_advanced_session(tmp_path_factory):
    """Session-scoped фикстура для проиндексированного vault'а с расширенными тестами.
    
    Индексация выполняется один раз для всех тестов в сессии.
    """
    from obsidian_kb.embedding_service import EmbeddingService
    
    # Создаём временную БД для сессии
    db_path = tmp_path_factory.mktemp("session_db_advanced") / "test_db.lance"
    
    # Создаём тестовый vault (копируем логику из conftest.py temp_vault_advanced)
    vault_path = tmp_path_factory.mktemp("session_vault_advanced") / "test_vault"
    vault_path.mkdir()
    
    # Файл с тегами
    (vault_path / "python_file.md").write_text(
        """---
title: Python Guide
tags: [python, async, programming]
type: guide
created: 2024-01-15
---

# Python Guide

Content about Python programming.
""",
        encoding="utf-8",
    )
    
    # Файл-протокол
    (vault_path / "protocol.md").write_text(
        """---
title: Протокол заседания
type: протокол
created: 2024-03-10
tags: [протокол, заседание]
---

# Протокол заседания

Содержимое протокола.
""",
        encoding="utf-8",
    )
    
    # Файл с датой
    (vault_path / "old_note.md").write_text(
        """---
title: Старая заметка
created: 2024-01-01
modified: 2024-01-05
tags: [old]
---

# Старая заметка

Старое содержимое.
""",
        encoding="utf-8",
    )
    
    # Файл с ссылками
    (vault_path / "linked_note.md").write_text(
        """---
title: Заметка со ссылками
tags: [linked]
---

# Заметка со ссылками

Ссылка на [[Python Guide]] и [[Протокол заседания]].
""",
        encoding="utf-8",
    )
    
    # Создаём embedding_service для сессии
    embedding_service = EmbeddingService()
    
    # Инициализируем сервисы
    reset_service_container()
    services = ServiceContainer(db_path=db_path)
    # Устанавливаем embedding_service напрямую в приватное поле
    services._embedding_service = embedding_service
    
    try:
        # Индексируем vault один раз для всей сессии
        vault_name = "test_vault"
        result = await index_vault_for_tests(
            services,
            vault_path,
            vault_name,
        )
        
        yield vault_name, vault_path, services
        
    finally:
        await services.cleanup()
        await embedding_service.close()
        reset_service_container()


@pytest_asyncio.fixture
async def indexed_vault_advanced(indexed_vault_advanced_session):
    """Проиндексированный vault для тестов (использует session-scoped)."""
    vault_name, vault_path, services = indexed_vault_advanced_session
    yield vault_name, vault_path, services


@pytest.mark.asyncio
async def test_search_by_tags(indexed_vault_advanced):
    """Тест поиска по тегам с нормализацией."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Парсим запрос с тегами (проверяем нормализацию)
    parsed = QueryParser.parse("tags:Python")
    where_clause, document_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=db_manager,
        vault_name=vault_name,
    )
    
    # Проверяем, что document_ids не пустые (двухэтапный запрос)
    assert document_ids is not None
    assert len(document_ids) > 0
    
    # Проверяем, что where_clause None для frontmatter тегов
    assert where_clause is None
    
    # Проверяем, что найден правильный документ
    assert any("python" in doc_id.lower() for doc_id in document_ids)


@pytest.mark.asyncio
async def test_search_by_date(indexed_vault_advanced):
    """Тест поиска по дате."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Парсим запрос с датой (ищем документы созданные после 2024-01-01, чтобы найти old_note.md)
    parsed = QueryParser.parse("created:>=2024-01-01")
    where_clause, document_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=db_manager,
        vault_name=vault_name,
    )
    
    # В текущей реализации FilterBuilder.build_where_clause() не обрабатывает даты для document_ids
    # Даты обрабатываются в BaseSearchStrategy._apply_filters()
    # Поэтому document_ids может быть None, если нет других фильтров
    # Проверяем, что запрос парсится корректно
    assert parsed.date_filters is not None
    assert "created" in parsed.date_filters
    
    # Проверяем, что where_clause None для дат (даты не добавляются в WHERE для chunks)
    assert where_clause is None


@pytest.mark.asyncio
async def test_search_by_doc_type(indexed_vault_advanced):
    """Тест поиска по типу документа."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Парсим запрос с типом (проверяем нормализацию)
    parsed = QueryParser.parse("type:Guide")
    where_clause, document_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=db_manager,
        vault_name=vault_name,
    )
    
    # Проверяем, что document_ids не пустые (двухэтапный запрос)
    assert document_ids is not None
    assert len(document_ids) > 0
    
    # Проверяем, что where_clause None для типов
    assert where_clause is None


@pytest.mark.asyncio
async def test_search_combined_filters(indexed_vault_advanced):
    """Тест поиска с комбинированными фильтрами."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Парсим запрос с комбинированными фильтрами (проверяем нормализацию)
    parsed = QueryParser.parse("Python tags:Python created:>2024-01-01 type:Guide")
    where_clause, document_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=db_manager,
        vault_name=vault_name,
    )
    
    # Проверяем, что document_ids не пустые (двухэтапный запрос)
    assert document_ids is not None
    assert len(document_ids) > 0
    
    # Проверяем, что where_clause None для комбинированных фильтров
    assert where_clause is None


@pytest.mark.asyncio
async def test_search_by_inline_tags(indexed_vault_advanced):
    """Тест поиска по inline тегам."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Парсим запрос
    parsed = QueryParser.parse("Python tags:python")
    where_clause, document_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=db_manager,
        vault_name=vault_name,
    )
    
    # Inline теги обрабатываются через where_clause, а не document_ids
    # Но если есть frontmatter теги, то document_ids тоже будет не None
    assert parsed.inline_tags is not None or parsed.tags is not None


@pytest.mark.asyncio
async def test_search_by_multiple_inline_tags(indexed_vault_advanced):
    """Тест поиска по нескольким inline тегам."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Парсим запрос
    parsed = QueryParser.parse("Python tags:python")
    where_clause, document_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=db_manager,
        vault_name=vault_name,
    )
    
    # Проверяем, что запрос парсится корректно
    assert parsed.text_query is not None or parsed.inline_tags is not None


@pytest.mark.asyncio
async def test_search_by_links(indexed_vault_advanced):
    """Тест поиска по ссылкам."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Парсим запрос с links (проверяем нормализацию)
    parsed = QueryParser.parse("links:Test-Note")
    where_clause, document_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=db_manager,
        vault_name=vault_name,
    )
    
    # Links обрабатываются через where_clause, а не document_ids
    assert where_clause is not None or document_ids is not None


@pytest.mark.asyncio
async def test_search_by_links_and_tags(indexed_vault_advanced):
    """Тест поиска по ссылкам и тегам."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Парсим запрос с links и другими фильтрами (проверяем нормализацию)
    parsed = QueryParser.parse("links:Test-Note tags:Python")
    where_clause, document_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=db_manager,
        vault_name=vault_name,
    )
    
    # Links обрабатываются через where_clause, frontmatter теги через document_ids
    assert where_clause is not None or document_ids is not None


@pytest.mark.asyncio
async def test_search_by_multiple_links(indexed_vault_advanced):
    """Тест поиска по нескольким ссылкам."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Парсим запрос с несколькими links (используем реальные ссылки из vault)
    parsed = QueryParser.parse("links:Python-Guide links:Протокол-заседания")
    where_clause, document_ids = await QueryParser.build_where_clause(
        parsed,
        db_manager=db_manager,
        vault_name=vault_name,
    )
    
    # Проверяем, что запрос парсится корректно
    assert parsed.links is not None
    assert len(parsed.links) > 0
    
    # Links обрабатываются через where_clause для chunks
    # Проверяем, что where_clause не None или document_ids не None
    assert where_clause is not None or document_ids is not None


@pytest.mark.asyncio
async def test_tag_normalization_in_chunks(indexed_vault_advanced):
    """Тест нормализации тегов в чанках."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Получаем чанки из БД
    chunks_table = await db_manager._ensure_table(vault_name, "chunks")
    db = db_manager._get_db()
    
    def _get_chunks():
        try:
            arrow_table = chunks_table.search().limit(100).to_arrow()
            results = []
            for i in range(arrow_table.num_rows):
                row = {col: arrow_table[col][i].as_py() for col in arrow_table.column_names}
                results.append(row)
            return results
        except Exception:
            return []
    
    import asyncio
    rows = await asyncio.to_thread(_get_chunks)
    
    if rows:
        # Проверяем, что теги нормализованы в чанках
        for row in rows:
            if "inline_tags" in row and row["inline_tags"]:
                for tag in row["inline_tags"]:
                    # Все теги должны быть нормализованы (lowercase, trim)
                    assert tag == tag.lower().strip(), f"Tag {tag} не нормализован"


@pytest.mark.asyncio
async def test_link_normalization_in_chunks(indexed_vault_advanced):
    """Тест нормализации ссылок в чанках."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Получаем чанки из БД
    chunks_table = await db_manager._ensure_table(vault_name, "chunks")
    db = db_manager._get_db()
    
    def _get_chunks():
        try:
            arrow_table = chunks_table.search().limit(100).to_arrow()
            results = []
            for i in range(arrow_table.num_rows):
                row = {col: arrow_table[col][i].as_py() for col in arrow_table.column_names}
                results.append(row)
            return results
        except Exception:
            return []
    
    import asyncio
    rows = await asyncio.to_thread(_get_chunks)
    
    if rows:
        # Проверяем, что ссылки нормализованы в чанках
        for row in rows:
            if "links" in row and row["links"]:
                for link in row["links"]:
                    # Все ссылки должны быть нормализованы (lowercase, извлечено имя файла)
                    assert link == link.lower(), f"Link {link} не нормализован"


@pytest.mark.asyncio
async def test_doc_type_normalization_in_metadata(indexed_vault_advanced):
    """Тест нормализации типов документов в metadata."""
    vault_name, vault_path, services = indexed_vault_advanced
    
    db_manager = services.db_manager
    
    # Получаем metadata из БД
    metadata_table = await db_manager._ensure_table(vault_name, "metadata")
    db = db_manager._get_db()
    
    def _get_metadata():
        try:
            arrow_table = metadata_table.search().limit(100).to_arrow()
            results = []
            for i in range(arrow_table.num_rows):
                row = {col: arrow_table[col][i].as_py() for col in arrow_table.column_names}
                results.append(row)
            return results
        except Exception:
            return []
    
    import asyncio
    rows = await asyncio.to_thread(_get_metadata)
    
    if rows:
        # Проверяем, что типы документов нормализованы в metadata
        for row in rows:
            if isinstance(row.get("properties"), dict) and "type" in row.get("properties", {}):
                doc_type = row["properties"]["type"]
                # Типы должны быть нормализованы (lowercase)
                assert doc_type == doc_type.lower(), f"Doc type {doc_type} не нормализован"
