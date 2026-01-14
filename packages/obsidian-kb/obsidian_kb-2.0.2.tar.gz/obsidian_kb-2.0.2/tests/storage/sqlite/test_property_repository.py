"""Tests for PropertyRepository."""

from pathlib import Path

import pytest
import pytest_asyncio

from obsidian_kb.storage.sqlite.frontmatter_parser import (
    FrontmatterParseResult,
    FrontmatterParser,
    ParsedProperty,
    PropertyValueType,
)
from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.document import (
    SQLiteDocument,
    SQLiteDocumentRepository,
)
from obsidian_kb.storage.sqlite.repositories.property import (
    DocumentProperty,
    PropertyRepository,
)
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
async def vault_id(manager: SQLiteManager) -> int:
    """Create a test vault and return its ID."""
    vault_repo = VaultRepository(manager)
    return await vault_repo.create(Vault(name="test-vault", path="/path/to/vault"))


@pytest_asyncio.fixture
async def document_id(manager: SQLiteManager, vault_id: int) -> int:
    """Create a test document and return its ID."""
    doc_repo = SQLiteDocumentRepository(manager)
    doc = SQLiteDocument(
        document_id="test-vault::note.md",
        vault_id=vault_id,
        file_path="note.md",
        file_name="note.md",
        content_hash="abc123",
    )
    return await doc_repo.create(doc)


@pytest_asyncio.fixture
async def repo(manager: SQLiteManager) -> PropertyRepository:
    """Create PropertyRepository."""
    return PropertyRepository(manager)


@pytest.fixture
def parser() -> FrontmatterParser:
    """Create FrontmatterParser."""
    return FrontmatterParser()


class TestDocumentPropertyEntity:
    """Tests for DocumentProperty dataclass."""

    def test_create_property(self):
        """Test creating DocumentProperty entity."""
        prop = DocumentProperty(
            document_id=1,
            property_key="status",
            value_type="string",
            property_value="active",
        )

        assert prop.document_id == 1
        assert prop.property_key == "status"
        assert prop.value_type == "string"
        assert prop.property_value == "active"
        assert prop.id is None
        assert prop.list_index == 0

    def test_create_number_property(self):
        """Test creating number property."""
        prop = DocumentProperty(
            document_id=1,
            property_key="priority",
            value_type="number",
            property_value="5",
            value_number=5.0,
        )

        assert prop.value_number == 5.0

    def test_create_link_property(self):
        """Test creating link property."""
        prop = DocumentProperty(
            document_id=1,
            property_key="participant",
            value_type="link",
            property_value="[[vshadrin]]",
            value_link_target="vshadrin",
        )

        assert prop.value_link_target == "vshadrin"


class TestPropertyRepositoryCreate:
    """Tests for PropertyRepository create operations."""

    @pytest.mark.asyncio
    async def test_create_property(self, repo: PropertyRepository, document_id: int):
        """Test creating a single property."""
        prop = DocumentProperty(
            document_id=document_id,
            property_key="status",
            value_type="string",
            property_value="active",
        )
        prop_id = await repo.create(prop)

        assert prop_id > 0

    @pytest.mark.asyncio
    async def test_create_from_parsed(
        self,
        repo: PropertyRepository,
        document_id: int,
        parser: FrontmatterParser,
    ):
        """Test creating properties from parsed frontmatter."""
        yaml_content = """status: active
priority: 5
tags: [a, b]"""
        result = parser.parse_yaml(yaml_content)

        count = await repo.create_from_parsed(document_id, result)

        assert count == 4  # status + priority + 2 tags

    @pytest.mark.asyncio
    async def test_create_from_parsed_empty(self, repo: PropertyRepository, document_id: int):
        """Test creating from empty parse result."""
        result = FrontmatterParseResult()

        count = await repo.create_from_parsed(document_id, result)

        assert count == 0

    @pytest.mark.asyncio
    async def test_create_from_parsed_property(
        self,
        repo: PropertyRepository,
        document_id: int,
    ):
        """Test creating single property from ParsedProperty."""
        parsed_prop = ParsedProperty(
            key="status",
            value_type=PropertyValueType.STRING,
            property_value="active",
        )

        prop_id = await repo.create_from_parsed_property(document_id, parsed_prop)

        assert prop_id > 0


