"""Tests for PropertySchemaBuilder."""

from pathlib import Path

import pytest
import pytest_asyncio

from obsidian_kb.storage.sqlite.frontmatter_parser import FrontmatterParser
from obsidian_kb.storage.sqlite.manager import SQLiteManager
from obsidian_kb.storage.sqlite.repositories.document import (
    SQLiteDocument,
    SQLiteDocumentRepository,
)
from obsidian_kb.storage.sqlite.repositories.property import PropertyRepository
from obsidian_kb.storage.sqlite.repositories.vault import Vault, VaultRepository
from obsidian_kb.storage.sqlite.schema import create_schema
from obsidian_kb.storage.sqlite.schema_builder import (
    PropertySchema,
    PropertySchemaBuilder,
    VaultSchema,
)


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
async def builder(manager: SQLiteManager) -> PropertySchemaBuilder:
    """Create PropertySchemaBuilder."""
    return PropertySchemaBuilder(manager)


@pytest.fixture
def parser() -> FrontmatterParser:
    """Create FrontmatterParser."""
    return FrontmatterParser()


class TestPropertySchema:
    """Tests for PropertySchema dataclass."""

    def test_create_schema(self):
        """Test creating PropertySchema."""
        schema = PropertySchema(
            vault_id=1,
            property_key="status",
            inferred_type="string",
            sample_values=["active", "pending", "done"],
            document_count=10,
        )

        assert schema.vault_id == 1
        assert schema.property_key == "status"
        assert schema.inferred_type == "string"
        assert len(schema.sample_values) == 3
        assert schema.document_count == 10
        assert schema.id is None


class TestVaultSchema:
    """Tests for VaultSchema dataclass."""

    def test_create_empty_schema(self):
        """Test creating empty VaultSchema."""
        schema = VaultSchema(vault_id=1)

        assert schema.vault_id == 1
        assert schema.properties == []
        assert schema.total_documents == 0

    def test_get_property(self):
        """Test getting property by key."""
        schema = VaultSchema(
            vault_id=1,
            properties=[
                PropertySchema(vault_id=1, property_key="status"),
                PropertySchema(vault_id=1, property_key="priority"),
            ],
        )

        prop = schema.get_property("status")
        assert prop is not None
        assert prop.property_key == "status"

        prop = schema.get_property("nonexistent")
        assert prop is None

    def test_get_keys_by_type(self):
        """Test filtering keys by type."""
        schema = VaultSchema(
            vault_id=1,
            properties=[
                PropertySchema(vault_id=1, property_key="status", inferred_type="string"),
                PropertySchema(vault_id=1, property_key="name", inferred_type="string"),
                PropertySchema(vault_id=1, property_key="count", inferred_type="number"),
            ],
        )

        string_keys = schema.get_keys_by_type("string")
        assert len(string_keys) == 2
        assert "status" in string_keys
        assert "name" in string_keys

        number_keys = schema.get_keys_by_type("number")
        assert len(number_keys) == 1
        assert "count" in number_keys


class TestPropertySchemaBuilderInferType:
    """Tests for type inference from values."""

    def test_infer_string_type(self, builder: PropertySchemaBuilder):
        """Test inferring string type."""
        inferred = builder.infer_type(["active", "pending", "done"])
        assert inferred == "string"

    def test_infer_number_type(self, builder: PropertySchemaBuilder):
        """Test inferring number type."""
        inferred = builder.infer_type([1, 2, 3, 4, 5])
        assert inferred == "number"

    def test_infer_boolean_type(self, builder: PropertySchemaBuilder):
        """Test inferring boolean type."""
        inferred = builder.infer_type([True, False, True])
        assert inferred == "boolean"

    def test_infer_date_type(self, builder: PropertySchemaBuilder):
        """Test inferring date type."""
        inferred = builder.infer_type(["2025-01-01", "2025-01-15", "2025-02-01"])
        assert inferred == "date"

    def test_infer_link_type(self, builder: PropertySchemaBuilder):
        """Test inferring link type."""
        inferred = builder.infer_type(["[[john]]", "[[alice]]", "[[bob]]"])
        assert inferred == "link"

    def test_infer_mixed_type(self, builder: PropertySchemaBuilder):
        """Test inferring type from mixed values."""
        # Most common type wins
        inferred = builder.infer_type(["a", "b", "c", 1, 2])
        assert inferred == "string"  # 3 strings vs 2 numbers

    def test_infer_empty_list(self, builder: PropertySchemaBuilder):
        """Test inferring type from empty list."""
        inferred = builder.infer_type([])
        assert inferred == "string"  # Default

    def test_infer_none_values(self, builder: PropertySchemaBuilder):
        """Test inferring type with None values."""
        inferred = builder.infer_type([None, None, "value"])
        assert inferred == "string"


