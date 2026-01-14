"""Менеджер подключений к LanceDB с пулом соединений."""

import logging
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import lancedb

from obsidian_kb.config import settings
from obsidian_kb.types import DatabaseError

logger = logging.getLogger(__name__)


class DBConnectionManager:
    """Менеджер подключений к LanceDB с пулом соединений.

    Обеспечивает переиспользование соединений к базе данных,
    что уменьшает накладные расходы и улучшает производительность.
    """

    _instance: "DBConnectionManager | None" = None
    _lock = threading.Lock()

    def __init__(self, db_path: Path | None = None) -> None:
        """Инициализация менеджера подключений.

        Args:
            db_path: Путь к базе данных (по умолчанию из settings)
        """
        self.db_path = Path(db_path or settings.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connections: dict[str, lancedb.DBConnection] = {}
        self._connection_lock = threading.Lock()
        self._connection_count = 0

    @classmethod
    def get_instance(cls, db_path: Path | None = None) -> "DBConnectionManager":
        """Получение singleton экземпляра менеджера.

        Args:
            db_path: Путь к базе данных. Если отличается от текущего пути
                    существующего экземпляра, создаётся новый экземпляр.

        Returns:
            Экземпляр DBConnectionManager
        """
        with cls._lock:
            # Если db_path передан и отличается от текущего, пересоздаём экземпляр
            if db_path is not None and cls._instance is not None:
                if cls._instance.db_path != Path(db_path):
                    cls._instance.close_all()
                    cls._instance = None

            if cls._instance is None:
                cls._instance = cls(db_path)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Сброс singleton экземпляра (для тестов).

        Закрывает все соединения и сбрасывает singleton.
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close_all()
                cls._instance = None

    @contextmanager
    def get_connection(
        self, db_path: Path | None = None
    ) -> Generator[lancedb.DBConnection, None, None]:
        """Получение подключения из пула (context manager).

        Args:
            db_path: Путь к базе данных (по умолчанию используется self.db_path)

        Yields:
            Подключение к LanceDB

        Raises:
            DatabaseError: Если не удалось создать подключение
        """
        path = str(db_path or self.db_path)

        # Проверяем, есть ли уже соединение для этого пути
        if path not in self._connections:
            with self._connection_lock:
                # Двойная проверка после получения блокировки
                if path not in self._connections:
                    try:
                        logger.debug(f"Creating new LanceDB connection to: {path}")
                        self._connections[path] = lancedb.connect(path)
                        self._connection_count += 1
                        logger.debug(f"Connection pool size: {self._connection_count}")
                    except Exception as e:
                        logger.error(
                            f"Failed to create database connection to {path}: {e}"
                        )
                        raise DatabaseError(
                            f"Failed to connect to database: {e}"
                        ) from e

        try:
            yield self._connections[path]
        except Exception as e:
            logger.warning(f"Error using database connection: {e}")
            # При ошибке пересоздаём соединение
            with self._connection_lock:
                if path in self._connections:
                    try:
                        # Пытаемся пересоздать соединение
                        self._connections[path] = lancedb.connect(path)
                        logger.info(f"Recreated database connection to: {path}")
                    except Exception as recreate_error:
                        logger.error(f"Failed to recreate connection: {recreate_error}")
                        # Удаляем нерабочее соединение из пула
                        del self._connections[path]
                        self._connection_count -= 1
            raise

    def get_or_create_connection(
        self, db_path: Path | None = None
    ) -> lancedb.DBConnection:
        """Получение соединения из пула (без context manager).

        Этот метод возвращает соединение напрямую, без оборачивания в context manager.
        Соединение кешируется в пуле и переиспользуется.

        Args:
            db_path: Путь к базе данных (по умолчанию используется self.db_path)

        Returns:
            Подключение к LanceDB

        Raises:
            DatabaseError: Если не удалось создать подключение
        """
        path = str(db_path or self.db_path)

        if path not in self._connections:
            with self._connection_lock:
                # Двойная проверка после получения блокировки
                if path not in self._connections:
                    try:
                        logger.debug(f"Creating new LanceDB connection to: {path}")
                        self._connections[path] = lancedb.connect(path)
                        self._connection_count += 1
                        logger.debug(f"Connection pool size: {self._connection_count}")
                    except Exception as e:
                        logger.error(
                            f"Failed to create database connection to {path}: {e}"
                        )
                        raise DatabaseError(
                            f"Failed to connect to database: {e}"
                        ) from e

        return self._connections[path]

    def close_connection(self, db_path: Path | None = None) -> None:
        """Закрытие конкретного подключения.

        Args:
            db_path: Путь к базе данных (по умолчанию используется self.db_path)
        """
        path = str(db_path or self.db_path)
        with self._connection_lock:
            if path in self._connections:
                try:
                    # LanceDB не имеет явного close(), но можно очистить из пула
                    del self._connections[path]
                    self._connection_count -= 1
                    logger.debug(f"Removed connection from pool: {path}")
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")

    def close_all(self) -> None:
        """Закрытие всех подключений в пуле."""
        with self._connection_lock:
            logger.info(f"Closing all {len(self._connections)} database connections")
            self._connections.clear()
            self._connection_count = 0

    def get_connection_count(self) -> int:
        """Получение количества активных соединений в пуле.

        Returns:
            Количество соединений
        """
        return self._connection_count

    def get_pool_info(self) -> dict[str, int]:
        """Получение информации о пуле соединений.

        Returns:
            Словарь с информацией о пуле
        """
        return {
            "connection_count": self._connection_count,
            "pool_size": len(self._connections),
        }
