"""Система управления конфигурацией для obsidian-kb.

Поддерживает:
- Глобальную конфигурацию
- Vault-specific конфигурацию
- Пресеты конфигурации
- Персистентное хранение в YAML
"""

from obsidian_kb.config.manager import ConfigManager, get_config_manager, reset_config_manager
from obsidian_kb.config.schema import (
    EnrichmentConfig,
    IndexingConfig,
    ProviderConfig,
    VaultConfig,
)
# Импортируем Settings и settings из модуля config.py (не из пакета config)
import sys
import importlib.util
from pathlib import Path

# Импортируем напрямую из config.py файла
_config_path = Path(__file__).parent.parent / "config.py"
if _config_path.exists():
    spec = importlib.util.spec_from_file_location("obsidian_kb.config_module", _config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    Settings = config_module.Settings
    settings = config_module.settings
else:
    # Fallback: пробуем импортировать через относительный импорт
    from ..config import Settings, settings

__all__ = [
    "ConfigManager",
    "get_config_manager",
    "reset_config_manager",
    "IndexingConfig",
    "EnrichmentConfig",
    "ProviderConfig",
    "VaultConfig",
    "Settings",
    "settings",
]