class TestPropertyRepositoryDocumentQueries:
    """Tests for document-scoped property queries."""

    @pytest_asyncio.fixture
    async def setup_properties(
        self,
        repo: PropertyRepository,
        document_id: int,
        parser: FrontmatterParser,
    ):
        """Setup test properties."""
        yaml_content = """status: active
priority: 5
date: 2025-01-08
tags: [meeting, q1]
participant: "[[vshadrin]]"
"""
        result = parser.parse_yaml(yaml_content)
        await repo.create_from_parsed(document_id, result)

    @pytest.mark.asyncio
    async def test_get_document_properties(
        self,
        repo: PropertyRepository,
        document_id: int,
        setup_properties,
    ):
        """Test getting all properties for a document."""
        properties = await repo.get_document_properties(document_id)

        assert len(properties) == 6  # status, priority, date, tags(2), participant

    @pytest.mark.asyncio
    async def test_get_document_property(
        self,
        repo: PropertyRepository,
        document_id: int,
        setup_properties,
    ):
        """Test getting specific property."""
        properties = await repo.get_document_property(document_id, "status")

        assert len(properties) == 1
        assert properties[0].property_value == "active"

    @pytest.mark.asyncio
    async def test_get_document_property_list(
        self,
        repo: PropertyRepository,
        document_id: int,
        setup_properties,
    ):
        """Test getting list property."""
        properties = await repo.get_document_property(document_id, "tags")

        assert len(properties) == 2
        values = {p.property_value for p in properties}
        assert values == {"meeting", "q1"}

    @pytest.mark.asyncio
    async def test_delete_document_properties(
        self,
        repo: PropertyRepository,
        document_id: int,
        setup_properties,
    ):
        """Test deleting all document properties."""
        count = await repo.delete_document_properties(document_id)

        assert count == 6

        remaining = await repo.get_document_properties(document_id)
        assert len(remaining) == 0


