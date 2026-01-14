"""Общие фикстуры для всех тестов."""

from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from obsidian_kb.db_connection_manager import DBConnectionManager
from obsidian_kb.embedding_service import EmbeddingService
from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.types import DocumentChunk
from obsidian_kb.vault_indexer import VaultIndexer


@pytest.fixture(autouse=True)
def reset_db_connection_manager():
    """Сброс singleton DBConnectionManager перед каждым тестом."""
    DBConnectionManager.reset_instance()
    yield
    DBConnectionManager.reset_instance()


@pytest.fixture
def temp_db(tmp_path):
    """Временная база данных для тестов."""
    return tmp_path / "test_db"


@pytest.fixture
def temp_vault(tmp_path):
    """Временный vault с тестовыми файлами."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    
    # Создаём несколько тестовых markdown файлов
    (vault_path / "file1.md").write_text(
        """---
title: Test File 1
tags: [test, python]
created: 2024-01-01
---

# Test File 1

This is test content about Python programming and async operations.
""",
        encoding="utf-8",
    )
    
    (vault_path / "file2.md").write_text(
        """---
title: Test File 2
tags: [test, database]
---

# Test File 2

Content about databases and vector search.
""",
        encoding="utf-8",
    )
    
    (vault_path / "subdir").mkdir()
    (vault_path / "subdir" / "file3.md").write_text(
        """# Test File 3

More test content here.
""",
        encoding="utf-8",
    )
    
    return vault_path


@pytest.fixture
def temp_vault_advanced(tmp_path):
    """Временный vault с файлами разных типов для расширенного поиска."""
    vault_path = tmp_path / "test_vault"
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
    
    # Файл-договор
    (vault_path / "contract.md").write_text(
        """---
title: Договор
type: договор
created: 2024-06-20
tags: [договор, юридический]
---

# Договор

Содержимое договора.
""",
        encoding="utf-8",
    )
    
    return vault_path


@pytest_asyncio.fixture
async def embedding_service():
    """EmbeddingService с автоматическим закрытием."""
    service = EmbeddingService()
    try:
        yield service
    finally:
        await service.close()


@pytest.fixture
def mock_embedding_service():
    """Мок EmbeddingService для быстрых тестов без реального Ollama."""
    service = AsyncMock(spec=EmbeddingService)
    # Моки должны поддерживать новый параметр embedding_type
    async def mock_get_embedding(text: str, embedding_type: str = "doc"):
        return [0.1] * 768
    async def mock_get_embeddings_batch(texts: list[str], batch_size: int | None = None, embedding_type: str = "doc"):
        return [[0.1] * 768] * len(texts)
    service.get_embedding = AsyncMock(side_effect=mock_get_embedding)
    service.get_embeddings_batch = AsyncMock(side_effect=mock_get_embeddings_batch)
    service.health_check = AsyncMock(return_value=True)
    service.close = AsyncMock()
    return service


@pytest.fixture
def db_manager(temp_db):
    """LanceDBManager с временной БД."""
    return LanceDBManager(db_path=temp_db)


@pytest.fixture
def sample_chunks():
    """Примеры DocumentChunk для тестов (v4)."""
    return [
            DocumentChunk(
                id="test::file1.md::0",
                vault_name="test",
                file_path="file1.md",
                title="Test File 1",
                section="Introduction",
                content="Test content about Python",
                tags=["python", "test"],  # Объединенные теги для обратной совместимости
                frontmatter_tags=["python", "test"],
                inline_tags=[],
                links=["Python", "JavaScript"],
                created_at=datetime(2024, 1, 1),
                modified_at=datetime(2024, 1, 1),
                metadata={"type": "guide"},
                # УДАЛЕНЫ денормализованные поля: author, status, priority, project (v4)
            ),
            DocumentChunk(
                id="test::file2.md::0",
                vault_name="test",
                file_path="file2.md",
                title="Test File 2",
                section="Main",
                content="Test content about async programming",
                tags=["python", "async"],  # Объединенные теги для обратной совместимости
                frontmatter_tags=["python", "async"],
                inline_tags=[],
                links=["async"],
                created_at=datetime(2024, 1, 2),
                modified_at=datetime(2024, 1, 2),
                metadata={"type": "tutorial"},
                # УДАЛЕНЫ денормализованные поля: author, status, priority, project (v4)
            ),
    ]


@pytest.fixture
def sample_embeddings():
    """Примеры embeddings для тестов."""
    return [[0.1] * 768, [0.2] * 768]