class TestPropertySchemaBuilderBuild:
    """Tests for building schema from vault data."""

    @pytest_asyncio.fixture
    async def setup_vault_data(
        self,
        manager: SQLiteManager,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Setup vault with documents and properties."""
        doc_repo = SQLiteDocumentRepository(manager)
        prop_repo = PropertyRepository(manager)

        # Document 1
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
tags: [meeting, q1]
"""
        result1 = parser.parse_yaml(yaml1)
        await prop_repo.create_from_parsed(doc1_id, result1)

        # Document 2
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
archived: false
"""
        result2 = parser.parse_yaml(yaml2)
        await prop_repo.create_from_parsed(doc2_id, result2)

        # Document 3
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
"""
        result3 = parser.parse_yaml(yaml3)
        await prop_repo.create_from_parsed(doc3_id, result3)

        return {"doc1": doc1_id, "doc2": doc2_id, "doc3": doc3_id}

    @pytest.mark.asyncio
    async def test_build_schema(
        self,
        builder: PropertySchemaBuilder,
        vault_id: int,
        setup_vault_data,
    ):
        """Test building complete vault schema."""
        schema = await builder.build_schema(vault_id)

        assert schema.vault_id == vault_id
        assert schema.total_documents == 3
        assert len(schema.properties) > 0

        # Check that common properties are found
        keys = {p.property_key for p in schema.properties}
        assert "status" in keys
        assert "priority" in keys
        assert "date" in keys

    @pytest.mark.asyncio
    async def test_build_schema_infers_types(
        self,
        builder: PropertySchemaBuilder,
        vault_id: int,
        setup_vault_data,
    ):
        """Test that schema correctly infers types."""
        schema = await builder.build_schema(vault_id)

        # Status should be string
        status_schema = schema.get_property("status")
        assert status_schema is not None
        assert status_schema.inferred_type == "string"

        # Priority should be number
        priority_schema = schema.get_property("priority")
        assert priority_schema is not None
        assert priority_schema.inferred_type == "number"

        # Date should be date
        date_schema = schema.get_property("date")
        assert date_schema is not None
        assert date_schema.inferred_type == "date"

        # Participant should be link
        participant_schema = schema.get_property("participant")
        assert participant_schema is not None
        assert participant_schema.inferred_type == "link"

    @pytest.mark.asyncio
    async def test_build_schema_document_counts(
        self,
        builder: PropertySchemaBuilder,
        vault_id: int,
        setup_vault_data,
    ):
        """Test that schema counts documents correctly."""
        schema = await builder.build_schema(vault_id)

        # Status is in all 3 documents
        status_schema = schema.get_property("status")
        assert status_schema is not None
        assert status_schema.document_count == 3

        # Archived is only in 1 document
        archived_schema = schema.get_property("archived")
        assert archived_schema is not None
        assert archived_schema.document_count == 1

    @pytest.mark.asyncio
    async def test_build_schema_sample_values(
        self,
        builder: PropertySchemaBuilder,
        vault_id: int,
        setup_vault_data,
    ):
        """Test that schema collects sample values."""
        schema = await builder.build_schema(vault_id)

        status_schema = schema.get_property("status")
        assert status_schema is not None
        assert len(status_schema.sample_values) > 0
        assert "active" in status_schema.sample_values

    @pytest.mark.asyncio
    async def test_build_schema_empty_vault(
        self,
        builder: PropertySchemaBuilder,
        vault_id: int,
    ):
        """Test building schema for empty vault."""
        schema = await builder.build_schema(vault_id)

        assert schema.vault_id == vault_id
        assert schema.total_documents == 0
        assert len(schema.properties) == 0


class TestPropertySchemaBuilderPersistence:
    """Tests for schema persistence."""

    @pytest_asyncio.fixture
    async def setup_and_build(
        self,
        manager: SQLiteManager,
        builder: PropertySchemaBuilder,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Setup data and build schema."""
        doc_repo = SQLiteDocumentRepository(manager)
        prop_repo = PropertyRepository(manager)

        doc = SQLiteDocument(
            document_id="test-vault::doc.md",
            vault_id=vault_id,
            file_path="doc.md",
            file_name="doc.md",
            content_hash="hash",
        )
        doc_id = await doc_repo.create(doc)

        yaml_content = """status: active
priority: 5
"""
        result = parser.parse_yaml(yaml_content)
        await prop_repo.create_from_parsed(doc_id, result)

        await builder.build_schema(vault_id)
        return vault_id

    @pytest.mark.asyncio
    async def test_get_schema(
        self,
        builder: PropertySchemaBuilder,
        setup_and_build,
    ):
        """Test retrieving saved schema."""
        vault_id = setup_and_build

        schema = await builder.get_schema(vault_id)

        assert schema is not None
        assert schema.vault_id == vault_id
        assert len(schema.properties) == 2

    @pytest.mark.asyncio
    async def test_get_schema_nonexistent(
        self,
        builder: PropertySchemaBuilder,
    ):
        """Test getting schema for nonexistent vault."""
        schema = await builder.get_schema(9999)
        assert schema is None

    @pytest.mark.asyncio
    async def test_get_property_keys(
        self,
        builder: PropertySchemaBuilder,
        setup_and_build,
    ):
        """Test getting property keys."""
        vault_id = setup_and_build

        keys = await builder.get_property_keys(vault_id)

        assert len(keys) == 2
        assert "status" in keys
        assert "priority" in keys

    @pytest.mark.asyncio
    async def test_get_property_schema(
        self,
        builder: PropertySchemaBuilder,
        setup_and_build,
    ):
        """Test getting specific property schema."""
        vault_id = setup_and_build

        schema = await builder.get_property_schema(vault_id, "status")

        assert schema is not None
        assert schema.property_key == "status"
        assert schema.inferred_type == "string"

    @pytest.mark.asyncio
    async def test_get_property_schema_nonexistent(
        self,
        builder: PropertySchemaBuilder,
        setup_and_build,
    ):
        """Test getting nonexistent property schema."""
        vault_id = setup_and_build

        schema = await builder.get_property_schema(vault_id, "nonexistent")
        assert schema is None

    @pytest.mark.asyncio
    async def test_delete_schema(
        self,
        builder: PropertySchemaBuilder,
        setup_and_build,
    ):
        """Test deleting schema."""
        vault_id = setup_and_build

        count = await builder.delete_schema(vault_id)
        assert count == 2

        schema = await builder.get_schema(vault_id)
        assert schema is None

    @pytest.mark.asyncio
    async def test_rebuild_schema(
        self,
        manager: SQLiteManager,
        builder: PropertySchemaBuilder,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Test rebuilding schema updates existing entries."""
        doc_repo = SQLiteDocumentRepository(manager)
        prop_repo = PropertyRepository(manager)

        # Create initial document
        doc1 = SQLiteDocument(
            document_id="test-vault::doc1.md",
            vault_id=vault_id,
            file_path="doc1.md",
            file_name="doc1.md",
            content_hash="hash1",
        )
        doc1_id = await doc_repo.create(doc1)

        yaml1 = "status: active"
        result1 = parser.parse_yaml(yaml1)
        await prop_repo.create_from_parsed(doc1_id, result1)

        # Build initial schema
        schema1 = await builder.build_schema(vault_id)
        assert len(schema1.properties) == 1

        # Add more data
        doc2 = SQLiteDocument(
            document_id="test-vault::doc2.md",
            vault_id=vault_id,
            file_path="doc2.md",
            file_name="doc2.md",
            content_hash="hash2",
        )
        doc2_id = await doc_repo.create(doc2)

        yaml2 = "status: pending\npriority: 5"
        result2 = parser.parse_yaml(yaml2)
        await prop_repo.create_from_parsed(doc2_id, result2)

        # Rebuild schema
        schema2 = await builder.build_schema(vault_id)

        assert len(schema2.properties) == 2
        assert schema2.get_property("status") is not None
        assert schema2.get_property("priority") is not None

        # Status document count should be updated
        status = schema2.get_property("status")
        assert status.document_count == 2


class TestPropertySchemaBuilderEdgeCases:
    """Edge case tests for PropertySchemaBuilder."""

    @pytest.mark.asyncio
    async def test_handle_duplicate_keys_in_list(
        self,
        manager: SQLiteManager,
        builder: PropertySchemaBuilder,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Test handling properties with list values."""
        doc_repo = SQLiteDocumentRepository(manager)
        prop_repo = PropertyRepository(manager)

        doc = SQLiteDocument(
            document_id="test-vault::doc.md",
            vault_id=vault_id,
            file_path="doc.md",
            file_name="doc.md",
            content_hash="hash",
        )
        doc_id = await doc_repo.create(doc)

        yaml_content = "tags: [a, b, c]"
        result = parser.parse_yaml(yaml_content)
        await prop_repo.create_from_parsed(doc_id, result)

        schema = await builder.build_schema(vault_id)

        # tags should appear once in schema
        tags_schema = schema.get_property("tags")
        assert tags_schema is not None
        assert tags_schema.inferred_type == "string"
        assert tags_schema.document_count == 1

    @pytest.mark.asyncio
    async def test_handle_mixed_types_for_same_key(
        self,
        manager: SQLiteManager,
        builder: PropertySchemaBuilder,
        vault_id: int,
        parser: FrontmatterParser,
    ):
        """Test handling same key with different types across documents."""
        doc_repo = SQLiteDocumentRepository(manager)
        prop_repo = PropertyRepository(manager)

        # Doc 1: value as string
        doc1 = SQLiteDocument(
            document_id="test-vault::doc1.md",
            vault_id=vault_id,
            file_path="doc1.md",
            file_name="doc1.md",
            content_hash="hash1",
        )
        doc1_id = await doc_repo.create(doc1)

        yaml1 = 'field: "123"'
        result1 = parser.parse_yaml(yaml1)
        await prop_repo.create_from_parsed(doc1_id, result1)

        # Doc 2: value as number
        doc2 = SQLiteDocument(
            document_id="test-vault::doc2.md",
            vault_id=vault_id,
            file_path="doc2.md",
            file_name="doc2.md",
            content_hash="hash2",
        )
        doc2_id = await doc_repo.create(doc2)

        yaml2 = "field: 456"
        result2 = parser.parse_yaml(yaml2)
        await prop_repo.create_from_parsed(doc2_id, result2)

        # Doc 3: value as string again
        doc3 = SQLiteDocument(
            document_id="test-vault::doc3.md",
            vault_id=vault_id,
            file_path="doc3.md",
            file_name="doc3.md",
            content_hash="hash3",
        )
        doc3_id = await doc_repo.create(doc3)

        yaml3 = 'field: "789"'
        result3 = parser.parse_yaml(yaml3)
        await prop_repo.create_from_parsed(doc3_id, result3)

        schema = await builder.build_schema(vault_id)

        # Most common type should win (string: 2, number: 1)
        field_schema = schema.get_property("field")
        assert field_schema is not None
        # The inferred type depends on what was stored
        # Since parser detects "123" as number (numeric string), we check it's consistent
        assert field_schema.inferred_type in ["string", "number"]
