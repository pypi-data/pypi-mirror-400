"""Common test fixtures and factories.

This module provides factories for creating test data objects
with sensible defaults.

Usage:
    from tests.helpers.fixtures import ChunkFactory, VaultFactory

    chunk = ChunkFactory.create(content="Test content")
    chunks = ChunkFactory.create_batch(5, vault_name="my_vault")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ChunkFactory:
    """Factory for creating DocumentChunk test objects."""

    _counter: int = field(default=0, init=False, repr=False)

    @classmethod
    def create(
        cls,
        *,
        vault_name: str = "test_vault",
        file_path: str | None = None,
        title: str | None = None,
        section: str = "Main",
        content: str = "Test content",
        tags: list[str] | None = None,
        links: list[str] | None = None,
        created_at: datetime | None = None,
        modified_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        chunk_index: int = 0,
    ) -> "DocumentChunk":
        """Create a single DocumentChunk with defaults.

        Args:
            vault_name: Name of the vault
            file_path: Path to file (auto-generated if None)
            title: Document title (derived from file_path if None)
            section: Section name
            content: Chunk content
            tags: List of tags
            links: List of links
            created_at: Creation timestamp
            modified_at: Modification timestamp
            metadata: Additional metadata
            chunk_index: Index of chunk within document

        Returns:
            DocumentChunk instance
        """
        from obsidian_kb.types import DocumentChunk

        cls._counter = getattr(cls, "_counter", 0) + 1

        if file_path is None:
            file_path = f"file{cls._counter}.md"

        if title is None:
            title = f"Test Document {cls._counter}"

        chunk_id = f"{vault_name}::{file_path}::{chunk_index}"

        return DocumentChunk(
            id=chunk_id,
            vault_name=vault_name,
            file_path=file_path,
            title=title,
            section=section,
            content=content,
            tags=tags or [],
            frontmatter_tags=tags or [],
            inline_tags=[],
            links=links or [],
            created_at=created_at or datetime(2024, 1, 1, 10, 0, 0),
            modified_at=modified_at or datetime(2024, 1, 1, 12, 0, 0),
            metadata=metadata or {},
        )

    @classmethod
    def create_batch(
        cls,
        count: int,
        *,
        vault_name: str = "test_vault",
        content_prefix: str = "Content for chunk",
        **kwargs: Any,
    ) -> list["DocumentChunk"]:
        """Create multiple DocumentChunks.

        Args:
            count: Number of chunks to create
            vault_name: Name of the vault
            content_prefix: Prefix for content (index appended)
            **kwargs: Additional arguments passed to create()

        Returns:
            List of DocumentChunk instances
        """
        chunks = []
        for i in range(count):
            chunks.append(
                cls.create(
                    vault_name=vault_name,
                    content=f"{content_prefix} {i}",
                    file_path=f"file{i}.md",
                    title=f"Document {i}",
                    chunk_index=0,
                    **kwargs,
                )
            )
        return chunks


@dataclass
class VaultFactory:
    """Factory for creating test vault directories."""

    @staticmethod
    def create(
        tmp_path: Path,
        name: str = "test_vault",
        files: dict[str, str] | None = None,
    ) -> Path:
        """Create a test vault directory with files.

        Args:
            tmp_path: Temporary directory path
            name: Vault name
            files: Dict of {filename: content} for files to create

        Returns:
            Path to created vault directory
        """
        vault_path = tmp_path / name
        vault_path.mkdir(parents=True, exist_ok=True)

        if files is None:
            # Create default test files
            files = {
                "file1.md": """---
title: Test File 1
tags: [test, python]
---

# Test File 1

This is test content about Python programming.
""",
                "file2.md": """---
title: Test File 2
tags: [test, database]
---

# Test File 2

Content about databases and vector search.
""",
            }

        for filename, content in files.items():
            file_path = vault_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

        return vault_path

    @staticmethod
    def create_with_subdirs(
        tmp_path: Path,
        name: str = "test_vault",
    ) -> Path:
        """Create a test vault with subdirectories.

        Args:
            tmp_path: Temporary directory path
            name: Vault name

        Returns:
            Path to created vault directory
        """
        files = {
            "root.md": "# Root file\n\nContent in root.",
            "subdir/nested.md": "# Nested file\n\nContent in subdirectory.",
            "subdir/deep/deeper.md": "# Deep file\n\nDeep nested content.",
        }
        return VaultFactory.create(tmp_path, name, files)


@dataclass
class SearchResultFactory:
    """Factory for creating SearchResult test objects."""

    @classmethod
    def create(
        cls,
        *,
        vault_name: str = "test_vault",
        file_path: str = "file1.md",
        title: str = "Test Document",
        content: str = "Test content",
        score: float = 0.9,
        tags: list[str] | None = None,
    ) -> "SearchResult":
        """Create a SearchResult instance.

        Args:
            vault_name: Name of the vault
            file_path: Path to file
            title: Document title
            content: Result content
            score: Relevance score
            tags: List of tags

        Returns:
            SearchResult instance
        """
        from obsidian_kb.types import SearchResult

        return SearchResult(
            chunk_id=f"{vault_name}::{file_path}::0",
            vault_name=vault_name,
            file_path=file_path,
            title=title,
            section="Main",
            content=content,
            tags=tags or [],
            score=score,
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            modified_at=datetime(2024, 1, 1, 12, 0, 0),
        )

    @classmethod
    def create_batch(
        cls,
        count: int,
        *,
        vault_name: str = "test_vault",
        base_score: float = 0.9,
        score_step: float = 0.05,
        **kwargs: Any,
    ) -> list["SearchResult"]:
        """Create multiple SearchResult instances.

        Args:
            count: Number of results to create
            vault_name: Name of the vault
            base_score: Starting score
            score_step: Score decrease per result
            **kwargs: Additional arguments passed to create()

        Returns:
            List of SearchResult instances
        """
        results = []
        for i in range(count):
            results.append(
                cls.create(
                    vault_name=vault_name,
                    file_path=f"file{i}.md",
                    title=f"Document {i}",
                    content=f"Content for result {i}",
                    score=base_score - (i * score_step),
                    **kwargs,
                )
            )
        return results


def mock_embeddings(count: int, dim: int = 768) -> list[list[float]]:
    """Generate mock embeddings.

    Args:
        count: Number of embeddings to generate
        dim: Embedding dimension

    Returns:
        List of mock embedding vectors
    """
    return [[0.1 + (i * 0.01)] * dim for i in range(count)]
