"""SQLite repositories for domain entities.

This module provides repository pattern implementations for:
- Vaults
- Documents
- Properties
- Tags
- Links
- Entities
"""

from obsidian_kb.storage.sqlite.repositories.base import BaseRepository
from obsidian_kb.storage.sqlite.repositories.document import (
    SQLiteDocument,
    SQLiteDocumentRepository,
)
from obsidian_kb.storage.sqlite.repositories.property import (
    DocumentProperty,
    PropertyRepository,
)
from obsidian_kb.storage.sqlite.repositories.vault import Vault, VaultRepository

__all__ = [
    "BaseRepository",
    "Vault",
    "VaultRepository",
    "SQLiteDocument",
    "SQLiteDocumentRepository",
    "DocumentProperty",
    "PropertyRepository",
]
