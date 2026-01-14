"""Tests for VaultRepository."""

from datetime import datetime
from pathlib import Path

import pytest
import pytest_asyncio

from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.vault import Vault, VaultRepository
from obsidian_kb.storage.sqlite.schema import create_schema


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
    """Create SQLiteManager with schema."""
    mgr = SQLiteManager(temp_db_path)
    await mgr.initialize()
    await create_schema(mgr)
    yield mgr
    await mgr.close()


@pytest_asyncio.fixture
async def repo(manager: SQLiteManager) -> VaultRepository:
    """Create VaultRepository."""
    return VaultRepository(manager)


class TestVaultEntity:
    """Tests for Vault dataclass."""

    def test_vault_creation(self):
        """Test creating Vault entity."""
        vault = Vault(name="my-vault", path="/path/to/vault")

        assert vault.name == "my-vault"
        assert vault.path == "/path/to/vault"
        assert vault.id is None
        assert vault.document_count == 0
        assert vault.chunk_count == 0

    def test_vault_with_all_fields(self):
        """Test creating Vault with all fields."""
        now = datetime.now()
        vault = Vault(
            id=1,
            name="my-vault",
            path="/path/to/vault",
            created_at=now,
            last_indexed_at=now,
            document_count=100,
            chunk_count=500,
            settings={"key": "value"},
        )

        assert vault.id == 1
        assert vault.document_count == 100
        assert vault.settings == {"key": "value"}


class TestVaultRepositoryCreate:
    """Tests for VaultRepository create operations."""

    @pytest.mark.asyncio
    async def test_create_vault(self, repo: VaultRepository):
        """Test creating a vault."""
        vault = Vault(name="test-vault", path="/path/to/vault")
        vault_id = await repo.create(vault)

        assert vault_id == 1

    @pytest.mark.asyncio
    async def test_create_multiple_vaults(self, repo: VaultRepository):
        """Test creating multiple vaults."""
        vault1 = Vault(name="vault1", path="/path1")
        vault2 = Vault(name="vault2", path="/path2")

        id1 = await repo.create(vault1)
        id2 = await repo.create(vault2)

        assert id1 == 1
        assert id2 == 2

    @pytest.mark.asyncio
    async def test_create_vault_with_settings(self, repo: VaultRepository):
        """Test creating vault with settings."""
        vault = Vault(
            name="test-vault",
            path="/path",
            settings={"ignore_patterns": ["*.tmp"]},
        )
        vault_id = await repo.create(vault)

        retrieved = await repo.get_by_id(vault_id)
        assert retrieved is not None
        assert retrieved.settings == {"ignore_patterns": ["*.tmp"]}


class TestVaultRepositoryRead:
    """Tests for VaultRepository read operations."""

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo: VaultRepository):
        """Test getting vault by ID."""
        vault = Vault(name="test-vault", path="/path")
        vault_id = await repo.create(vault)

        retrieved = await repo.get_by_id(vault_id)

        assert retrieved is not None
        assert retrieved.name == "test-vault"
        assert retrieved.path == "/path"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo: VaultRepository):
        """Test getting non-existent vault by ID."""
        retrieved = await repo.get_by_id(999)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_by_name(self, repo: VaultRepository):
        """Test getting vault by name."""
        vault = Vault(name="my-vault", path="/path")
        await repo.create(vault)

        retrieved = await repo.get_by_name("my-vault")

        assert retrieved is not None
        assert retrieved.name == "my-vault"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, repo: VaultRepository):
        """Test getting non-existent vault by name."""
        retrieved = await repo.get_by_name("nonexistent")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_exists_by_name(self, repo: VaultRepository):
        """Test checking vault existence by name."""
        vault = Vault(name="existing", path="/path")
        await repo.create(vault)

        assert await repo.exists_by_name("existing") is True
        assert await repo.exists_by_name("nonexistent") is False

    @pytest.mark.asyncio
    async def test_get_id_by_name(self, repo: VaultRepository):
        """Test getting vault ID by name."""
        vault = Vault(name="my-vault", path="/path")
        vault_id = await repo.create(vault)

        retrieved_id = await repo.get_id_by_name("my-vault")
        assert retrieved_id == vault_id

    @pytest.mark.asyncio
    async def test_list_all(self, repo: VaultRepository):
        """Test listing all vaults."""
        await repo.create(Vault(name="vault1", path="/path1"))
        await repo.create(Vault(name="vault2", path="/path2"))
        await repo.create(Vault(name="vault3", path="/path3"))

        vaults = await repo.list_all()
        assert len(vaults) == 3

    @pytest.mark.asyncio
    async def test_list_names(self, repo: VaultRepository):
        """Test listing vault names."""
        await repo.create(Vault(name="beta", path="/path1"))
        await repo.create(Vault(name="alpha", path="/path2"))
        await repo.create(Vault(name="gamma", path="/path3"))

        names = await repo.list_names()
        assert names == ["alpha", "beta", "gamma"]  # Sorted


