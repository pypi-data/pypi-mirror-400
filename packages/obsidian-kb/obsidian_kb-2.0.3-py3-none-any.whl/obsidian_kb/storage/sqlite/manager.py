"""SQLite connection manager with connection pooling and WAL mode.

This module provides async SQLite database management using aiosqlite
with features for production use:
- Connection pooling for concurrent access
- WAL mode for better concurrency
- Context manager support
- Transaction management
"""

import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Sequence

import aiosqlite

logger = logging.getLogger(__name__)


class SQLiteManager:
    """Async SQLite connection manager with pooling and WAL mode.

    Provides connection pooling and WAL mode for concurrent read/write
    operations. Designed for use with asyncio.

    Usage:
        # As context manager (recommended)
        async with SQLiteManager("path/to/db.sqlite") as manager:
            result = await manager.execute("SELECT * FROM documents")
            rows = await result.fetchall()

        # Manual lifecycle management
        manager = SQLiteManager("path/to/db.sqlite")
        await manager.initialize()
        try:
            result = await manager.execute("SELECT * FROM documents")
        finally:
            await manager.close()

    Attributes:
        db_path: Path to SQLite database file
        pool_size: Maximum number of connections in pool
        timeout: Connection timeout in seconds
    """

    _instances: dict[str, "SQLiteManager"] = {}
    _instances_lock = threading.Lock()

    def __init__(
        self,
        db_path: str | Path,
        pool_size: int = 5,
        timeout: float = 30.0,
    ) -> None:
        """Initialize SQLite manager.

        Args:
            db_path: Path to SQLite database file
            pool_size: Maximum number of connections in pool (default: 5)
            timeout: Connection timeout in seconds (default: 30.0)
        """
        self.db_path = Path(db_path)
        self.pool_size = pool_size
        self.timeout = timeout

        # Connection pool
        self._pool: asyncio.Queue[aiosqlite.Connection] = asyncio.Queue(maxsize=pool_size)
        self._pool_lock = asyncio.Lock()
        self._initialized = False
        self._connections_created = 0

        # Statistics
        self._total_queries = 0
        self._total_errors = 0

    @classmethod
    def get_instance(
        cls,
        db_path: str | Path,
        pool_size: int = 5,
        timeout: float = 30.0,
    ) -> "SQLiteManager":
        """Get or create singleton instance for a database path.

        Args:
            db_path: Path to SQLite database file
            pool_size: Maximum connections (only used on first call)
            timeout: Connection timeout (only used on first call)

        Returns:
            SQLiteManager instance for the given path
        """
        path_key = str(Path(db_path).resolve())

        with cls._instances_lock:
            if path_key not in cls._instances:
                cls._instances[path_key] = cls(db_path, pool_size, timeout)

            return cls._instances[path_key]

    @classmethod
    def reset_instance(cls, db_path: str | Path | None = None) -> None:
        """Reset singleton instance(s) for testing.

        Args:
            db_path: Specific path to reset, or None to reset all
        """
        with cls._instances_lock:
            if db_path is None:
                cls._instances.clear()
            else:
                path_key = str(Path(db_path).resolve())
                cls._instances.pop(path_key, None)

    async def initialize(self) -> None:
        """Initialize the connection pool and enable WAL mode.

        Creates the database file and parent directories if needed.
        Enables WAL mode for better concurrent access.

        Raises:
            aiosqlite.Error: If database initialization fails
        """
        if self._initialized:
            return

        async with self._pool_lock:
            if self._initialized:
                return

            # Ensure parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Create initial connection to set up WAL mode
            conn = await self._create_connection()

            # Enable WAL mode for better concurrency
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA synchronous=NORMAL")
            await conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            await conn.execute("PRAGMA temp_store=MEMORY")
            await conn.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
            await conn.commit()

            # Add to pool
            await self._pool.put(conn)
            self._connections_created = 1

            self._initialized = True
            logger.info(f"SQLiteManager initialized: {self.db_path} (WAL mode enabled)")

    async def _create_connection(self) -> aiosqlite.Connection:
        """Create a new database connection.

        Returns:
            New aiosqlite connection

        Raises:
            aiosqlite.Error: If connection creation fails
        """
        conn = await aiosqlite.connect(
            self.db_path,
            timeout=self.timeout,
        )

        # Enable foreign keys
        await conn.execute("PRAGMA foreign_keys=ON")

        # Row factory for dict-like access
        conn.row_factory = aiosqlite.Row

        self._connections_created += 1
        logger.debug(f"Created SQLite connection #{self._connections_created}")

        return conn

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Get a connection from the pool.

        Usage:
            async with manager.get_connection() as conn:
                await conn.execute("SELECT * FROM documents")

        Yields:
            Database connection from pool

        Raises:
            RuntimeError: If manager not initialized
            asyncio.TimeoutError: If pool exhausted and timeout exceeded
        """
        if not self._initialized:
            await self.initialize()

        conn: aiosqlite.Connection | None = None

        try:
            # Try to get from pool
            try:
                conn = self._pool.get_nowait()
            except asyncio.QueueEmpty:
                # Pool empty, create new if under limit
                async with self._pool_lock:
                    if self._connections_created < self.pool_size:
                        conn = await self._create_connection()
                    else:
                        # Wait for connection from pool
                        conn = await asyncio.wait_for(
                            self._pool.get(),
                            timeout=self.timeout,
                        )

            yield conn

        finally:
            if conn is not None:
                # Return to pool
                try:
                    self._pool.put_nowait(conn)
                except asyncio.QueueFull:
                    # Pool full, close connection
                    await conn.close()
                    async with self._pool_lock:
                        self._connections_created -= 1

    async def execute(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> aiosqlite.Cursor:
        """Execute a SQL statement.

        Args:
            sql: SQL statement to execute
            parameters: Optional parameters for the statement

        Returns:
            Cursor with results

        Raises:
            aiosqlite.Error: If execution fails
        """
        async with self.get_connection() as conn:
            self._total_queries += 1
            try:
                if parameters:
                    cursor = await conn.execute(sql, parameters)
                else:
                    cursor = await conn.execute(sql)
                await conn.commit()
                return cursor
            except aiosqlite.Error as e:
                self._total_errors += 1
                logger.error(f"SQL execution error: {e}\nSQL: {sql}")
                raise

    async def execute_many(
        self,
        sql: str,
        parameters: Sequence[Sequence[Any]],
    ) -> aiosqlite.Cursor:
        """Execute a SQL statement with multiple parameter sets.

        Args:
            sql: SQL statement to execute
            parameters: Sequence of parameter sequences

        Returns:
            Cursor (from last execution)

        Raises:
            aiosqlite.Error: If execution fails
        """
        async with self.get_connection() as conn:
            self._total_queries += len(parameters)
            try:
                cursor = await conn.executemany(sql, parameters)
                await conn.commit()
                return cursor
            except aiosqlite.Error as e:
                self._total_errors += 1
                logger.error(f"SQL executemany error: {e}\nSQL: {sql}")
                raise

    async def execute_script(self, sql_script: str) -> None:
        """Execute a SQL script (multiple statements).

        Args:
            sql_script: SQL script with multiple statements

        Raises:
            aiosqlite.Error: If execution fails
        """
        async with self.get_connection() as conn:
            try:
                await conn.executescript(sql_script)
                await conn.commit()
                logger.debug("SQL script executed successfully")
            except aiosqlite.Error as e:
                self._total_errors += 1
                logger.error(f"SQL script error: {e}")
                raise

    async def fetch_one(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> dict[str, Any] | None:
        """Execute SQL and fetch one row as dict.

        Args:
            sql: SQL SELECT statement
            parameters: Optional parameters

        Returns:
            Row as dict, or None if no results
        """
        async with self.get_connection() as conn:
            self._total_queries += 1
            try:
                if parameters:
                    cursor = await conn.execute(sql, parameters)
                else:
                    cursor = await conn.execute(sql)
                row = await cursor.fetchone()
                if row is None:
                    return None
                return dict(row)
            except aiosqlite.Error as e:
                self._total_errors += 1
                logger.error(f"SQL fetch_one error: {e}\nSQL: {sql}")
                raise

    async def fetch_all(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute SQL and fetch all rows as list of dicts.

        Args:
            sql: SQL SELECT statement
            parameters: Optional parameters

        Returns:
            List of rows as dicts
        """
        async with self.get_connection() as conn:
            self._total_queries += 1
            try:
                if parameters:
                    cursor = await conn.execute(sql, parameters)
                else:
                    cursor = await conn.execute(sql)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
            except aiosqlite.Error as e:
                self._total_errors += 1
                logger.error(f"SQL fetch_all error: {e}\nSQL: {sql}")
                raise

    async def fetch_value(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> Any:
        """Execute SQL and fetch a single value.

        Args:
            sql: SQL SELECT statement returning single value
            parameters: Optional parameters

        Returns:
            Single value, or None if no results
        """
        row = await self.fetch_one(sql, parameters)
        if row is None:
            return None
        # Return first column value
        return next(iter(row.values()), None)

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Execute operations in a transaction.

        Usage:
            async with manager.transaction() as conn:
                await conn.execute("INSERT INTO ...")
                await conn.execute("UPDATE ...")
                # Auto-commit on exit, rollback on exception

        Yields:
            Connection in transaction mode

        Raises:
            aiosqlite.Error: If transaction fails
        """
        async with self.get_connection() as conn:
            try:
                await conn.execute("BEGIN")
                yield conn
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

    async def close(self) -> None:
        """Close all connections in the pool."""
        async with self._pool_lock:
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    await conn.close()
                except asyncio.QueueEmpty:
                    break

            self._connections_created = 0
            self._initialized = False

        logger.info(f"SQLiteManager closed: {self.db_path}")

    async def __aenter__(self) -> "SQLiteManager":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def get_stats(self) -> dict[str, Any]:
        """Get connection pool statistics.

        Returns:
            Dict with pool statistics
        """
        return {
            "db_path": str(self.db_path),
            "pool_size": self.pool_size,
            "connections_created": self._connections_created,
            "pool_available": self._pool.qsize(),
            "initialized": self._initialized,
            "total_queries": self._total_queries,
            "total_errors": self._total_errors,
        }

    def is_initialized(self) -> bool:
        """Check if manager is initialized.

        Returns:
            True if initialized
        """
        return self._initialized
