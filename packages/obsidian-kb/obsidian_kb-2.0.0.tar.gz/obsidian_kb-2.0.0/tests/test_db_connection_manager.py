"""Тесты для db_connection_manager.py"""

import pytest
from pathlib import Path

from obsidian_kb.db_connection_manager import DBConnectionManager


def test_get_instance_singleton(temp_db):
    """Тест singleton паттерна для DBConnectionManager."""
    manager1 = DBConnectionManager.get_instance(temp_db)
    manager2 = DBConnectionManager.get_instance(temp_db)
    
    assert manager1 is manager2
    assert manager1.db_path == temp_db


def test_get_connection(temp_db):
    """Тест получения подключения из пула."""
    manager = DBConnectionManager.get_instance(temp_db)
    
    with manager.get_connection(temp_db) as db:
        assert db is not None
        # Проверяем, что это действительно подключение к LanceDB
        assert hasattr(db, 'table_names')


def test_connection_reuse(temp_db):
    """Тест переиспользования соединений в пуле."""
    manager = DBConnectionManager.get_instance(temp_db)
    
    # Получаем первое соединение
    with manager.get_connection(temp_db) as db1:
        connection_id1 = id(db1)
    
    # Получаем второе соединение - должно быть то же самое
    with manager.get_connection(temp_db) as db2:
        connection_id2 = id(db2)
    
    assert connection_id1 == connection_id2, "Соединения должны переиспользоваться"


def test_multiple_db_paths(temp_db):
    """Тест работы с несколькими путями к БД."""
    manager = DBConnectionManager.get_instance(temp_db)
    
    db_path1 = temp_db / "db1"
    db_path2 = temp_db / "db2"
    
    with manager.get_connection(db_path1) as db1:
        with manager.get_connection(db_path2) as db2:
            assert db1 is not db2, "Разные пути должны давать разные соединения"
            assert id(db1) != id(db2)


def test_get_connection_count(temp_db):
    """Тест подсчета количества соединений."""
    manager = DBConnectionManager.get_instance(temp_db)
    
    initial_count = manager.get_connection_count()
    
    with manager.get_connection(temp_db):
        assert manager.get_connection_count() >= initial_count
    
    # Количество должно остаться тем же после закрытия context manager
    assert manager.get_connection_count() >= initial_count


def test_get_pool_info(temp_db):
    """Тест получения информации о пуле."""
    manager = DBConnectionManager.get_instance(temp_db)
    
    info = manager.get_pool_info()
    assert "connection_count" in info
    assert "pool_size" in info
    assert isinstance(info["connection_count"], int)
    assert isinstance(info["pool_size"], int)


def test_close_connection(temp_db):
    """Тест закрытия конкретного подключения."""
    manager = DBConnectionManager.get_instance(temp_db)
    
    # Создаём соединение
    with manager.get_connection(temp_db):
        pass
    
    initial_count = manager.get_connection_count()
    
    # Закрываем соединение
    manager.close_connection(temp_db)
    
    # Количество должно уменьшиться
    assert manager.get_connection_count() < initial_count


def test_close_all(temp_db):
    """Тест закрытия всех подключений."""
    manager = DBConnectionManager.get_instance(temp_db)
    
    # Создаём несколько соединений
    with manager.get_connection(temp_db):
        pass
    
    db_path2 = temp_db / "db2"
    with manager.get_connection(db_path2):
        pass
    
    assert manager.get_connection_count() > 0
    
    # Закрываем все
    manager.close_all()
    
    assert manager.get_connection_count() == 0
    assert manager.get_pool_info()["pool_size"] == 0

