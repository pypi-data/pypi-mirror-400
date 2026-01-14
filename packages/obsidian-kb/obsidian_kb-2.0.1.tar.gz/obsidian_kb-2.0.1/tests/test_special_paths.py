"""Тесты для путей с пробелами, кириллицей и спецсимволами.

Проверяют корректную работу с путями, содержащими:
- Пробелы: "/path/to/My Vault/"
- Кириллицу: "/path/to/Мой Vault/"
- Скобки: "/path/to/test(1)/"
- Апострофы: "/path/to/John's Notes/"
"""

import pytest
from pathlib import Path

from obsidian_kb.vault_indexer import VaultIndexer
from obsidian_kb.types import IndexingError


class TestVaultPathWithSpaces:
    """Тесты для vault'ов с пробелами в пути."""

    @pytest.fixture
    def vault_with_spaces(self, tmp_path):
        """Vault с пробелами в названии директории."""
        vault_path = tmp_path / "My Vault Name"
        vault_path.mkdir()

        # Создаём файл с обычным именем
        (vault_path / "file1.md").write_text(
            """---
title: Test File
tags: [test]
---

# Test File

Content here.
""",
            encoding="utf-8",
        )

        # Создаём файл с пробелом в имени
        (vault_path / "my file.md").write_text(
            """---
title: My File
---

# My File

Content with spaces in filename.
""",
            encoding="utf-8",
        )

        # Создаём поддиректорию с пробелом
        subdir = vault_path / "My Folder"
        subdir.mkdir()
        (subdir / "nested file.md").write_text(
            """# Nested File

Nested content.
""",
            encoding="utf-8",
        )

        return vault_path

    @pytest.mark.asyncio
    async def test_scan_vault_with_spaces_in_path(self, vault_with_spaces):
        """Тест сканирования vault'а с пробелами в пути."""
        indexer = VaultIndexer(vault_with_spaces, "test-vault")
        chunks = await indexer.scan_all()

        assert len(chunks) >= 3, f"Expected at least 3 chunks, got {len(chunks)}"

        # Проверяем, что все файлы были просканированы
        file_paths = {chunk.file_path for chunk in chunks}
        assert "file1.md" in file_paths or any("file1.md" in fp for fp in file_paths)
        assert "my file.md" in file_paths or any("my file.md" in fp for fp in file_paths)

    @pytest.mark.asyncio
    async def test_scan_single_file_with_spaces(self, vault_with_spaces):
        """Тест сканирования отдельного файла с пробелами в имени."""
        indexer = VaultIndexer(vault_with_spaces, "test-vault")

        file_path = vault_with_spaces / "my file.md"
        chunks = await indexer.scan_file(file_path)

        assert len(chunks) > 0
        assert chunks[0].title == "My File"

    @pytest.mark.asyncio
    async def test_scan_nested_file_with_spaces(self, vault_with_spaces):
        """Тест сканирования вложенного файла с пробелами в пути."""
        indexer = VaultIndexer(vault_with_spaces, "test-vault")

        file_path = vault_with_spaces / "My Folder" / "nested file.md"
        chunks = await indexer.scan_file(file_path)

        assert len(chunks) > 0
        assert "nested" in chunks[0].content.lower()


class TestVaultPathWithCyrillic:
    """Тесты для vault'ов с кириллицей в пути."""

    @pytest.fixture
    def vault_with_cyrillic(self, tmp_path):
        """Vault с кириллицей в названии."""
        vault_path = tmp_path / "Мой Vault"
        vault_path.mkdir()

        # Файл с кириллическим именем
        (vault_path / "Заметка.md").write_text(
            """---
title: Заметка
tags: [тест, кириллица]
---

# Заметка

Содержимое на русском языке.
""",
            encoding="utf-8",
        )

        # Поддиректория с кириллицей
        subdir = vault_path / "Папка проекта"
        subdir.mkdir()
        (subdir / "Протокол встречи.md").write_text(
            """---
title: Протокол встречи
---

# Протокол встречи

Содержимое протокола.
""",
            encoding="utf-8",
        )

        return vault_path

    @pytest.mark.asyncio
    async def test_scan_vault_with_cyrillic_path(self, vault_with_cyrillic):
        """Тест сканирования vault'а с кириллицей в пути."""
        indexer = VaultIndexer(vault_with_cyrillic, "test-vault")
        chunks = await indexer.scan_all()

        assert len(chunks) >= 2

        # Проверяем кириллический контент
        titles = {chunk.title for chunk in chunks}
        assert "Заметка" in titles or any("Заметка" in t for t in titles)

    @pytest.mark.asyncio
    async def test_scan_cyrillic_filename(self, vault_with_cyrillic):
        """Тест сканирования файла с кириллическим именем."""
        indexer = VaultIndexer(vault_with_cyrillic, "test-vault")

        file_path = vault_with_cyrillic / "Заметка.md"
        chunks = await indexer.scan_file(file_path)

        assert len(chunks) > 0
        assert chunks[0].title == "Заметка"
        assert "тест" in chunks[0].tags or "кириллица" in chunks[0].tags


