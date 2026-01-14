"""Модуль для валидации конфигурации и данных."""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from obsidian_kb.types import IndexingError, ObsidianKBError

logger = logging.getLogger(__name__)


class ValidationError(ObsidianKBError):
    """Ошибка валидации."""


def validate_vault_config(config_path: Path) -> list[dict[str, Any]]:
    """Валидация конфигурации vault'ов.

    Args:
        config_path: Путь к файлу конфигурации

    Returns:
        Список валидных vault'ов

    Raises:
        ValidationError: При ошибке валидации
    """
    if not config_path.exists():
        raise ValidationError(f"Конфигурационный файл не найден: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Ошибка парсинга JSON в {config_path}: {e}") from e
    except Exception as e:
        raise ValidationError(f"Ошибка чтения конфигурации: {e}") from e

    if not isinstance(config, dict):
        raise ValidationError("Конфигурация должна быть объектом JSON")

    vaults = config.get("vaults", [])
    if not isinstance(vaults, list):
        raise ValidationError("Поле 'vaults' должно быть массивом")

    validated_vaults = []
    errors = []

    for idx, vault in enumerate(vaults):
        if not isinstance(vault, dict):
            errors.append(f"Vault #{idx + 1}: должен быть объектом")
            continue

        vault_name = vault.get("name")
        vault_path = vault.get("path")

        if not vault_name:
            errors.append(f"Vault #{idx + 1}: отсутствует поле 'name'")
            continue

        if not vault_path:
            errors.append(f"Vault '{vault_name}': отсутствует поле 'path'")
            continue

        # Проверяем путь
        path_obj = Path(vault_path)
        if not path_obj.exists():
            errors.append(f"Vault '{vault_name}': путь не существует: {vault_path}")
            continue

        if not path_obj.is_dir():
            errors.append(f"Vault '{vault_name}': путь не является директорией: {vault_path}")
            continue

        # Проверяем доступность
        if not path_obj.is_absolute():
            logger.warning(f"Vault '{vault_name}': путь не абсолютный: {vault_path}")

        validated_vaults.append(vault)

    if errors and not validated_vaults:
        raise ValidationError("Все vault'ы невалидны:\n" + "\n".join(f"  - {e}" for e in errors))

    if errors:
        logger.warning("Найдены проблемы в конфигурации:\n" + "\n".join(f"  - {e}" for e in errors))

    return validated_vaults


def validate_vault_path(vault_path: Path, vault_name: str) -> None:
    """Валидация пути к vault'у.

    Args:
        vault_path: Путь к vault'у
        vault_name: Имя vault'а

    Raises:
        IndexingError: При ошибке валидации
    """
    path_obj = Path(vault_path).resolve()

    if not path_obj.exists():
        raise IndexingError(f"Vault '{vault_name}': путь не существует: {vault_path}")

    if not path_obj.is_dir():
        raise IndexingError(f"Vault '{vault_name}': путь не является директорией: {vault_path}")

        # Проверяем доступность на чтение
        if not os.access(path_obj, os.R_OK):
            raise IndexingError(f"Vault '{vault_name}': нет доступа на чтение: {vault_path}")


def validate_db_path(db_path: Path) -> None:
    """Валидация пути к базе данных.

    Args:
        db_path: Путь к базе данных

    Raises:
        ValidationError: При ошибке валидации
    """
    db_dir = db_path.parent

    # Проверяем, что родительская директория существует или может быть создана
    if not db_dir.exists():
        try:
            db_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValidationError(f"Не удалось создать директорию для БД: {db_dir}: {e}") from e

        # Проверяем доступность на запись
        if not os.access(db_dir, os.W_OK):
            raise ValidationError(f"Нет доступа на запись в директорию БД: {db_dir}")


