"""Tests for SQLiteManager."""

import asyncio
from pathlib import Path

import pytest
import pytest_asyncio

from obsidian_kb.storage.sqlite.manager import SQLiteManager


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create temporary database path."""
    return tmp_path / "test.sqlite"


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset SQLiteManager singleton before each test."""
    SQLiteManager.reset_instance()
    yield
    SQLiteManager.reset_instance()


class TestSQLiteManagerInit:
    """Tests for SQLiteManager initialization."""

    @pytest.mark.asyncio
    async def test_init_creates_db_file(self, temp_db_path: Path):
        """Test that initialization creates database file."""
        manager = SQLiteManager(temp_db_path)
        await manager.initialize()

        assert temp_db_path.exists()
        await manager.close()

    @pytest.mark.asyncio
    async def test_init_creates_parent_dirs(self, tmp_path: Path):
        """Test that initialization creates parent directories."""
        db_path = tmp_path / "nested" / "dir" / "test.sqlite"
        manager = SQLiteManager(db_path)
        await manager.initialize()

        assert db_path.exists()
        assert db_path.parent.exists()
        await manager.close()

    @pytest.mark.asyncio
    async def test_context_manager(self, temp_db_path: Path):
        """Test async context manager."""
        async with SQLiteManager(temp_db_path) as manager:
            assert manager.is_initialized()

        # After exit, should be closed
        assert not manager.is_initialized()

    @pytest.mark.asyncio
    async def test_double_init_is_safe(self, temp_db_path: Path):
        """Test that calling initialize twice is safe."""
        manager = SQLiteManager(temp_db_path)
        await manager.initialize()
        await manager.initialize()  # Should not raise

        assert manager.is_initialized()
        await manager.close()


class TestSQLiteManagerSingleton:
    """Tests for SQLiteManager singleton pattern."""

    def test_get_instance_creates_singleton(self, temp_db_path: Path):
        """Test that get_instance creates singleton."""
        manager1 = SQLiteManager.get_instance(temp_db_path)
        manager2 = SQLiteManager.get_instance(temp_db_path)

        assert manager1 is manager2

    def test_different_paths_create_different_instances(self, tmp_path: Path):
        """Test that different paths create different instances."""
        path1 = tmp_path / "db1.sqlite"
        path2 = tmp_path / "db2.sqlite"

        manager1 = SQLiteManager.get_instance(path1)
        manager2 = SQLiteManager.get_instance(path2)

        assert manager1 is not manager2

    def test_reset_instance_clears_specific_path(self, tmp_path: Path):
        """Test resetting specific instance."""
        path1 = tmp_path / "db1.sqlite"
        path2 = tmp_path / "db2.sqlite"

        manager1 = SQLiteManager.get_instance(path1)
        manager2 = SQLiteManager.get_instance(path2)

        SQLiteManager.reset_instance(path1)

        manager1_new = SQLiteManager.get_instance(path1)
        manager2_same = SQLiteManager.get_instance(path2)

        assert manager1 is not manager1_new
        assert manager2 is manager2_same

    def test_reset_instance_clears_all(self, tmp_path: Path):
        """Test resetting all instances."""
        path1 = tmp_path / "db1.sqlite"
        path2 = tmp_path / "db2.sqlite"

        manager1 = SQLiteManager.get_instance(path1)
        manager2 = SQLiteManager.get_instance(path2)

        SQLiteManager.reset_instance()  # Reset all

        manager1_new = SQLiteManager.get_instance(path1)
        manager2_new = SQLiteManager.get_instance(path2)

        assert manager1 is not manager1_new
        assert manager2 is not manager2_new