class TestVaultPathWithSpecialChars:
    """Тесты для vault'ов со спецсимволами в пути."""

    @pytest.fixture
    def vault_with_parentheses(self, tmp_path):
        """Vault со скобками в названии."""
        vault_path = tmp_path / "test(1)"
        vault_path.mkdir()

        (vault_path / "file(draft).md").write_text(
            """---
title: Draft Document
---

# Draft Document

Content.
""",
            encoding="utf-8",
        )

        return vault_path

    @pytest.fixture
    def vault_with_apostrophe(self, tmp_path):
        """Vault с апострофом в названии."""
        vault_path = tmp_path / "John's Notes"
        vault_path.mkdir()

        (vault_path / "John's Meeting.md").write_text(
            """---
title: John's Meeting
---

# John's Meeting

Notes from John's meeting.
""",
            encoding="utf-8",
        )

        return vault_path

    @pytest.mark.asyncio
    async def test_scan_vault_with_parentheses(self, vault_with_parentheses):
        """Тест сканирования vault'а со скобками в пути."""
        indexer = VaultIndexer(vault_with_parentheses, "test-vault")
        chunks = await indexer.scan_all()

        assert len(chunks) >= 1
        assert chunks[0].title == "Draft Document"

    @pytest.mark.asyncio
    async def test_scan_vault_with_apostrophe(self, vault_with_apostrophe):
        """Тест сканирования vault'а с апострофом в пути."""
        indexer = VaultIndexer(vault_with_apostrophe, "test-vault")
        chunks = await indexer.scan_all()

        assert len(chunks) >= 1
        assert chunks[0].title == "John's Meeting"


class TestVaultPathEdgeCases:
    """Дополнительные тесты для крайних случаев путей."""

    @pytest.fixture
    def vault_complex_path(self, tmp_path):
        """Vault со сложным путём: пробелы + кириллица + спецсимволы."""
        vault_path = tmp_path / "My Vault (Проект 1)"
        vault_path.mkdir()

        # Файл со сложным именем
        (vault_path / "Встреча (Draft) - копия.md").write_text(
            """---
title: Встреча Draft
tags: [встреча, draft]
---

# Встреча (Draft)

Содержимое встречи.
""",
            encoding="utf-8",
        )

        return vault_path

    @pytest.mark.asyncio
    async def test_scan_vault_complex_path(self, vault_complex_path):
        """Тест сканирования vault'а со сложным путём."""
        indexer = VaultIndexer(vault_complex_path, "test-vault")
        chunks = await indexer.scan_all()

        assert len(chunks) >= 1
        # Проверяем, что файл был корректно просканирован
        assert any("Встреча" in chunk.title or "Draft" in chunk.title for chunk in chunks)

    @pytest.mark.asyncio
    async def test_vault_path_normalization(self, tmp_path):
        """Тест нормализации путей с пробелами."""
        vault_path = tmp_path / "Test Vault"
        vault_path.mkdir()

        (vault_path / "test.md").write_text("# Test\n\nContent.", encoding="utf-8")

        # Инициализируем с Path объектом
        indexer1 = VaultIndexer(vault_path, "test-vault")

        # Инициализируем со строкой
        indexer2 = VaultIndexer(str(vault_path), "test-vault")

        chunks1 = await indexer1.scan_all()
        chunks2 = await indexer2.scan_all()

        assert len(chunks1) == len(chunks2)
        assert len(chunks1) > 0

    @pytest.mark.asyncio
    async def test_relative_path_in_chunks(self, tmp_path):
        """Тест что file_path в чанках содержит относительный путь."""
        vault_path = tmp_path / "My Vault"
        vault_path.mkdir()

        subdir = vault_path / "Folder With Spaces"
        subdir.mkdir()

        (subdir / "File With Spaces.md").write_text(
            "# Test\n\nContent.",
            encoding="utf-8",
        )

        indexer = VaultIndexer(vault_path, "test-vault")
        chunks = await indexer.scan_all()

        assert len(chunks) > 0

        # file_path должен быть относительным путём
        for chunk in chunks:
            assert not Path(chunk.file_path).is_absolute(), \
                f"file_path должен быть относительным: {chunk.file_path}"
            # Проверяем, что путь содержит директорию с пробелом
            assert "Folder With Spaces" in chunk.file_path