def validate_search_params(
    query: str | None = None,
    vault_name: str | None = None,
    limit: int | None = None,
    search_type: str | None = None,
) -> None:
    """Валидация параметров поиска.
    
    Args:
        query: Поисковый запрос
        vault_name: Имя vault'а
        limit: Максимальное количество результатов
        search_type: Тип поиска (vector, fts, hybrid)
        
    Raises:
        ValidationError: При ошибке валидации
    """
    if query is not None:
        if not isinstance(query, str):
            raise ValidationError("Параметр 'query' должен быть строкой")
        if len(query.strip()) == 0:
            raise ValidationError("Параметр 'query' не может быть пустым")
        if len(query) > 10000:  # Разумный лимит для запроса
            raise ValidationError(f"Параметр 'query' слишком длинный (максимум 10000 символов, получено {len(query)})")
    
    if vault_name is not None:
        if not isinstance(vault_name, str):
            raise ValidationError("Параметр 'vault_name' должен быть строкой")
        if len(vault_name.strip()) == 0:
            raise ValidationError("Параметр 'vault_name' не может быть пустым")
        if len(vault_name) > 255:
            raise ValidationError("Параметр 'vault_name' слишком длинный (максимум 255 символов)")
    
    if limit is not None:
        if not isinstance(limit, int):
            raise ValidationError("Параметр 'limit' должен быть целым числом")
        if limit < 1:
            raise ValidationError("Параметр 'limit' должен быть больше 0")
        if limit > 1000:  # Разумный лимит для результатов
            raise ValidationError(f"Параметр 'limit' слишком большой (максимум 1000, получено {limit})")
    
    if search_type is not None:
        valid_types = {"vector", "fts", "hybrid"}
        if search_type not in valid_types:
            raise ValidationError(f"Параметр 'search_type' должен быть одним из: {', '.join(valid_types)}")


def validate_date_format(date_str: str) -> None:
    """Валидация формата даты.
    
    Args:
        date_str: Строка с датой
        
    Raises:
        ValidationError: При ошибке валидации
    """
    if not isinstance(date_str, str):
        raise ValidationError("Дата должна быть строкой")
    
    if not date_str.strip():
        raise ValidationError("Дата не может быть пустой")
    
    # Проверяем основные форматы дат
    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}$',  # YYYY-MM-DD HH:MM:SS
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO 8601
        r'^\d{2}\.\d{2}\.\d{4}$',  # DD.MM.YYYY
        r'^\d{2}/\d{2}/\d{4}$',  # DD/MM/YYYY или MM/DD/YYYY
    ]
    
    matches = any(re.match(pattern, date_str.strip()) for pattern in date_patterns)
    
    if not matches:
        # Пробуем распарсить как ISO формат или timestamp
        try:
            datetime.fromisoformat(date_str.replace(' ', 'T', 1))
        except (ValueError, AttributeError):
            try:
                float(date_str)  # Проверяем timestamp
            except ValueError:
                raise ValidationError(f"Невалидный формат даты: {date_str}. Ожидается YYYY-MM-DD, ISO 8601 или timestamp")


def validate_batch_size(batch_size: int, max_batch_size: int = 1000) -> None:
    """Валидация размера батча.
    
    Args:
        batch_size: Размер батча
        max_batch_size: Максимальный размер батча
        
    Raises:
        ValidationError: При ошибке валидации
    """
    if not isinstance(batch_size, int):
        raise ValidationError("Размер батча должен быть целым числом")
    
    if batch_size < 1:
        raise ValidationError("Размер батча должен быть больше 0")
    
    if batch_size > max_batch_size:
        raise ValidationError(f"Размер батча слишком большой (максимум {max_batch_size}, получено {batch_size})")


def validate_filter_value(filter_type: str, value: str) -> None:
    """Валидация значения фильтра.
    
    Args:
        filter_type: Тип фильтра (type, tags, links, created, modified)
        value: Значение фильтра
        
    Raises:
        ValidationError: При ошибке валидации
    """
    if not isinstance(value, str):
        raise ValidationError(f"Значение фильтра '{filter_type}' должно быть строкой")
    
    if not value.strip():
        raise ValidationError(f"Значение фильтра '{filter_type}' не может быть пустым")
    
    # Валидация для дат
    if filter_type in ("created", "modified"):
        # Проверяем формат даты (может быть с оператором: >2024-01-01)
        date_part = value
        if value.startswith((">=", "<=")):
            date_part = value[2:]
        elif value.startswith((">", "<", "=")):
            date_part = value[1:]
        
        validate_date_format(date_part)
    
    # Валидация длины для других типов
    if filter_type in ("type", "tags", "links"):
        if len(value) > 500:
            raise ValidationError(f"Значение фильтра '{filter_type}' слишком длинное (максимум 500 символов)")