class TestVaultRepositoryUpdate:
    """Tests for VaultRepository update operations."""

    @pytest.mark.asyncio
    async def test_update_vault(self, repo: VaultRepository):
        """Test updating vault."""
        vault = Vault(name="test-vault", path="/path")
        vault_id = await repo.create(vault)

        updated_vault = Vault(name="test-vault", path="/new/path")
        success = await repo.update(vault_id, updated_vault)

        assert success is True

        retrieved = await repo.get_by_id(vault_id)
        assert retrieved is not None
        assert retrieved.path == "/new/path"

    @pytest.mark.asyncio
    async def test_update_index_stats(self, repo: VaultRepository):
        """Test updating index statistics."""
        vault = Vault(name="test-vault", path="/path")
        await repo.create(vault)

        success = await repo.update_index_stats(
            "test-vault",
            document_count=100,
            chunk_count=500,
        )

        assert success is True

        retrieved = await repo.get_by_name("test-vault")
        assert retrieved is not None
        assert retrieved.document_count == 100
        assert retrieved.chunk_count == 500
        assert retrieved.last_indexed_at is not None

    @pytest.mark.asyncio
    async def test_touch_indexed(self, repo: VaultRepository):
        """Test updating last_indexed_at timestamp."""
        vault = Vault(name="test-vault", path="/path")
        await repo.create(vault)

        success = await repo.touch_indexed("test-vault")

        assert success is True

        retrieved = await repo.get_by_name("test-vault")
        assert retrieved is not None
        assert retrieved.last_indexed_at is not None

    @pytest.mark.asyncio
    async def test_update_settings(self, repo: VaultRepository):
        """Test updating vault settings."""
        vault = Vault(name="test-vault", path="/path")
        await repo.create(vault)

        new_settings = {"ignore_patterns": ["*.tmp"], "auto_index": True}
        success = await repo.update_settings("test-vault", new_settings)

        assert success is True

        retrieved = await repo.get_by_name("test-vault")
        assert retrieved is not None
        assert retrieved.settings == new_settings


class TestVaultRepositoryDelete:
    """Tests for VaultRepository delete operations."""

    @pytest.mark.asyncio
    async def test_delete_by_id(self, repo: VaultRepository):
        """Test deleting vault by ID."""
        vault = Vault(name="test-vault", path="/path")
        vault_id = await repo.create(vault)

        success = await repo.delete(vault_id)

        assert success is True
        assert await repo.get_by_id(vault_id) is None

    @pytest.mark.asyncio
    async def test_delete_by_name(self, repo: VaultRepository):
        """Test deleting vault by name."""
        vault = Vault(name="test-vault", path="/path")
        await repo.create(vault)

        success = await repo.delete_by_name("test-vault")

        assert success is True
        assert await repo.get_by_name("test-vault") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, repo: VaultRepository):
        """Test deleting non-existent vault."""
        success = await repo.delete(999)
        assert success is False


class TestVaultRepositoryUpsert:
    """Tests for VaultRepository upsert operations."""

    @pytest.mark.asyncio
    async def test_upsert_creates_new(self, repo: VaultRepository):
        """Test upsert creates new vault."""
        vault = Vault(name="new-vault", path="/path")
        vault_id = await repo.upsert(vault)

        assert vault_id > 0
        retrieved = await repo.get_by_name("new-vault")
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_upsert_updates_existing(self, repo: VaultRepository):
        """Test upsert updates existing vault."""
        vault = Vault(name="test-vault", path="/path1")
        original_id = await repo.create(vault)

        updated_vault = Vault(name="test-vault", path="/path2")
        result_id = await repo.upsert(updated_vault)

        assert result_id == original_id

        retrieved = await repo.get_by_name("test-vault")
        assert retrieved is not None
        assert retrieved.path == "/path2"


class TestVaultRepositoryCount:
    """Tests for VaultRepository count operations."""

    @pytest.mark.asyncio
    async def test_count_empty(self, repo: VaultRepository):
        """Test counting empty table."""
        count = await repo.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_with_vaults(self, repo: VaultRepository):
        """Test counting vaults."""
        await repo.create(Vault(name="vault1", path="/path1"))
        await repo.create(Vault(name="vault2", path="/path2"))

        count = await repo.count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_exists(self, repo: VaultRepository):
        """Test exists check."""
        vault = Vault(name="test-vault", path="/path")
        vault_id = await repo.create(vault)

        assert await repo.exists(vault_id) is True
        assert await repo.exists(999) is False