class TestSQLiteManagerExecute:
    """Tests for SQLiteManager query execution."""

    @pytest.mark.asyncio
    async def test_execute_simple_query(self, temp_db_path: Path):
        """Test executing simple query."""
        async with SQLiteManager(temp_db_path) as manager:
            cursor = await manager.execute(
                "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
            )
            assert cursor is not None

    @pytest.mark.asyncio
    async def test_execute_with_parameters(self, temp_db_path: Path):
        """Test executing query with parameters."""
        async with SQLiteManager(temp_db_path) as manager:
            await manager.execute(
                "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
            )
            cursor = await manager.execute(
                "INSERT INTO test (name) VALUES (?)",
                ("test_name",),
            )
            assert cursor.lastrowid == 1

    @pytest.mark.asyncio
    async def test_execute_many(self, temp_db_path: Path):
        """Test executemany with multiple parameter sets."""
        async with SQLiteManager(temp_db_path) as manager:
            await manager.execute(
                "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
            )
            cursor = await manager.execute_many(
                "INSERT INTO test (name) VALUES (?)",
                [("name1",), ("name2",), ("name3",)],
            )
            assert cursor.rowcount == 3

    @pytest.mark.asyncio
    async def test_execute_script(self, temp_db_path: Path):
        """Test executing SQL script."""
        async with SQLiteManager(temp_db_path) as manager:
            await manager.execute_script("""
                CREATE TABLE test1 (id INTEGER PRIMARY KEY);
                CREATE TABLE test2 (id INTEGER PRIMARY KEY);
            """)

            # Verify tables exist
            tables = await manager.fetch_all(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            table_names = [t["name"] for t in tables]
            assert "test1" in table_names
            assert "test2" in table_names


class TestSQLiteManagerFetch:
    """Tests for SQLiteManager fetch methods."""

    @pytest_asyncio.fixture
    async def manager_with_data(self, temp_db_path: Path):
        """Create manager with test data."""
        manager = SQLiteManager(temp_db_path)
        await manager.initialize()

        await manager.execute(
            "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)"
        )
        await manager.execute_many(
            "INSERT INTO test (name, value) VALUES (?, ?)",
            [("alpha", 10), ("beta", 20), ("gamma", 30)],
        )

        yield manager
        await manager.close()

    @pytest.mark.asyncio
    async def test_fetch_one(self, manager_with_data: SQLiteManager):
        """Test fetching single row."""
        row = await manager_with_data.fetch_one(
            "SELECT * FROM test WHERE name = ?",
            ("beta",),
        )

        assert row is not None
        assert row["name"] == "beta"
        assert row["value"] == 20

    @pytest.mark.asyncio
    async def test_fetch_one_no_result(self, manager_with_data: SQLiteManager):
        """Test fetching single row with no results."""
        row = await manager_with_data.fetch_one(
            "SELECT * FROM test WHERE name = ?",
            ("nonexistent",),
        )

        assert row is None

    @pytest.mark.asyncio
    async def test_fetch_all(self, manager_with_data: SQLiteManager):
        """Test fetching all rows."""
        rows = await manager_with_data.fetch_all(
            "SELECT * FROM test ORDER BY name"
        )

        assert len(rows) == 3
        assert rows[0]["name"] == "alpha"
        assert rows[1]["name"] == "beta"
        assert rows[2]["name"] == "gamma"

    @pytest.mark.asyncio
    async def test_fetch_all_with_params(self, manager_with_data: SQLiteManager):
        """Test fetching all rows with parameters."""
        rows = await manager_with_data.fetch_all(
            "SELECT * FROM test WHERE value > ?",
            (15,),
        )

        assert len(rows) == 2

    @pytest.mark.asyncio
    async def test_fetch_value(self, manager_with_data: SQLiteManager):
        """Test fetching single value."""
        count = await manager_with_data.fetch_value("SELECT COUNT(*) FROM test")

        assert count == 3

    @pytest.mark.asyncio
    async def test_fetch_value_no_result(self, manager_with_data: SQLiteManager):
        """Test fetching single value with no results."""
        result = await manager_with_data.fetch_value(
            "SELECT name FROM test WHERE value > 100"
        )

        assert result is None


class TestSQLiteManagerTransaction:
    """Tests for SQLiteManager transaction support."""

    @pytest.mark.asyncio
    async def test_transaction_commit(self, temp_db_path: Path):
        """Test transaction commits on success."""
        async with SQLiteManager(temp_db_path) as manager:
            await manager.execute(
                "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"
            )

            async with manager.transaction() as conn:
                await conn.execute("INSERT INTO test (name) VALUES (?)", ("test1",))
                await conn.execute("INSERT INTO test (name) VALUES (?)", ("test2",))

            # Verify data was committed
            count = await manager.fetch_value("SELECT COUNT(*) FROM test")
            assert count == 2

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, temp_db_path: Path):
        """Test transaction rollback on error."""
        async with SQLiteManager(temp_db_path) as manager:
            await manager.execute(
                "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT UNIQUE)"
            )
            await manager.execute("INSERT INTO test (name) VALUES (?)", ("test1",))

            with pytest.raises(Exception):
                async with manager.transaction() as conn:
                    await conn.execute("INSERT INTO test (name) VALUES (?)", ("test2",))
                    # This will fail due to UNIQUE constraint
                    await conn.execute("INSERT INTO test (name) VALUES (?)", ("test1",))

            # Verify rollback - only original row should exist
            count = await manager.fetch_value("SELECT COUNT(*) FROM test")
            assert count == 1


class TestSQLiteManagerConnectionPool:
    """Tests for SQLiteManager connection pooling."""

    @pytest.mark.asyncio
    async def test_pool_reuses_connections(self, temp_db_path: Path):
        """Test that pool reuses connections."""
        async with SQLiteManager(temp_db_path, pool_size=2) as manager:
            # Make several queries
            for _ in range(10):
                await manager.fetch_value("SELECT 1")

            stats = manager.get_stats()
            # Should have reused connections, not created 10
            assert stats["connections_created"] <= 2

    @pytest.mark.asyncio
    async def test_concurrent_queries(self, temp_db_path: Path):
        """Test concurrent query execution."""
        async with SQLiteManager(temp_db_path, pool_size=3) as manager:
            await manager.execute(
                "CREATE TABLE test (id INTEGER PRIMARY KEY)"
            )

            # Execute concurrent queries
            async def query():
                return await manager.fetch_value("SELECT COUNT(*) FROM test")

            results = await asyncio.gather(*[query() for _ in range(10)])
            assert all(r == 0 for r in results)

    @pytest.mark.asyncio
    async def test_get_stats(self, temp_db_path: Path):
        """Test getting pool statistics."""
        async with SQLiteManager(temp_db_path) as manager:
            await manager.fetch_value("SELECT 1")

            stats = manager.get_stats()

            assert "db_path" in stats
            assert "pool_size" in stats
            assert "connections_created" in stats
            assert "total_queries" in stats
            assert stats["total_queries"] >= 1
            assert stats["initialized"] is True


class TestSQLiteManagerWALMode:
    """Tests for WAL mode configuration."""

    @pytest.mark.asyncio
    async def test_wal_mode_enabled(self, temp_db_path: Path):
        """Test that WAL mode is enabled."""
        async with SQLiteManager(temp_db_path) as manager:
            mode = await manager.fetch_value("PRAGMA journal_mode")
            assert mode == "wal"

    @pytest.mark.asyncio
    async def test_foreign_keys_enabled(self, temp_db_path: Path):
        """Test that foreign keys are enabled."""
        async with SQLiteManager(temp_db_path) as manager:
            fk_status = await manager.fetch_value("PRAGMA foreign_keys")
            assert fk_status == 1
