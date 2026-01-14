"""Тесты для модуля валидации."""

import json
from pathlib import Path

import pytest

from obsidian_kb.validation import (
    ValidationError,
    validate_batch_size,
    validate_date_format,
    validate_filter_value,
    validate_search_params,
    validate_db_path,
    validate_vault_config,
    validate_vault_path,
)


def test_validate_vault_config_success(tmp_path):
    """Тест успешной валидации конфигурации vault'ов."""
    config_path = tmp_path / "vaults.json"
    vault_dir = tmp_path / "test_vault"
    vault_dir.mkdir()

    config = {
        "vaults": [
            {"name": "test_vault", "path": str(vault_dir)},
        ]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    validated = validate_vault_config(config_path)
    assert len(validated) == 1
    assert validated[0]["name"] == "test_vault"


def test_validate_vault_config_not_found(tmp_path):
    """Тест валидации несуществующего конфига."""
    config_path = tmp_path / "nonexistent.json"

    with pytest.raises(ValidationError, match="не найден"):
        validate_vault_config(config_path)


def test_validate_vault_config_invalid_json(tmp_path):
    """Тест валидации невалидного JSON."""
    config_path = tmp_path / "vaults.json"
    config_path.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(ValidationError, match="парсинга JSON"):
        validate_vault_config(config_path)


def test_validate_vault_config_missing_name(tmp_path):
    """Тест валидации vault'а без имени."""
    config_path = tmp_path / "vaults.json"
    vault_dir = tmp_path / "test_vault"
    vault_dir.mkdir()

    config = {
        "vaults": [
            {"path": str(vault_dir)},  # Нет name
        ]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match="отсутствует поле 'name'"):
        validate_vault_config(config_path)


def test_validate_vault_config_missing_path(tmp_path):
    """Тест валидации vault'а без пути."""
    config_path = tmp_path / "vaults.json"

    config = {
        "vaults": [
            {"name": "test_vault"},  # Нет path
        ]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match="отсутствует поле 'path'"):
        validate_vault_config(config_path)


def test_validate_vault_config_nonexistent_path(tmp_path):
    """Тест валидации vault'а с несуществующим путём."""
    config_path = tmp_path / "vaults.json"

    config = {
        "vaults": [
            {"name": "test_vault", "path": "/nonexistent/path"},
        ]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match="путь не существует"):
        validate_vault_config(config_path)


def test_validate_vault_config_not_directory(tmp_path):
    """Тест валидации vault'а с путём к файлу вместо директории."""
    config_path = tmp_path / "vaults.json"
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test", encoding="utf-8")

    config = {
        "vaults": [
            {"name": "test_vault", "path": str(test_file)},
        ]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match="не является директорией"):
        validate_vault_config(config_path)


def test_validate_vault_config_partial_errors(tmp_path, caplog):
    """Тест валидации с частичными ошибками (некоторые vault'ы валидны)."""
    config_path = tmp_path / "vaults.json"
    valid_vault = tmp_path / "valid_vault"
    valid_vault.mkdir()

    config = {
        "vaults": [
            {"name": "valid_vault", "path": str(valid_vault)},
            {"name": "invalid_vault", "path": "/nonexistent"},
        ]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    validated = validate_vault_config(config_path)
    assert len(validated) == 1
    assert validated[0]["name"] == "valid_vault"
    assert "invalid_vault" in caplog.text


def test_validate_vault_path_success(tmp_path):
    """Тест успешной валидации пути vault'а."""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()

    # Не должно быть исключения
    validate_vault_path(vault_path, "test_vault")


def test_validate_vault_path_not_exists(tmp_path):
    """Тест валидации несуществующего пути."""
    vault_path = tmp_path / "nonexistent"

    with pytest.raises(Exception, match="не существует"):
        validate_vault_path(vault_path, "test_vault")


def test_validate_vault_path_not_directory(tmp_path):
    """Тест валидации пути к файлу."""
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test", encoding="utf-8")

    with pytest.raises(Exception, match="не является директорией"):
        validate_vault_path(test_file, "test_vault")


def test_validate_db_path_success(tmp_path):
    """Тест успешной валидации пути к БД."""
    db_path = tmp_path / "test_db" / "database.lance"

    # Не должно быть исключения
    validate_db_path(db_path)
    assert db_path.parent.exists()


def test_validate_db_path_creates_directory(tmp_path):
    """Тест создания директории для БД."""
    db_path = tmp_path / "new_dir" / "database.lance"

    validate_db_path(db_path)
    assert db_path.parent.exists()
    assert db_path.parent.is_dir()


class TestSearchParamsValidation:
    """Тесты для валидации параметров поиска."""
    
    def test_validate_search_params_success(self):
        """Тест успешной валидации параметров поиска."""
        validate_search_params(
            query="test query",
            vault_name="test_vault",
            limit=10,
            search_type="hybrid"
        )
    
    def test_validate_search_params_empty_query(self):
        """Тест валидации пустого запроса."""
        with pytest.raises(ValidationError, match="не может быть пустым"):
            validate_search_params(query="")
    
    def test_validate_search_params_query_too_long(self):
        """Тест валидации слишком длинного запроса."""
        long_query = "x" * 10001
        with pytest.raises(ValidationError, match="слишком длинный"):
            validate_search_params(query=long_query)
    
    def test_validate_search_params_invalid_limit(self):
        """Тест валидации невалидного лимита."""
        with pytest.raises(ValidationError, match="должен быть больше 0"):
            validate_search_params(limit=0)
        
        with pytest.raises(ValidationError, match="слишком большой"):
            validate_search_params(limit=1001)
    
    def test_validate_search_params_invalid_search_type(self):
        """Тест валидации невалидного типа поиска."""
        with pytest.raises(ValidationError, match="должен быть одним из"):
            validate_search_params(search_type="invalid")
    
    def test_validate_search_params_empty_vault_name(self):
        """Тест валидации пустого имени vault'а."""
        with pytest.raises(ValidationError, match="не может быть пустым"):
            validate_search_params(vault_name="")


class TestDateValidation:
    """Тесты для валидации форматов дат."""
    
    def test_validate_date_format_iso(self):
        """Тест валидации ISO формата даты."""
        validate_date_format("2024-01-01")
        validate_date_format("2024-01-01T10:30:00")
        validate_date_format("2024-01-01 10:30:00")
    
    def test_validate_date_format_alternative(self):
        """Тест валидации альтернативных форматов дат."""
        validate_date_format("01.01.2024")
        validate_date_format("01/01/2024")
    
    def test_validate_date_format_empty(self):
        """Тест валидации пустой даты."""
        with pytest.raises(ValidationError, match="не может быть пустой"):
            validate_date_format("")
    
    def test_validate_date_format_invalid(self):
        """Тест валидации невалидной даты."""
        with pytest.raises(ValidationError, match="Невалидный формат даты"):
            validate_date_format("invalid-date")


class TestFilterValidation:
    """Тесты для валидации значений фильтров."""
    
    def test_validate_filter_value_date(self):
        """Тест валидации фильтра даты."""
        validate_filter_value("created", "2024-01-01")
        validate_filter_value("modified", ">2024-01-01")
        validate_filter_value("created", ">=2024-12-31")
    
    def test_validate_filter_value_type(self):
        """Тест валидации фильтра типа."""
        validate_filter_value("type", "person")
        validate_filter_value("type", "протокол")
    
    def test_validate_filter_value_empty(self):
        """Тест валидации пустого значения фильтра."""
        with pytest.raises(ValidationError, match="не может быть пустым"):
            validate_filter_value("type", "")
    
    def test_validate_filter_value_too_long(self):
        """Тест валидации слишком длинного значения фильтра."""
        long_value = "x" * 501
        with pytest.raises(ValidationError, match="слишком длинное"):
            validate_filter_value("type", long_value)


class TestBatchSizeValidation:
    """Тесты для валидации размера батча."""
    
    def test_validate_batch_size_success(self):
        """Тест успешной валидации размера батча."""
        validate_batch_size(10)
        validate_batch_size(100)
        validate_batch_size(1000)
    
    def test_validate_batch_size_zero(self):
        """Тест валидации нулевого размера батча."""
        with pytest.raises(ValidationError, match="должен быть больше 0"):
            validate_batch_size(0)
    
    def test_validate_batch_size_negative(self):
        """Тест валидации отрицательного размера батча."""
        with pytest.raises(ValidationError, match="должен быть больше 0"):
            validate_batch_size(-1)
    
    def test_validate_batch_size_too_large(self):
        """Тест валидации слишком большого размера батча."""
        with pytest.raises(ValidationError, match="слишком большой"):
            validate_batch_size(1001)
    
    def test_validate_batch_size_custom_max(self):
        """Тест валидации с кастомным максимумом."""
        validate_batch_size(500, max_batch_size=500)
        with pytest.raises(ValidationError, match="слишком большой"):
            validate_batch_size(501, max_batch_size=500)

