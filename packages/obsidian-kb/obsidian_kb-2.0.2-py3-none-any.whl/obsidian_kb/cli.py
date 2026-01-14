"""CLI интерфейс для obsidian-kb.

DEPRECATED: This module is a redirect to the new modular CLI structure.
Use `from obsidian_kb.cli import cli, main` instead.

This file is kept for backward compatibility with existing entry points
defined in pyproject.toml.
"""

# Redirect to new modular CLI
from obsidian_kb.cli import cli, main

__all__ = ["cli", "main"]

if __name__ == "__main__":
    main()
