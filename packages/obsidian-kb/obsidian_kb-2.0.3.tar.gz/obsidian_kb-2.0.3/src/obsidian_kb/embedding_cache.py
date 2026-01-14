"""Модуль для кэширования embeddings неизменённых файлов."""

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import lancedb
import pyarrow as pa

from obsidian_kb.config import settings
from obsidian_kb.db_connection_manager import DBConnectionManager

logger = logging.getLogger(__name__)


@dataclass
class CachedEmbedding:
    """Кэшированный embedding для файла."""

    file_path: str
    file_hash: str  # SHA256 хеш содержимого файла
    chunk_index: int  # Индекс чанка в файле
    embedding: list[float]
    cached_at: datetime


class EmbeddingCache:
    """Кэш для embeddings неизменённых файлов."""

    def __init__(self, db_path: Path | None = None) -> None:
        """Инициализация кэша.

        Args:
            db_path: Путь к базе данных (по умолчанию из settings)
        """
        self.db_path = Path(db_path or settings.db_path).parent / "embedding_cache.lance"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection_manager = DBConnectionManager.get_instance(self.db_path.parent)

    def _get_db(self) -> lancedb.DBConnection:
        """Получение подключения к БД через connection manager."""
        # Используем connection manager для получения соединения из пула
        ctx = self.connection_manager.get_connection(self.db_path.parent)
        return ctx.__enter__()

    def _get_table(self, vault_name: str) -> lancedb.table.Table:
        """Получение или создание таблицы кэша для vault'а.

        Args:
            vault_name: Имя vault'а (нормализованное)

        Returns:
            Таблица кэша
        """
        db = self._get_db()
        table_name = f"embedding_cache_{vault_name.replace(' ', '_').replace('/', '_')}"

        try:
            table = db.open_table(table_name)
            return table
        except Exception:
            # Создаём новую таблицу
            schema = pa.schema([
                pa.field("file_path", pa.string()),
                pa.field("file_hash", pa.string()),
                pa.field("chunk_index", pa.int32()),
                pa.field("embedding", pa.list_(pa.float64())),
                pa.field("cached_at", pa.timestamp("us")),
            ])
            table = db.create_table(table_name, schema=schema, mode="overwrite")
            logger.info(f"Created embedding cache table: {table_name}")
            return table

    def _compute_file_hash(self, file_path: Path) -> str:
        """Вычисление SHA256 хеша файла.

        Args:
            file_path: Путь к файлу

        Returns:
            SHA256 хеш в hex формате
        """
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute hash for {file_path}: {e}")
            # Используем время модификации как fallback
            try:
                mtime = file_path.stat().st_mtime
                return hashlib.sha256(str(mtime).encode()).hexdigest()
            except Exception:
                return ""

    async def get_cached_embeddings(
        self,
        vault_name: str,
        file_path: Path,
        chunk_count: int,
    ) -> list[list[float]] | None:
        """Получение кэшированных embeddings для файла.

        Args:
            vault_name: Имя vault'а
            file_path: Путь к файлу
            file_content: Содержимое файла (для проверки хеша)
            chunk_count: Количество чанков в файле

        Returns:
            Список embeddings или None, если кэш недействителен
        """
        try:
            file_hash = self._compute_file_hash(file_path)
            if not file_hash:
                return None

            table = self._get_table(vault_name)

            def _query() -> list[dict[str, Any]]:
                # Используем WHERE фильтрацию вместо загрузки всей таблицы
                file_path_escaped = str(file_path).replace("'", "''")
                file_hash_escaped = file_hash.replace("'", "''")
                where_clause = f"file_path = '{file_path_escaped}' AND file_hash = '{file_hash_escaped}'"

                arrow_table = table.search().where(where_clause).to_arrow()
                cached = arrow_table.to_pylist()

                # Проверяем, что есть embeddings для всех чанков
                if len(cached) != chunk_count:
                    return []

                # Сортируем по chunk_index
                cached.sort(key=lambda x: x["chunk_index"])

                return cached

            cached_data = await asyncio.to_thread(_query)

            if not cached_data or len(cached_data) != chunk_count:
                return None

            # Извлекаем embeddings
            embeddings = [row["embedding"] for row in cached_data]

            logger.debug(f"Cache hit for {file_path} ({chunk_count} chunks)")
            return embeddings

        except Exception as e:
            logger.warning(f"Failed to get cached embeddings for {file_path}: {e}")
            return None

    async def cache_embeddings(
        self,
        vault_name: str,
        file_path: Path,
        chunk_indices: list[int],
        embeddings: list[list[float]],
    ) -> None:
        """Сохранение embeddings в кэш.

        Args:
            vault_name: Имя vault'а
            file_path: Путь к файлу
            chunk_indices: Индексы чанков
            embeddings: Список embeddings
        """
        try:
            file_hash = self._compute_file_hash(file_path)
            if not file_hash:
                return

            table = self._get_table(vault_name)

            def _insert() -> None:
                data = [
                    {
                        "file_path": str(file_path),
                        "file_hash": file_hash,
                        "chunk_index": idx,
                        "embedding": emb,
                        "cached_at": datetime.now(),
                    }
                    for idx, emb in zip(chunk_indices, embeddings)
                ]

                # Удаляем старые записи для этого файла с помощью WHERE
                try:
                    file_path_escaped = str(file_path).replace("'", "''")
                    table.delete(f"file_path = '{file_path_escaped}'")
                except Exception as e:
                    logger.debug(f"No existing cache entries to delete for {file_path}: {e}")

                # Добавляем новые записи
                try:
                    new_table = pa.Table.from_pylist(data)
                    table.add(new_table)
                except Exception as e:
                    logger.warning(f"Failed to add cache entries for {file_path}: {e}")

            await asyncio.to_thread(_insert)
            logger.debug(f"Cached embeddings for {file_path} ({len(embeddings)} chunks)")

        except Exception as e:
            logger.warning(f"Failed to cache embeddings for {file_path}: {e}")

    async def invalidate_file(self, vault_name: str, file_path: Path) -> None:
        """Инвалидация кэша для файла.

        Args:
            vault_name: Имя vault'а
            file_path: Путь к файлу
        """
        try:
            table = self._get_table(vault_name)

            def _delete() -> None:
                try:
                    arrow_table = table.to_arrow()
                    data = arrow_table.to_pylist()

                    # Фильтруем записи, исключая указанный файл
                    to_keep = [
                        row
                        for row in data
                        if row["file_path"] != str(file_path)
                    ]

                    if len(to_keep) < len(data):
                        # Есть записи для удаления
                        new_table = pa.Table.from_pylist(to_keep)
                        table.add(new_table, mode="overwrite")
                        logger.debug(f"Invalidated cache for {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to invalidate cache: {e}")

            await asyncio.to_thread(_delete)

        except Exception as e:
            logger.warning(f"Failed to invalidate cache for {file_path}: {e}")

    async def clear_vault_cache(self, vault_name: str) -> None:
        """Очистка всего кэша для vault'а.

        Args:
            vault_name: Имя vault'а
        """
        try:
            db = self._get_db()
            table_name = f"embedding_cache_{vault_name.replace(' ', '_').replace('/', '_')}"

            def _clear() -> None:
                try:
                    table = db.open_table(table_name)
                    # Создаём пустую таблицу
                    schema = pa.schema([
                        pa.field("file_path", pa.string()),
                        pa.field("file_hash", pa.string()),
                        pa.field("chunk_index", pa.int32()),
                        pa.field("embedding", pa.list_(pa.float64())),
                        pa.field("cached_at", pa.timestamp("us")),
                    ])
                    empty_table = pa.Table.from_pylist([], schema=schema)
                    table.add(empty_table, mode="overwrite")
                    logger.info(f"Cleared cache for vault: {vault_name}")
                except Exception:
                    # Таблица не существует, ничего не делаем
                    pass

            await asyncio.to_thread(_clear)

        except Exception as e:
            logger.warning(f"Failed to clear cache for vault {vault_name}: {e}")

    async def get_cache_stats(self, vault_name: str) -> dict[str, Any]:
        """Получение статистики кэша для vault'а.

        Args:
            vault_name: Имя vault'а

        Returns:
            Словарь со статистикой
        """
        try:
            table = self._get_table(vault_name)

            def _stats() -> dict[str, Any]:
                try:
                    arrow_table = table.to_arrow()
                    data = arrow_table.to_pylist()

                    unique_files = len(set(row["file_path"] for row in data))
                    total_embeddings = len(data)

                    return {
                        "cached_files": unique_files,
                        "total_embeddings": total_embeddings,
                    }
                except Exception:
                    return {"cached_files": 0, "total_embeddings": 0}

            return await asyncio.to_thread(_stats)

        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {"cached_files": 0, "total_embeddings": 0}