class TestOrchestratorWithSpecialPaths:
    """Тесты для IndexingOrchestrator с путями со спецсимволами."""

    @pytest.fixture
    def vault_with_spaces_for_orchestrator(self, tmp_path):
        """Vault с пробелами для тестов orchestrator."""
        vault_path = tmp_path / "Naumen CTO"
        vault_path.mkdir()

        inbox = vault_path / "00 Inbox"
        inbox.mkdir()

        (inbox / "inbox.md").write_text(
            """---
title: Inbox
tags: [inbox]
---

# Inbox

Inbox content.
""",
            encoding="utf-8",
        )

        (inbox / "Встреча по целям.md").write_text(
            """---
title: Встреча по целям
tags: [meeting]
---

# Встреча по целям

Meeting notes.
""",
            encoding="utf-8",
        )

        return vault_path

    @pytest.mark.asyncio
    async def test_indexing_job_has_vault_path(
        self, vault_with_spaces_for_orchestrator, tmp_path
    ):
        """Тест что IndexingJob хранит vault_path."""
        from obsidian_kb.indexing.orchestrator import (
            EnrichmentStrategy,
            IndexingJob,
        )

        vault_path = vault_with_spaces_for_orchestrator

        # Создаём job напрямую
        job = IndexingJob(
            id="test-job",
            vault_name="naumen-cto",
            vault_path=vault_path,
            paths=[
                Path("00 Inbox/inbox.md"),
                Path("00 Inbox/Встреча по целям.md"),
            ],
            enrichment=EnrichmentStrategy.NONE,
            status="pending",
            progress=0.0,
            documents_total=2,
            documents_processed=0,
        )

        # Проверяем, что vault_path сохранён
        assert job.vault_path == vault_path
        assert job.vault_name == "naumen-cto"
        assert len(job.paths) == 2

    @pytest.mark.asyncio
    async def test_full_paths_can_be_built(
        self, vault_with_spaces_for_orchestrator, tmp_path
    ):
        """Тест что полные пути можно построить из vault_path + relative_path."""
        from obsidian_kb.indexing.orchestrator import (
            EnrichmentStrategy,
            IndexingJob,
        )

        vault_path = vault_with_spaces_for_orchestrator

        # Создаём job вручную с относительными путями
        job = IndexingJob(
            id="test-job",
            vault_name="naumen-cto",
            vault_path=vault_path,
            paths=[
                Path("00 Inbox/inbox.md"),
                Path("00 Inbox/Встреча по целям.md"),
            ],
            enrichment=EnrichmentStrategy.NONE,
            status="pending",
            progress=0.0,
            documents_total=2,
            documents_processed=0,
        )

        # Проверяем, что полные пути можно построить и файлы существуют
        for rel_path in job.paths:
            full_path = job.vault_path / rel_path
            assert full_path.exists(), f"File not found: {full_path}"

        # Проверяем, что файлы можно прочитать через pathlib
        for rel_path in job.paths:
            full_path = job.vault_path / rel_path
            content = full_path.read_text(encoding="utf-8")
            assert len(content) > 0, f"Empty file: {full_path}"


class TestFileParserWithSpecialPaths:
    """Тесты для file_parsers с путями со спецсимволами."""

    @pytest.mark.asyncio
    async def test_read_markdown_with_spaces(self, tmp_path):
        """Тест чтения markdown файла с пробелами в пути."""
        from obsidian_kb.file_parsers import extract_text_from_file

        file_dir = tmp_path / "Test Folder"
        file_dir.mkdir()

        file_path = file_dir / "test file.md"
        file_path.write_text("# Test\n\nContent here.", encoding="utf-8")

        content = extract_text_from_file(file_path)

        assert content is not None
        assert "# Test" in content
        assert "Content here" in content

    @pytest.mark.asyncio
    async def test_read_markdown_with_cyrillic(self, tmp_path):
        """Тест чтения markdown файла с кириллицей в пути."""
        from obsidian_kb.file_parsers import extract_text_from_file

        file_dir = tmp_path / "Тестовая папка"
        file_dir.mkdir()

        file_path = file_dir / "тест.md"
        file_path.write_text("# Тест\n\nСодержимое.", encoding="utf-8")

        content = extract_text_from_file(file_path)

        assert content is not None
        assert "# Тест" in content
        assert "Содержимое" in content
