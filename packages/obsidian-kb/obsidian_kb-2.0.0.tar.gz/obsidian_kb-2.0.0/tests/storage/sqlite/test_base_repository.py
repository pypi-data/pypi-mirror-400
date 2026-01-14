"""Tests for BaseRepository abstract class."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio

from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.base import BaseRepository


@dataclass
class SampleEntity:
    """Sample entity for repository tests."""

    name: str
    value: int
    id: int | None = None


class SampleRepository(BaseRepository[SampleEntity]):
    """Concrete implementation of BaseRepository for testing."""

    table_name = "test_entities"

    def _row_to_entity(self, row: dict[str, Any]) -> SampleEntity:
        return SampleEntity(
            id=row["id"],
            name=row["name"],
            value=row["value"],
        )

    def _entity_to_row(self, entity: SampleEntity) -> dict[str, Any]:
        return {
            "name": entity.name,
            "value": entity.value,
        }


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


@pytest_asyncio.fixture
async def manager(temp_db_path: Path) -> SQLiteManager:
    """Create SQLiteManager with test table."""
    mgr = SQLiteManager(temp_db_path)
    await mgr.initialize()
    await mgr.execute("""
        CREATE TABLE test_entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value INTEGER NOT NULL
        )
    """)
    yield mgr
    await mgr.close()


@pytest_asyncio.fixture
async def repo(manager: SQLiteManager) -> SampleRepository:
    """Create test repository."""
    return SampleRepository(manager)


class TestBaseRepositoryInit:
    """Tests for BaseRepository initialization."""

    def test_init_without_table_name_raises(self, manager: SQLiteManager):
        """Test that init without table_name raises ValueError."""

        class BadRepository(BaseRepository[SampleEntity]):
            # table_name not set

            def _row_to_entity(self, row: dict[str, Any]) -> SampleEntity:
                return SampleEntity(id=row["id"], name=row["name"], value=row["value"])

            def _entity_to_row(self, entity: SampleEntity) -> dict[str, Any]:
                return {"name": entity.name, "value": entity.value}

        with pytest.raises(ValueError, match="must define table_name"):
            BadRepository(manager)


class TestBaseRepositoryCRUD:
    """Tests for basic CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_get_by_id(self, repo: SampleRepository):
        """Test create and get_by_id."""
        entity = SampleEntity(name="test", value=42)
        entity_id = await repo.create(entity)

        retrieved = await repo.get_by_id(entity_id)
        assert retrieved is not None
        assert retrieved.name == "test"
        assert retrieved.value == 42

    @pytest.mark.asyncio
    async def test_get_all(self, repo: SampleRepository):
        """Test get_all."""
        for i in range(5):
            await repo.create(SampleEntity(name=f"entity_{i}", value=i))

        all_entities = await repo.get_all()
        assert len(all_entities) == 5

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, repo: SampleRepository):
        """Test get_all with limit and offset."""
        for i in range(10):
            await repo.create(SampleEntity(name=f"entity_{i}", value=i))

        page = await repo.get_all(limit=3, offset=2)
        assert len(page) == 3

    @pytest.mark.asyncio
    async def test_update(self, repo: SampleRepository):
        """Test update."""
        entity = SampleEntity(name="original", value=1)
        entity_id = await repo.create(entity)

        updated = SampleEntity(name="updated", value=99)
        success = await repo.update(entity_id, updated)

        assert success is True
        retrieved = await repo.get_by_id(entity_id)
        assert retrieved is not None
        assert retrieved.name == "updated"
        assert retrieved.value == 99

    @pytest.mark.asyncio
    async def test_update_fields(self, repo: SampleRepository):
        """Test update_fields for partial update."""
        entity = SampleEntity(name="original", value=1)
        entity_id = await repo.create(entity)

        success = await repo.update_fields(entity_id, {"value": 100})

        assert success is True
        retrieved = await repo.get_by_id(entity_id)
        assert retrieved is not None
        assert retrieved.name == "original"  # Unchanged
        assert retrieved.value == 100  # Updated

    @pytest.mark.asyncio
    async def test_update_fields_empty(self, repo: SampleRepository):
        """Test update_fields with empty dict returns False."""
        entity = SampleEntity(name="test", value=1)
        entity_id = await repo.create(entity)

        success = await repo.update_fields(entity_id, {})
        assert success is False

    @pytest.mark.asyncio
    async def test_delete(self, repo: SampleRepository):
        """Test delete."""
        entity = SampleEntity(name="test", value=1)
        entity_id = await repo.create(entity)

        success = await repo.delete(entity_id)
        assert success is True

        retrieved = await repo.get_by_id(entity_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_where(self, repo: SampleRepository):
        """Test delete_where."""
        for i in range(10):
            await repo.create(SampleEntity(name=f"entity_{i}", value=i))

        deleted = await repo.delete_where("value < ?", (5,))
        assert deleted == 5

        remaining = await repo.count()
        assert remaining == 5


class TestBaseRepositoryCount:
    """Tests for count operations."""

    @pytest.mark.asyncio
    async def test_count_empty(self, repo: SampleRepository):
        """Test count on empty table."""
        count = await repo.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_with_data(self, repo: SampleRepository):
        """Test count with data."""
        for i in range(5):
            await repo.create(SampleEntity(name=f"entity_{i}", value=i))

        count = await repo.count()
        assert count == 5

    @pytest.mark.asyncio
    async def test_count_with_where(self, repo: SampleRepository):
        """Test count with where clause."""
        for i in range(10):
            await repo.create(SampleEntity(name=f"entity_{i}", value=i))

        count = await repo.count("value >= ?", (5,))
        assert count == 5

    @pytest.mark.asyncio
    async def test_exists(self, repo: SampleRepository):
        """Test exists."""
        entity_id = await repo.create(SampleEntity(name="test", value=1))

        assert await repo.exists(entity_id) is True
        assert await repo.exists(999) is False


class TestBaseRepositoryFind:
    """Tests for find operations."""

    @pytest_asyncio.fixture
    async def setup_data(self, repo: SampleRepository):
        """Setup test data."""
        for i in range(10):
            await repo.create(SampleEntity(name=f"entity_{i}", value=i * 10))

    @pytest.mark.asyncio
    async def test_find_one(self, repo: SampleRepository, setup_data):
        """Test find_one."""
        entity = await repo.find_one("name = ?", ("entity_5",))

        assert entity is not None
        assert entity.name == "entity_5"
        assert entity.value == 50

    @pytest.mark.asyncio
    async def test_find_one_not_found(self, repo: SampleRepository, setup_data):
        """Test find_one returns None when not found."""
        entity = await repo.find_one("name = ?", ("nonexistent",))
        assert entity is None

    @pytest.mark.asyncio
    async def test_find_many(self, repo: SampleRepository, setup_data):
        """Test find_many."""
        entities = await repo.find_many("value >= ?", (50,))

        assert len(entities) == 5

    @pytest.mark.asyncio
    async def test_find_many_with_limit(self, repo: SampleRepository, setup_data):
        """Test find_many with limit."""
        entities = await repo.find_many("value >= ?", (0,), limit=3)
        assert len(entities) == 3

    @pytest.mark.asyncio
    async def test_find_many_with_order_by(self, repo: SampleRepository, setup_data):
        """Test find_many with order_by."""
        entities = await repo.find_many(
            "value >= ?",
            (0,),
            order_by="value DESC",
            limit=3,
        )

        assert len(entities) == 3
        assert entities[0].value == 90  # Highest first

    @pytest.mark.asyncio
    async def test_find_ids(self, repo: SampleRepository, setup_data):
        """Test find_ids."""
        ids = await repo.find_ids("value < ?", (30,))

        assert len(ids) == 3


class TestBaseRepositoryCreateMany:
    """Tests for batch create operations."""

    @pytest.mark.asyncio
    async def test_create_many(self, repo: SampleRepository):
        """Test create_many."""
        entities = [
            SampleEntity(name=f"batch_{i}", value=i)
            for i in range(5)
        ]

        count = await repo.create_many(entities)
        assert count == 5

        total = await repo.count()
        assert total == 5

    @pytest.mark.asyncio
    async def test_create_many_empty(self, repo: SampleRepository):
        """Test create_many with empty list."""
        count = await repo.create_many([])
        assert count == 0


class TestBaseRepositoryTransaction:
    """Tests for transaction support in repository."""

    @pytest.mark.asyncio
    async def test_create_in_transaction(self, repo: SampleRepository, manager: SQLiteManager):
        """Test create_in_transaction."""
        async with manager.transaction() as conn:
            entity = SampleEntity(name="in_transaction", value=100)
            entity_id = await repo.create_in_transaction(conn, entity)

        retrieved = await repo.get_by_id(entity_id)
        assert retrieved is not None
        assert retrieved.name == "in_transaction"

    @pytest.mark.asyncio
    async def test_update_in_transaction(self, repo: SampleRepository, manager: SQLiteManager):
        """Test update_in_transaction."""
        entity_id = await repo.create(SampleEntity(name="original", value=1))

        async with manager.transaction() as conn:
            updated = SampleEntity(name="in_transaction", value=200)
            success = await repo.update_in_transaction(conn, entity_id, updated)

        assert success is True
        retrieved = await repo.get_by_id(entity_id)
        assert retrieved is not None
        assert retrieved.name == "in_transaction"

    @pytest.mark.asyncio
    async def test_delete_in_transaction(self, repo: SampleRepository, manager: SQLiteManager):
        """Test delete_in_transaction."""
        entity_id = await repo.create(SampleEntity(name="to_delete", value=1))

        async with manager.transaction() as conn:
            success = await repo.delete_in_transaction(conn, entity_id)

        assert success is True
        assert await repo.get_by_id(entity_id) is None
