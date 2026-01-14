"""Менеджер конфигурации с персистентностью.

Управляет глобальной и vault-specific конфигурацией с приоритетами:
vault-specific > global > defaults
"""

import logging
from pathlib import Path
from typing import Any, Literal, get_args, get_origin

import yaml

from obsidian_kb.config.presets import ConfigPresets
from obsidian_kb.config.schema import VaultConfig

logger = logging.getLogger(__name__)

# Глобальный singleton экземпляр ConfigManager
_config_manager_instance: "ConfigManager | None" = None


def get_config_manager() -> "ConfigManager":
    """Получение глобального singleton экземпляра ConfigManager.

    Используйте эту функцию вместо создания новых экземпляров ConfigManager,
    чтобы все части системы работали с одним и тем же кэшем конфигурации.

    Returns:
        Единственный экземпляр ConfigManager
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance


def reset_config_manager() -> None:
    """Сброс singleton экземпляра ConfigManager.

    Используется в тестах для изоляции между тестами.
    В production коде обычно не требуется.
    """
    global _config_manager_instance
    _config_manager_instance = None


class ConfigManager:
    """Менеджер конфигурации.
    
    Хранит:
    - Глобальную конфигурацию (~/.obsidian-kb/config.yaml)
    - Vault-specific конфигурацию (~/.obsidian-kb/vaults/{name}/config.yaml)
    
    Приоритет: vault-specific > global > defaults
    
    Пример использования:
        manager = ConfigManager()
        config = manager.get_config("my-vault")
        manager.set_config("indexing.chunk_size", "1000", vault_name="my-vault")
    """
    
    def __init__(self, base_path: Path | None = None) -> None:
        """Инициализация менеджера конфигурации.
        
        Args:
            base_path: Базовый путь для хранения конфигурации
                      (по умолчанию ~/.obsidian-kb)
        """
        self._base_path = base_path or Path.home() / ".obsidian-kb"
        self._global_config_path = self._base_path / "config.yaml"
        self._vaults_config_dir = self._base_path / "vaults"
        
        # Кэш конфигураций
        self._global_config: VaultConfig | None = None
        self._vault_configs: dict[str, VaultConfig] = {}
        
        # Создаём директории если их нет
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._vaults_config_dir.mkdir(parents=True, exist_ok=True)
    
    def get_config(self, vault_name: str | None = None) -> VaultConfig:
        """Получение конфигурации с учётом приоритетов.
        
        Приоритет (от высшего к низшему):
        1. Vault-specific конфигурация (если vault_name указан)
        2. Глобальная конфигурация
        3. Значения по умолчанию
        
        Args:
            vault_name: Имя vault'а (None для глобальной конфигурации)
            
        Returns:
            VaultConfig с объединёнными настройками
        """
        # Загружаем глобальную конфигурацию
        global_config = self._load_global_config()
        
        # Если vault_name не указан, возвращаем глобальную
        if vault_name is None:
            return global_config
        
        # Загружаем vault-specific конфигурацию
        vault_config = self._load_vault_config(vault_name)
        
        # Объединяем конфигурации (vault-specific перезаписывает global)
        return self._merge_configs(global_config, vault_config)
    
    def set_config(
        self,
        key: str,
        value: str,
        vault_name: str | None = None,
    ) -> None:
        """Установка параметра конфигурации.
        
        Поддерживает dot-notation для вложенных параметров:
        - "indexing.chunk_size" -> indexing.chunk_size
        - "enrichment.strategy" -> enrichment.strategy
        - "providers.embedding" -> providers.embedding
        
        Args:
            key: Ключ параметра в dot-notation
            value: Новое значение (строка, будет преобразована в нужный тип)
            vault_name: Применить к vault'у (None = глобально)
            
        Raises:
            ValueError: Если ключ невалиден или значение не может быть преобразовано
        """
        # Парсим ключ
        parts = key.split(".")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid config key format: {key}. "
                f"Expected format: 'section.parameter' (e.g., 'indexing.chunk_size')"
            )
        
        section, param = parts
        
        # Определяем конфигурацию для изменения
        if vault_name:
            config = self._load_vault_config(vault_name)
            config_path = self._vaults_config_dir / vault_name / "config.yaml"
        else:
            config = self._load_global_config()
            config_path = self._global_config_path
        
        # Устанавливаем значение
        self._set_nested_value(config, section, param, value)
        
        # Сохраняем конфигурацию
        self._save_config(config, config_path)
        
        # Инвалидируем кэш
        if vault_name:
            self._vault_configs.pop(vault_name, None)
        else:
            self._global_config = None
        
        logger.info(
            f"Config updated: {key} = {value} "
            f"({'vault: ' + vault_name if vault_name else 'global'})"
        )
    
    def apply_preset(
        self,
        preset_name: str,
        vault_name: str | None = None,
    ) -> VaultConfig:
        """Применение пресета конфигурации.
        
        Args:
            preset_name: Имя пресета (fast, balanced, quality, local, cloud)
            vault_name: Применить к vault'у (None = глобально)
            
        Returns:
            Применённая конфигурация
            
        Raises:
            ValueError: Если пресет не найден
        """
        preset = ConfigPresets.get_preset(preset_name)
        
        # Определяем путь для сохранения
        if vault_name:
            config_path = self._vaults_config_dir / vault_name / "config.yaml"
            config_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            config_path = self._global_config_path
        
        # Сохраняем пресет
        self._save_config(preset, config_path)
        
        # Инвалидируем кэш
        if vault_name:
            self._vault_configs.pop(vault_name, None)
        else:
            self._global_config = None
        
        logger.info(
            f"Preset '{preset_name}' applied "
            f"({'to vault: ' + vault_name if vault_name else 'globally'})"
        )
        
        return preset
    
    def _load_global_config(self) -> VaultConfig:
        """Загрузка глобальной конфигурации."""
        if self._global_config is not None:
            return self._global_config
        
        if self._global_config_path.exists():
            try:
                with open(self._global_config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                self._global_config = VaultConfig(**data)
            except Exception as e:
                logger.warning(f"Failed to load global config: {e}, using defaults")
                self._global_config = VaultConfig()
        else:
            self._global_config = VaultConfig()
        
        return self._global_config
    
    def _load_vault_config(self, vault_name: str) -> VaultConfig:
        """Загрузка vault-specific конфигурации."""
        if vault_name in self._vault_configs:
            return self._vault_configs[vault_name]
        
        config_path = self._vaults_config_dir / vault_name / "config.yaml"
        
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                config = VaultConfig(**data)
            except Exception as e:
                logger.warning(
                    f"Failed to load vault config for '{vault_name}': {e}, "
                    "using empty config"
                )
                config = VaultConfig()
        else:
            config = VaultConfig()
        
        self._vault_configs[vault_name] = config
        return config
    
    def _merge_configs(
        self,
        base: VaultConfig,
        override: VaultConfig,
    ) -> VaultConfig:
        """Объединение конфигураций (override перезаписывает base).
        
        Использует model_dump и model_validate для глубокого объединения.
        """
        base_dict = base.model_dump(exclude_unset=True)
        override_dict = override.model_dump(exclude_unset=True)
        
        # Рекурсивное объединение словарей
        merged = self._deep_merge(base_dict, override_dict)
        
        return VaultConfig(**merged)
    
    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Рекурсивное объединение словарей."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _set_nested_value(
        self,
        config: VaultConfig,
        section: str,
        param: str,
        value: str,
    ) -> None:
        """Установка значения во вложенном объекте конфигурации.
        
        Args:
            config: Объект конфигурации
            section: Секция (indexing, enrichment, providers, search)
            param: Параметр внутри секции
            value: Значение (строка, будет преобразована)
            
        Raises:
            ValueError: Если секция или параметр не найдены
        """
        # Получаем секцию
        if not hasattr(config, section):
            raise ValueError(
                f"Unknown config section: {section}. "
                f"Available: indexing, enrichment, providers, search"
            )
        
        section_obj = getattr(config, section)
        
        # Проверяем, что параметр существует
        # Используем type() для доступа к model_fields через класс (Pydantic v3 compatibility)
        section_class = type(section_obj)
        if not hasattr(section_obj, param):
            raise ValueError(
                f"Unknown parameter '{param}' in section '{section}'. "
                f"Available: {', '.join(section_class.model_fields.keys())}"
            )

        # Преобразуем значение в нужный тип
        field_info = section_class.model_fields[param]
        field_type = field_info.annotation
        
        # Парсим значение
        parsed_value = self._parse_value(value, field_type)
        
        # Устанавливаем значение
        setattr(section_obj, param, parsed_value)
    
    def _parse_value(self, value: str, target_type: type) -> Any:
        """Парсинг строкового значения в нужный тип.
        
        Args:
            value: Строковое значение
            target_type: Целевой тип
            
        Returns:
            Преобразованное значение
        """
        # Обработка Union типов (например, str | None)
        origin = get_origin(target_type)
        if origin is not None:
            # Union, Optional или Literal
            args = get_args(target_type)
            
            # Literal - проверяем, что значение входит в допустимые
            if origin is Literal:
                if value not in args:
                    raise ValueError(
                        f"Invalid value '{value}' for Literal type. "
                        f"Allowed values: {', '.join(str(a) for a in args)}"
                    )
                return value
            
            # Optional (Union[T, None])
            if type(None) in args:
                # Берём первый не-None тип
                non_none_args = [a for a in args if a is not type(None)]
                if non_none_args:
                    target_type = non_none_args[0]
                    # Рекурсивно обрабатываем новый тип
                    return self._parse_value(value, target_type)
        
        # Преобразование по типу
        if target_type == bool:
            return value.lower() in ("true", "1", "yes", "on")
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == str:
            return value
        else:
            # Для enum и других типов пробуем использовать значение как есть
            return value
    
    def _save_config(self, config: VaultConfig, config_path: Path) -> None:
        """Сохранение конфигурации в YAML файл.

        Args:
            config: Конфигурация для сохранения
            config_path: Путь к файлу
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Конвертируем в словарь, исключая None значения для Optional полей
        # НЕ используем exclude_unset, так как setattr не помечает поля как "set"
        # mode='json' обеспечивает правильную сериализацию Enum в строку
        data = config.model_dump(exclude_none=False, exclude_defaults=False, mode="json")

        # Удаляем пустые вложенные словари и None значения для Optional полей
        data = self._clean_config_dict(data)

        # Сохраняем в YAML
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )

    def _clean_config_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Очистка словаря конфигурации от пустых значений.

        Удаляет:
        - None значения (Optional поля не установлены)
        - Пустые словари

        Args:
            data: Словарь конфигурации

        Returns:
            Очищенный словарь
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                cleaned = self._clean_config_dict(value)
                if cleaned:  # Не добавляем пустые словари
                    result[key] = cleaned
            elif value is not None:
                result[key] = value
        return result

