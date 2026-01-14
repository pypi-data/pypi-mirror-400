"""Utilities for testing MCP tools.

This module provides helpers for isolated testing of MCP tools:
- Getting original functions from decorated MCP tools
- Creating isolated test contexts with mocked services
- Mocking ServiceContainer for dependency injection

Usage:
    from tests.helpers import create_mcp_test_context, get_unwrapped_mcp_tool

    @pytest.mark.asyncio
    async def test_search_vault():
        async with create_mcp_test_context() as ctx:
            # Get unwrapped function (bypasses @mcp.tool() decorator)
            search_fn = get_unwrapped_mcp_tool("search_vault")

            # Setup mock data
            ctx.setup_mock_chunks([...])

            # Call function
            result = await search_fn("vault", "query")

            # Assert
            assert "expected" in result
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable
from unittest.mock import AsyncMock, MagicMock, patch

if TYPE_CHECKING:
    from obsidian_kb.lance_db import LanceDBManager
    from obsidian_kb.service_container import ServiceContainer
    from obsidian_kb.types import DocumentChunk


@dataclass
class MCPTestContext:
    """Context for isolated MCP tool testing.

    Provides mocked services and utilities for setting up test data.

    Attributes:
        db_path: Path to temporary test database
        db_manager: Mocked LanceDBManager
        embedding_service: Mocked EmbeddingService
        services: Mocked ServiceContainer
        patches: List of active patches to clean up
    """

    db_path: Path
    db_manager: MagicMock | None = None
    embedding_service: AsyncMock | None = None
    services: MagicMock | None = None
    patches: list[Any] = field(default_factory=list)

    # Test data
    _chunks: list["DocumentChunk"] = field(default_factory=list)
    _embeddings: list[list[float]] = field(default_factory=list)

    def setup_mock_chunks(
        self,
        chunks: list["DocumentChunk"],
        embeddings: list[list[float]] | None = None,
    ) -> None:
        """Setup mock chunks for testing.

        Args:
            chunks: List of DocumentChunk to add
            embeddings: Optional embeddings (defaults to mock vectors)
        """
        self._chunks = chunks
        if embeddings is None:
            self._embeddings = [[0.1] * 768 for _ in chunks]
        else:
            self._embeddings = embeddings

        # Update db_manager mock to return these chunks
        if self.db_manager:
            self.db_manager.hybrid_search = AsyncMock(
                return_value=self._create_search_results()
            )
            self.db_manager.vector_search = AsyncMock(
                return_value=self._create_search_results()
            )
            self.db_manager.fts_search = AsyncMock(
                return_value=self._create_search_results()
            )

    def _create_search_results(self) -> list:
        """Create mock search results from stored chunks."""
        from obsidian_kb.types import SearchResult

        results = []
        for i, chunk in enumerate(self._chunks):
            results.append(
                SearchResult(
                    chunk_id=chunk.id,
                    vault_name=chunk.vault_name,
                    file_path=chunk.file_path,
                    title=chunk.title,
                    section=chunk.section,
                    content=chunk.content,
                    tags=chunk.tags or [],
                    score=0.9 - (i * 0.1),  # Decreasing scores
                    created_at=chunk.created_at,
                    modified_at=chunk.modified_at,
                )
            )
        return results

    def setup_mock_vaults(self, vault_names: list[str]) -> None:
        """Setup mock vault list.

        Args:
            vault_names: List of vault names to return
        """
        if self.db_manager:
            self.db_manager.list_vaults = AsyncMock(return_value=vault_names)

    def setup_mock_vault_stats(
        self,
        vault_name: str,
        file_count: int = 10,
        chunk_count: int = 50,
    ) -> None:
        """Setup mock vault stats.

        Args:
            vault_name: Name of the vault
            file_count: Number of files
            chunk_count: Number of chunks
        """
        from obsidian_kb.types import VaultStats

        stats = VaultStats(
            vault_name=vault_name,
            file_count=file_count,
            chunk_count=chunk_count,
            indexed_at=datetime.now(),
            tags_count=5,
            top_tags=[("python", 10), ("test", 5)],
        )

        if self.db_manager:
            self.db_manager.get_vault_stats = AsyncMock(return_value=stats)

    def cleanup(self) -> None:
        """Stop all patches and cleanup resources."""
        for p in self.patches:
            try:
                p.stop()
            except RuntimeError:
                pass  # Already stopped
        self.patches.clear()


def get_unwrapped_mcp_tool(tool_name: str) -> Callable | None:
    """Get original function from decorated MCP tool.

    FastMCP's @mcp.tool() decorator wraps functions in FunctionTool objects.
    This function retrieves the original callable for direct testing.

    Args:
        tool_name: Name of the MCP tool function

    Returns:
        Original function if found, None otherwise

    Example:
        search_fn = get_unwrapped_mcp_tool("search_vault")
        if search_fn:
            result = await search_fn("vault", "query")
    """
    import obsidian_kb.mcp_server as mcp_module

    # Try to get function from mcp_server module
    func = getattr(mcp_module, tool_name, None)
    if func is None:
        # Try mcp_tools submodules
        from obsidian_kb.mcp_tools import indexing_tools, provider_tools, quality_tools

        for module in [indexing_tools, provider_tools, quality_tools]:
            func = getattr(module, tool_name, None)
            if func is not None:
                break

    if func is None:
        return None

    # Try to get __wrapped__ attribute (from @wraps decorator)
    wrapped = getattr(func, "__wrapped__", None)
    if wrapped is not None and callable(wrapped):
        return wrapped

    # If it's a FunctionTool, try to get the handler
    if hasattr(func, "fn"):
        return func.fn

    # If callable, return as-is
    if callable(func):
        return func

    return None


def mock_service_container(
    db_path: Path | None = None,
    mock_embedding: bool = True,
    mock_db: bool = True,
    mock_search: bool = True,
) -> tuple[MagicMock, list]:
    """Create a mocked ServiceContainer for testing.

    Args:
        db_path: Optional path for temporary database
        mock_embedding: Whether to mock embedding service
        mock_db: Whether to mock database manager
        mock_search: Whether to mock search service

    Returns:
        Tuple of (mock_services, patches_list)

    Example:
        mock_services, patches = mock_service_container(tmp_path)
        try:
            # Use mock_services in tests
            mock_services.db_manager.list_vaults.return_value = ["test"]
        finally:
            for p in patches:
                p.stop()
    """
    patches: list[Any] = []

    # Create mock ServiceContainer
    mock_services = MagicMock()

    # Mock embedding service
    if mock_embedding:
        mock_embedding_svc = AsyncMock()
        mock_embedding_svc.get_embedding = AsyncMock(return_value=[0.1] * 768)
        mock_embedding_svc.get_embeddings_batch = AsyncMock(
            side_effect=lambda texts, **kwargs: [[0.1] * 768] * len(texts)
        )
        mock_embedding_svc.health_check = AsyncMock(return_value=True)
        mock_embedding_svc.close = AsyncMock()
        mock_services.embedding_service = mock_embedding_svc

    # Mock database manager
    if mock_db:
        mock_db_mgr = MagicMock()
        mock_db_mgr.list_vaults = AsyncMock(return_value=[])
        mock_db_mgr.get_vault_stats = AsyncMock(return_value=None)
        mock_db_mgr.hybrid_search = AsyncMock(return_value=[])
        mock_db_mgr.vector_search = AsyncMock(return_value=[])
        mock_db_mgr.fts_search = AsyncMock(return_value=[])
        mock_db_mgr.upsert_chunks = AsyncMock()
        mock_db_mgr.delete_vault = AsyncMock()
        mock_db_mgr.close = MagicMock()
        mock_services.db_manager = mock_db_mgr

    # Mock search service
    if mock_search:
        from obsidian_kb.types import (
            SearchIntent,
            SearchRequest,
            SearchResponse,
        )

        mock_search_svc = MagicMock()

        async def mock_search_fn(request: SearchRequest) -> SearchResponse:
            return SearchResponse(
                request=request,
                detected_intent=SearchIntent.SEMANTIC,
                intent_confidence=0.9,
                results=[],
                total_found=0,
                execution_time_ms=10.0,
                has_more=False,
                strategy_used="mock",
                filters_applied={},
            )

        mock_search_svc.search = AsyncMock(side_effect=mock_search_fn)
        mock_services.search_service = mock_search_svc

    # Mock other commonly used services
    mock_services.mcp_rate_limiter = None
    mock_services.job_queue = None
    mock_services.formatter = MagicMock()
    mock_services.formatter.format_markdown = MagicMock(return_value="Mock result")
    mock_services.diagnostics_service = MagicMock()
    mock_services.metrics_collector = MagicMock()
    mock_services.recovery_service = MagicMock()
    mock_services.performance_monitor = MagicMock()
    mock_services.chunk_repository = MagicMock()
    mock_services.document_repository = MagicMock()
    mock_services.embedding_cache = MagicMock()

    # Patch get_service_container to return our mock
    p = patch(
        "obsidian_kb.service_container.get_service_container",
        return_value=mock_services,
    )
    p.start()
    patches.append(p)

    # Also patch in mcp_server module
    p2 = patch(
        "obsidian_kb.mcp_server.get_service_container",
        return_value=mock_services,
    )
    p2.start()
    patches.append(p2)

    return mock_services, patches


@asynccontextmanager
async def create_mcp_test_context(
    tmp_path: Path | None = None,
    mock_embedding: bool = True,
    mock_db: bool = True,
    use_real_db: bool = False,
) -> AsyncIterator[MCPTestContext]:
    """Create an isolated context for MCP tool testing.

    This context manager sets up all necessary mocks and provides
    utilities for configuring test data.

    Args:
        tmp_path: Temporary path for test database (required if use_real_db=True)
        mock_embedding: Whether to mock embedding service
        mock_db: Whether to mock database manager (ignored if use_real_db=True)
        use_real_db: Use real LanceDB instead of mocks

    Yields:
        MCPTestContext with configured mocks

    Example:
        @pytest.mark.asyncio
        async def test_search(tmp_path):
            async with create_mcp_test_context(tmp_path) as ctx:
                ctx.setup_mock_chunks([chunk1, chunk2])
                ctx.setup_mock_vaults(["test_vault"])

                search_fn = get_unwrapped_mcp_tool("search_vault")
                result = await search_fn("test_vault", "query")

                assert "expected" in result
    """
    import tempfile

    # Use provided tmp_path or create temporary directory
    if tmp_path is None:
        import tempfile
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_db"
    else:
        db_path = tmp_path / "test_db"

    context = MCPTestContext(db_path=db_path)

    try:
        if use_real_db:
            # Use real LanceDB for integration tests
            from obsidian_kb.lance_db import LanceDBManager

            context.db_manager = LanceDBManager(db_path=db_path)
            mock_services, patches = mock_service_container(
                db_path=db_path,
                mock_embedding=mock_embedding,
                mock_db=False,  # Don't mock db_manager
            )
            # Replace mock db_manager with real one
            mock_services.db_manager = context.db_manager
        else:
            mock_services, patches = mock_service_container(
                db_path=db_path,
                mock_embedding=mock_embedding,
                mock_db=mock_db,
            )
            context.db_manager = mock_services.db_manager

        context.services = mock_services
        context.embedding_service = mock_services.embedding_service
        context.patches = patches

        yield context

    finally:
        context.cleanup()

        # Cleanup temporary directory if we created it
        if tmp_path is None:
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass


# Fixture helpers for pytest
def pytest_mcp_test_context(request):
    """Pytest fixture for MCP test context.

    Usage in conftest.py:
        from tests.helpers.mcp_testing import pytest_mcp_test_context

        @pytest.fixture
        async def mcp_context(tmp_path):
            async with create_mcp_test_context(tmp_path) as ctx:
                yield ctx
    """
    pass  # This is a documentation helper, actual fixture should be in conftest.py