class TestPropertyRepositoryVaultQueries:
    """Tests for vault-scoped property queries."""

    @pytest_asyncio.fixture
    async def setup_multi_doc(
        self,
        manager: SQLiteManager,
        repo: PropertyRepository,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Setup multiple documents with properties."""
        doc_repo = SQLiteDocumentRepository(manager)

        # Document 1: active, priority 1
        doc1 = SQLiteDocument(
            document_id="test-vault::doc1.md",
            vault_id=vault_id,
            file_path="doc1.md",
            file_name="doc1.md",
            content_hash="hash1",
        )
        doc1_id = await doc_repo.create(doc1)

        yaml1 = """status: active
priority: 1
date: 2025-01-01
participant: "[[alice]]"
"""
        result1 = parser.parse_yaml(yaml1)
        await repo.create_from_parsed(doc1_id, result1)

        # Document 2: pending, priority 5
        doc2 = SQLiteDocument(
            document_id="test-vault::doc2.md",
            vault_id=vault_id,
            file_path="doc2.md",
            file_name="doc2.md",
            content_hash="hash2",
        )
        doc2_id = await doc_repo.create(doc2)

        yaml2 = """status: pending
priority: 5
date: 2025-01-15
participant: "[[bob]]"
"""
        result2 = parser.parse_yaml(yaml2)
        await repo.create_from_parsed(doc2_id, result2)

        # Document 3: done, priority 3
        doc3 = SQLiteDocument(
            document_id="test-vault::doc3.md",
            vault_id=vault_id,
            file_path="doc3.md",
            file_name="doc3.md",
            content_hash="hash3",
        )
        doc3_id = await doc_repo.create(doc3)

        yaml3 = """status: done
priority: 3
date: 2025-01-10
participant: "[[alice]]"
archived: true
"""
        result3 = parser.parse_yaml(yaml3)
        await repo.create_from_parsed(doc3_id, result3)

        return {"doc1": doc1_id, "doc2": doc2_id, "doc3": doc3_id}

    @pytest.mark.asyncio
    async def test_find_by_key(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents by property key."""
        doc_ids = await repo.find_by_key(vault_id, "status")

        assert len(doc_ids) == 3

    @pytest.mark.asyncio
    async def test_find_by_key_value(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents by exact key-value."""
        doc_ids = await repo.find_by_key_value(vault_id, "status", "active")

        assert len(doc_ids) == 1
        assert setup_multi_doc["doc1"] in doc_ids

    @pytest.mark.asyncio
    async def test_find_by_key_value_like(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents by value pattern."""
        doc_ids = await repo.find_by_key_value_like(vault_id, "status", "%e%")

        assert len(doc_ids) == 3  # active, pending, done all have 'e'

    @pytest.mark.asyncio
    async def test_find_by_number_range(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents by number range."""
        doc_ids = await repo.find_by_number_range(vault_id, "priority", 1, 3)

        assert len(doc_ids) == 2  # priority 1 and 3

    @pytest.mark.asyncio
    async def test_find_by_number_range_min_only(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents with minimum number value."""
        doc_ids = await repo.find_by_number_range(vault_id, "priority", min_value=3)

        assert len(doc_ids) == 2  # priority 3 and 5

    @pytest.mark.asyncio
    async def test_find_by_number_range_max_only(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents with maximum number value."""
        doc_ids = await repo.find_by_number_range(vault_id, "priority", max_value=3)

        assert len(doc_ids) == 2  # priority 1 and 3

    @pytest.mark.asyncio
    async def test_find_by_date_range(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents by date range."""
        doc_ids = await repo.find_by_date_range(
            vault_id, "date", after="2025-01-05", before="2025-01-12"
        )

        assert len(doc_ids) == 1  # only doc3 with date 2025-01-10

    @pytest.mark.asyncio
    async def test_find_by_date_range_after_only(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents after a date."""
        doc_ids = await repo.find_by_date_range(vault_id, "date", after="2025-01-10")

        assert len(doc_ids) == 2  # doc2 (2025-01-15) and doc3 (2025-01-10)

    @pytest.mark.asyncio
    async def test_find_by_link_target(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents by link target."""
        doc_ids = await repo.find_by_link_target(vault_id, "alice")

        assert len(doc_ids) == 2  # doc1 and doc3

    @pytest.mark.asyncio
    async def test_find_by_boolean(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_multi_doc,
    ):
        """Test finding documents by boolean value."""
        doc_ids = await repo.find_by_boolean(vault_id, "archived", True)

        assert len(doc_ids) == 1
        assert setup_multi_doc["doc3"] in doc_ids


class TestPropertyRepositoryAggregation:
    """Tests for aggregation queries."""

    @pytest_asyncio.fixture
    async def setup_aggregation(
        self,
        manager: SQLiteManager,
        repo: PropertyRepository,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Setup documents for aggregation tests."""
        doc_repo = SQLiteDocumentRepository(manager)

        for i in range(5):
            doc = SQLiteDocument(
                document_id=f"test-vault::doc{i}.md",
                vault_id=vault_id,
                file_path=f"doc{i}.md",
                file_name=f"doc{i}.md",
                content_hash=f"hash{i}",
            )
            doc_id = await doc_repo.create(doc)

            statuses = ["active", "active", "pending", "done", "done"]
            yaml_content = f"""status: {statuses[i]}
priority: {i + 1}
"""
            result = parser.parse_yaml(yaml_content)
            await repo.create_from_parsed(doc_id, result)

    @pytest.mark.asyncio
    async def test_get_unique_keys(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_aggregation,
    ):
        """Test getting unique property keys."""
        keys = await repo.get_unique_keys(vault_id)

        assert "status" in keys
        assert "priority" in keys
        assert len(keys) == 2

    @pytest.mark.asyncio
    async def test_get_unique_values(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_aggregation,
    ):
        """Test getting unique values for a key."""
        values = await repo.get_unique_values(vault_id, "status")

        assert len(values) == 3
        assert "active" in values
        assert "pending" in values
        assert "done" in values

    @pytest.mark.asyncio
    async def test_get_value_counts(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_aggregation,
    ):
        """Test getting value counts."""
        counts = await repo.get_value_counts(vault_id, "status")

        assert counts["active"] == 2
        assert counts["pending"] == 1
        assert counts["done"] == 2

    @pytest.mark.asyncio
    async def test_get_key_statistics(
        self,
        repo: PropertyRepository,
        vault_id: int,
        setup_aggregation,
    ):
        """Test getting numeric key statistics."""
        stats = await repo.get_key_statistics(vault_id, "priority")

        assert stats["min_value"] == 1.0
        assert stats["max_value"] == 5.0
        assert stats["avg_value"] == 3.0
        assert stats["document_count"] == 5

    @pytest.mark.asyncio
    async def test_get_link_targets(
        self,
        manager: SQLiteManager,
        repo: PropertyRepository,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Test getting all link targets."""
        doc_repo = SQLiteDocumentRepository(manager)

        doc = SQLiteDocument(
            document_id="test-vault::links.md",
            vault_id=vault_id,
            file_path="links.md",
            file_name="links.md",
            content_hash="links",
        )
        doc_id = await doc_repo.create(doc)

        yaml_content = """author: "[[john]]"
reviewers:
  - "[[alice]]"
  - "[[bob]]"
"""
        result = parser.parse_yaml(yaml_content)
        await repo.create_from_parsed(doc_id, result)

        targets = await repo.get_link_targets(vault_id)

        assert len(targets) == 3
        assert "john" in targets
        assert "alice" in targets
        assert "bob" in targets


class TestPropertyRepositoryBatch:
    """Tests for batch operations."""

    @pytest.mark.asyncio
    async def test_replace_document_properties(
        self,
        repo: PropertyRepository,
        document_id: int,
        parser: FrontmatterParser,
    ):
        """Test replacing all document properties."""
        # Create initial properties
        yaml1 = "status: active\npriority: 1"
        result1 = parser.parse_yaml(yaml1)
        await repo.create_from_parsed(document_id, result1)

        # Replace with new properties
        yaml2 = "status: done\ntags: [a, b]"
        result2 = parser.parse_yaml(yaml2)
        count = await repo.replace_document_properties(document_id, result2)

        assert count == 3  # status + 2 tags

        # Verify old properties are gone
        properties = await repo.get_document_properties(document_id)
        keys = {p.property_key for p in properties}
        assert "priority" not in keys
        assert "status" in keys
        assert "tags" in keys

    @pytest.mark.asyncio
    async def test_delete_by_vault(
        self,
        manager: SQLiteManager,
        repo: PropertyRepository,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Test deleting all properties in a vault."""
        doc_repo = SQLiteDocumentRepository(manager)

        # Create documents with properties
        for i in range(3):
            doc = SQLiteDocument(
                document_id=f"test-vault::doc{i}.md",
                vault_id=vault_id,
                file_path=f"doc{i}.md",
                file_name=f"doc{i}.md",
                content_hash=f"hash{i}",
            )
            doc_id = await doc_repo.create(doc)

            yaml_content = f"status: active\nindex: {i}"
            result = parser.parse_yaml(yaml_content)
            await repo.create_from_parsed(doc_id, result)

        # Delete all properties
        count = await repo.delete_by_vault(vault_id)

        assert count == 6  # 3 docs * 2 properties each


class TestPropertyRepositoryIntegration:
    """Integration tests with full parsing flow."""

    @pytest.mark.asyncio
    async def test_full_flow(
        self,
        manager: SQLiteManager,
        repo: PropertyRepository,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Test full flow from markdown to queries."""
        doc_repo = SQLiteDocumentRepository(manager)

        # Create document
        doc = SQLiteDocument(
            document_id="test-vault::meeting.md",
            vault_id=vault_id,
            file_path="meeting.md",
            file_name="meeting.md",
            content_hash="meeting",
        )
        doc_id = await doc_repo.create(doc)

        # Parse frontmatter
        content = """---
type: 1-1
participant: "[[vshadrin]]"
date: 2025-01-08
status: active
tags: [meeting, q1]
priority: 1
---

# Meeting Notes
"""
        result = parser.parse(content)

        # Store properties
        count = await repo.create_from_parsed(doc_id, result)
        assert count == 7

        # Query by exact value
        doc_ids = await repo.find_by_key_value(vault_id, "status", "active")
        assert doc_id in doc_ids

        # Query by link
        doc_ids = await repo.find_by_link_target(vault_id, "vshadrin")
        assert doc_id in doc_ids

        # Query by date
        doc_ids = await repo.find_by_date_range(
            vault_id, "date", after="2025-01-01", before="2025-01-31"
        )
        assert doc_id in doc_ids

        # Query by number
        doc_ids = await repo.find_by_number_range(vault_id, "priority", 1, 5)
        assert doc_id in doc_ids
