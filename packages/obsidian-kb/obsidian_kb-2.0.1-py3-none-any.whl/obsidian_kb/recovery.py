"""Модуль автоматического восстановления после сбоев."""

import asyncio
import json
import logging
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from obsidian_kb.diagnostics import send_notification
from obsidian_kb.providers.exceptions import ProviderConnectionError

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IDatabaseManager

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class RecoveryStrategy(Enum):
    """Стратегия восстановления."""

    RETRY = "retry"  # Повторная попытка
    FALLBACK = "fallback"  # Использование альтернативного метода
    SKIP = "skip"  # Пропуск операции
    FAIL = "fail"  # Завершение с ошибкой


@dataclass
class RecoveryState:
    """Состояние процесса восстановления."""

    operation: str
    attempts: int
    last_error: str | None = None
    last_attempt_time: datetime | None = None
    recovered: bool = False


class CircuitBreaker:
    """Circuit breaker для предотвращения каскадных сбоев."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ) -> None:
        """Инициализация circuit breaker.

        Args:
            failure_threshold: Количество ошибок до открытия circuit
            recovery_timeout: Время в секундах до попытки восстановления
            half_open_max_calls: Максимум попыток в half-open состоянии
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "closed"  # closed, open, half_open
        self.half_open_calls = 0

    def record_success(self) -> None:
        """Запись успешной операции."""
        if self.state == "half_open":
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                logger.info("Circuit breaker: переход в closed состояние")
                self.state = "closed"
                self.failure_count = 0
                self.half_open_calls = 0
        elif self.state == "closed":
            self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self) -> None:
        """Запись неудачной операции."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == "half_open":
            logger.warning("Circuit breaker: переход в open состояние (неудача в half-open)")
            self.state = "open"
            self.half_open_calls = 0
        elif self.failure_count >= self.failure_threshold:
            logger.warning(f"Circuit breaker: переход в open состояние ({self.failure_count} ошибок)")
            self.state = "open"

    def can_proceed(self) -> bool:
        """Проверка, можно ли выполнить операцию."""
        if self.state == "closed":
            return True

        if self.state == "open":
            if self.last_failure_time is None:
                return False
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                logger.info("Circuit breaker: переход в half-open состояние")
                self.state = "half_open"
                self.half_open_calls = 0
                return True
            return False

        if self.state == "half_open":
            return True

        return False

    def get_state(self) -> str:
        """Получение текущего состояния."""
        return self.state


class RecoveryService:
    """Сервис автоматического восстановления после сбоев."""

    def __init__(self, state_file: Path | None = None) -> None:
        """Инициализация сервиса восстановления.

        Args:
            state_file: Путь к файлу для сохранения состояния (опционально)
        """
        self.state_file = state_file or (Path.home() / ".obsidian-kb" / "recovery_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.recovery_states: dict[str, RecoveryState] = {}
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self._load_state()

    def _load_state(self) -> None:
        """Загрузка состояния из файла."""
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, state_data in data.get("recovery_states", {}).items():
                    self.recovery_states[key] = RecoveryState(**state_data)
        except Exception as e:
            logger.warning(f"Failed to load recovery state: {e}")

    def _save_state(self) -> None:
        """Сохранение состояния в файл."""
        try:
            data = {
                "recovery_states": {
                    key: asdict(state) for key, state in self.recovery_states.items()
                },
                "timestamp": datetime.now().isoformat(),
            }
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"Failed to save recovery state: {e}")

    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Получение или создание circuit breaker для операции.

        Args:
            name: Имя операции

        Returns:
            CircuitBreaker для операции
        """
        if name not in self.circuit_breakers:
            # Для LLM обогащения используем более мягкие настройки
            if name == "llm_enrichment":
                # Больше ошибок до открытия, быстрее восстановление
                self.circuit_breakers[name] = CircuitBreaker(
                    failure_threshold=10,  # Увеличено с 5 до 10
                    recovery_timeout=30.0,  # Уменьшено с 60 до 30 секунд
                    half_open_max_calls=2,  # Уменьшено для быстрого восстановления
                )
            else:
                self.circuit_breakers[name] = CircuitBreaker()
        return self.circuit_breakers[name]

    def reset_circuit_breaker(self, name: str) -> bool:
        """Принудительный сброс circuit breaker для операции.

        Args:
            name: Имя операции

        Returns:
            True если circuit breaker был сброшен, False если не найден
        """
        if name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[name]
            circuit_breaker.state = "closed"
            circuit_breaker.failure_count = 0
            circuit_breaker.last_failure_time = None
            circuit_breaker.half_open_calls = 0
            logger.info(f"Circuit breaker для '{name}' принудительно сброшен")
            return True
        return False

    async def retry_with_backoff(
        self,
        func: Callable[..., Any],
        *args: Any,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        operation_name: str = "operation",
        **kwargs: Any,
    ) -> Any:
        """Выполнение функции с повторными попытками и exponential backoff.

        Args:
            func: Функция для выполнения
            *args: Позиционные аргументы
            max_retries: Максимальное количество попыток
            initial_delay: Начальная задержка в секундах
            max_delay: Максимальная задержка в секундах
            exponential_base: База для exponential backoff
            operation_name: Имя операции для логирования
            **kwargs: Именованные аргументы

        Returns:
            Результат выполнения функции

        Raises:
            Последнее исключение, если все попытки неудачны
        """
        circuit_breaker = self.get_circuit_breaker(operation_name)

        # Проверяем circuit breaker
        if not circuit_breaker.can_proceed():
            raise Exception(f"Circuit breaker is open for {operation_name}")

        last_exception: Exception | None = None

        for attempt in range(max_retries):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Успешное выполнение
                circuit_breaker.record_success()
                if operation_name in self.recovery_states:
                    state = self.recovery_states[operation_name]
                    state.recovered = True
                    state.attempts = attempt + 1
                    self._save_state()

                return result

            except Exception as e:
                last_exception = e
                circuit_breaker.record_failure()

                if attempt < max_retries - 1:
                    # Вычисляем задержку с exponential backoff
                    delay = min(initial_delay * (exponential_base**attempt), max_delay)
                    logger.warning(
                        f"{operation_name} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {delay:.1f}s"
                    )

                    # Обновляем состояние восстановления
                    if operation_name not in self.recovery_states:
                        self.recovery_states[operation_name] = RecoveryState(
                            operation=operation_name,
                            attempts=attempt + 1,
                            last_error=str(e),
                            last_attempt_time=datetime.now(),
                        )
                    else:
                        state = self.recovery_states[operation_name]
                        state.attempts = attempt + 1
                        state.last_error = str(e)
                        state.last_attempt_time = datetime.now()
                    self._save_state()

                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{operation_name} failed after {max_retries} attempts: {e}")

        # Все попытки неудачны
        if operation_name in self.recovery_states:
            state = self.recovery_states[operation_name]
            state.recovered = False
            self._save_state()

        if last_exception:
            raise last_exception
        raise Exception(f"{operation_name} failed after {max_retries} attempts")

    async def recover_database_connection(
        self, db_manager: "IDatabaseManager", max_retries: int = 3
    ) -> bool:
        """Восстановление подключения к базе данных.

        Args:
            db_manager: Менеджер базы данных
            max_retries: Максимальное количество попыток

        Returns:
            True если подключение восстановлено, False иначе
        """
        circuit_breaker = self.get_circuit_breaker("database")

        if not circuit_breaker.can_proceed():
            logger.warning("Circuit breaker is open for database operations")
            return False

        for attempt in range(max_retries):
            try:
                # Пытаемся выполнить простую операцию для проверки подключения
                await asyncio.to_thread(lambda: db_manager._get_db())
                circuit_breaker.record_success()
                logger.info("Database connection recovered")
                send_notification(
                    "obsidian-kb: Восстановление",
                    "Подключение к базе данных восстановлено",
                    sound=False,
                )
                return True
            except Exception as e:
                circuit_breaker.record_failure()
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(f"Database connection failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to recover database connection after {max_retries} attempts: {e}")

        return False

    async def recover_ollama_connection(
        self, embedding_service: Any, max_retries: int = 3
    ) -> bool:
        """Восстановление подключения к Ollama.

        Args:
            embedding_service: Сервис embeddings
            max_retries: Максимальное количество попыток

        Returns:
            True если подключение восстановлено, False иначе
        """
        circuit_breaker = self.get_circuit_breaker("ollama")

        if not circuit_breaker.can_proceed():
            logger.warning("Circuit breaker is open for Ollama operations")
            return False

        for attempt in range(max_retries):
            try:
                # Закрываем старую сессию если есть
                if embedding_service._session and not embedding_service._session.closed:
                    await embedding_service.close()

                # Проверяем подключение через health check
                is_healthy = await embedding_service.health_check()
                if is_healthy:
                    circuit_breaker.record_success()
                    logger.info("Ollama connection recovered")
                    send_notification(
                        "obsidian-kb: Восстановление",
                        "Подключение к Ollama восстановлено",
                        sound=False,
                    )
                    return True
                else:
                    raise ProviderConnectionError("Ollama health check failed")

            except Exception as e:
                circuit_breaker.record_failure()
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(f"Ollama connection failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to recover Ollama connection after {max_retries} attempts: {e}")

        return False

    def save_indexing_progress(
        self, vault_name: str, processed_files: list[str], total_files: int
    ) -> None:
        """Сохранение прогресса индексации для возможности возобновления.

        Args:
            vault_name: Имя vault'а
            processed_files: Список обработанных файлов
            total_files: Общее количество файлов
        """
        progress_data = {
            "vault_name": vault_name,
            "processed_files": processed_files,
            "total_files": total_files,
            "timestamp": datetime.now().isoformat(),
        }

        progress_file = self.state_file.parent / f"indexing_progress_{vault_name}.json"
        try:
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save indexing progress: {e}")

    def load_indexing_progress(self, vault_name: str) -> dict[str, Any] | None:
        """Загрузка прогресса индексации.

        Args:
            vault_name: Имя vault'а

        Returns:
            Данные прогресса или None если нет сохранённого прогресса
        """
        progress_file = self.state_file.parent / f"indexing_progress_{vault_name}.json"
        if not progress_file.exists():
            return None

        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load indexing progress: {e}")
            return None

    def clear_indexing_progress(self, vault_name: str) -> None:
        """Очистка сохранённого прогресса индексации.

        Args:
            vault_name: Имя vault'а
        """
        progress_file = self.state_file.parent / f"indexing_progress_{vault_name}.json"
        if progress_file.exists():
            try:
                progress_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to clear indexing progress: {e}")


# Глобальный экземпляр сервиса восстановления
_recovery_service: RecoveryService | None = None


def get_recovery_service() -> RecoveryService:
    """Получение глобального экземпляра сервиса восстановления."""
    global _recovery_service
    if _recovery_service is None:
        _recovery_service = RecoveryService()
    return _recovery_service


def with_recovery(
    operation_name: str = "operation",
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
) -> Callable[[F], F]:
    """Декоратор для автоматического восстановления операций.

    Args:
        operation_name: Имя операции для логирования
        max_retries: Максимальное количество попыток
        initial_delay: Начальная задержка в секундах
        max_delay: Максимальная задержка в секундах

    Returns:
        Декорированная функция
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            recovery_service = get_recovery_service()
            return await recovery_service.retry_with_backoff(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                operation_name=operation_name,
                **kwargs,
            )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Для синхронных функций используем asyncio.run
            recovery_service = get_recovery_service()

            async def async_func() -> Any:
                return await recovery_service.retry_with_backoff(
                    func,
                    *args,
                    max_retries=max_retries,
                    initial_delay=initial_delay,
                    max_delay=max_delay,
                    operation_name=operation_name,
                    **kwargs,
                )

            return asyncio.run(async_func())

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator

