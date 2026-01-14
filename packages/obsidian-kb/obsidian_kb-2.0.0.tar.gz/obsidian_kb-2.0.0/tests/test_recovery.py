"""Тесты для модуля автоматического восстановления после сбоев."""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from datetime import datetime

from obsidian_kb.recovery import (
    CircuitBreaker,
    RecoveryService,
    RecoveryState,
    get_recovery_service,
    with_recovery,
)
from obsidian_kb.types import DatabaseError


class TestCircuitBreaker:
    """Тесты для CircuitBreaker."""

    def test_circuit_breaker_initial_state(self):
        """Тест начального состояния circuit breaker."""
        cb = CircuitBreaker()
        assert cb.get_state() == "closed"
        assert cb.failure_count == 0
        assert cb.can_proceed()

    def test_circuit_breaker_record_success_closed(self):
        """Тест записи успеха в closed состоянии."""
        cb = CircuitBreaker()
        cb.record_success()
        assert cb.failure_count == 0
        assert cb.get_state() == "closed"

    def test_circuit_breaker_record_failure(self):
        """Тест записи ошибки и перехода в open."""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.get_state() == "closed"
        
        # Первые 2 ошибки - остаёмся в closed
        cb.record_failure()
        assert cb.get_state() == "closed"
        assert cb.failure_count == 1
        
        cb.record_failure()
        assert cb.get_state() == "closed"
        assert cb.failure_count == 2
        
        # 3-я ошибка - переход в open
        cb.record_failure()
        assert cb.get_state() == "open"
        assert cb.failure_count == 3

    def test_circuit_breaker_open_cannot_proceed(self):
        """Тест что в open состоянии нельзя выполнять операции."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60.0)
        cb.record_failure()
        assert cb.get_state() == "open"
        assert not cb.can_proceed()

    def test_circuit_breaker_half_open_after_timeout(self):
        """Тест перехода в half-open после таймаута."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        cb.record_failure()
        assert cb.get_state() == "open"
        
        # Ждём таймаут
        import time
        time.sleep(0.15)
        
        # Теперь можно попробовать
        assert cb.can_proceed()
        assert cb.get_state() == "half_open"

    def test_circuit_breaker_half_open_success(self):
        """Тест успешного восстановления из half-open."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1, half_open_max_calls=2)
        cb.record_failure()
        
        import time
        time.sleep(0.15)
        cb.can_proceed()  # Переход в half-open
        
        # Успешные вызовы в half-open
        cb.record_success()
        assert cb.get_state() == "half_open"
        assert cb.half_open_calls == 1
        
        cb.record_success()
        assert cb.get_state() == "closed"  # Переход обратно в closed
        assert cb.failure_count == 0

    def test_circuit_breaker_half_open_failure(self):
        """Тест неудачи в half-open - возврат в open."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        cb.record_failure()
        
        import time
        time.sleep(0.15)
        cb.can_proceed()  # Переход в half-open
        
        # Неудача в half-open
        cb.record_failure()
        assert cb.get_state() == "open"
        assert cb.half_open_calls == 0


class TestRecoveryService:
    """Тесты для RecoveryService."""

    @pytest.fixture
    def temp_recovery_state(self, tmp_path):
        """Временный файл состояния восстановления."""
        return tmp_path / "recovery_state.json"

    @pytest.fixture
    def recovery_service(self, temp_recovery_state):
        """RecoveryService с временным файлом состояния."""
        return RecoveryService(state_file=temp_recovery_state)

    def test_recovery_service_initialization(self, recovery_service, temp_recovery_state):
        """Тест инициализации RecoveryService."""
        assert recovery_service.state_file == temp_recovery_state
        assert recovery_service.state_file.parent.exists()

    def test_get_circuit_breaker(self, recovery_service):
        """Тест получения circuit breaker."""
        cb1 = recovery_service.get_circuit_breaker("test_operation")
        cb2 = recovery_service.get_circuit_breaker("test_operation")
        
        # Должен быть тот же экземпляр
        assert cb1 is cb2
        
        # Разные операции - разные breaker'ы
        cb3 = recovery_service.get_circuit_breaker("other_operation")
        assert cb3 is not cb1

    @pytest.mark.asyncio
    async def test_retry_with_backoff_success(self, recovery_service):
        """Тест успешного выполнения без retry."""
        call_count = 0

        async def successful_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        result = await recovery_service.retry_with_backoff(
            successful_func,
            5,
            max_retries=3,
            operation_name="test_success",
        )

        assert result == 10
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_with_backoff_retry_success(self, recovery_service):
        """Тест успешного выполнения после retry."""
        call_count = 0

        async def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary error")
            return "success"

        result = await recovery_service.retry_with_backoff(
            flaky_func,
            max_retries=3,
            initial_delay=0.1,
            operation_name="test_retry",
        )

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_with_backoff_max_retries_exceeded(self, recovery_service):
        """Тест превышения максимального количества попыток."""
        call_count = 0

        async def always_failing_func() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            await recovery_service.retry_with_backoff(
                always_failing_func,
                max_retries=3,
                initial_delay=0.1,
                operation_name="test_failure",
            )

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_with_backoff_exponential_backoff(self, recovery_service):
        """Тест exponential backoff."""
        call_times = []

        async def flaky_func() -> str:
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < 3:
                raise ValueError("Error")
            return "success"

        result = await recovery_service.retry_with_backoff(
            flaky_func,
            max_retries=3,
            initial_delay=0.1,
            exponential_base=2.0,
            operation_name="test_backoff",
        )

        assert result == "success"
        assert len(call_times) == 3
        
        # Проверяем что задержки увеличиваются
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        assert delay1 >= 0.1
        assert delay2 >= 0.2  # exponential backoff

    @pytest.mark.asyncio
    async def test_retry_with_backoff_circuit_breaker_open(self, recovery_service):
        """Тест что retry не выполняется если circuit breaker открыт."""
        cb = recovery_service.get_circuit_breaker("test_circuit")
        # Открываем circuit breaker
        for _ in range(5):
            cb.record_failure()

        call_count = 0

        async def func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        with pytest.raises(Exception, match="Circuit breaker is open"):
            await recovery_service.retry_with_backoff(
                func,
                max_retries=3,
                operation_name="test_circuit",
            )

        assert call_count == 0  # Функция не должна вызываться

    @pytest.mark.asyncio
    async def test_retry_with_backoff_sync_function(self, recovery_service):
        """Тест retry для синхронной функции."""
        call_count = 0

        def sync_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Error")
            return x * 2

        result = await recovery_service.retry_with_backoff(
            sync_func,
            5,
            max_retries=3,
            initial_delay=0.1,
            operation_name="test_sync",
        )

        assert result == 10
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_recover_database_connection_success(self, recovery_service, db_manager):
        """Тест успешного восстановления подключения к БД."""
        # Мокаем _get_db чтобы не создавать реальное подключение
        mock_db = MagicMock()
        db_manager._db = mock_db

        result = await recovery_service.recover_database_connection(db_manager, max_retries=1)
        assert result is True

    @pytest.mark.asyncio
    async def test_recover_database_connection_failure(self, recovery_service, db_manager):
        """Тест неудачного восстановления подключения к БД."""
        # Мокаем _get_db чтобы выбрасывать ошибку
        def failing_get_db():
            raise Exception("Connection failed")

        with patch.object(db_manager, "_get_db", side_effect=failing_get_db):
            result = await recovery_service.recover_database_connection(
                db_manager, max_retries=2
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_recover_ollama_connection_success(self, recovery_service, mock_embedding_service):
        """Тест успешного восстановления подключения к Ollama."""
        mock_embedding_service.health_check = AsyncMock(return_value=True)
        mock_embedding_service._session = None

        result = await recovery_service.recover_ollama_connection(
            mock_embedding_service, max_retries=1
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_recover_ollama_connection_failure(self, recovery_service, mock_embedding_service):
        """Тест неудачного восстановления подключения к Ollama."""
        mock_embedding_service.health_check = AsyncMock(return_value=False)

        result = await recovery_service.recover_ollama_connection(
            mock_embedding_service, max_retries=2
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_recover_ollama_connection_closes_session(self, recovery_service, mock_embedding_service):
        """Тест что при восстановлении закрывается старая сессия."""
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_embedding_service._session = mock_session
        mock_embedding_service.close = AsyncMock()
        mock_embedding_service.health_check = AsyncMock(return_value=True)

        await recovery_service.recover_ollama_connection(
            mock_embedding_service, max_retries=1
        )

        mock_embedding_service.close.assert_called_once()

    def test_save_indexing_progress(self, recovery_service, temp_recovery_state):
        """Тест сохранения прогресса индексации."""
        vault_name = "test_vault"
        processed_files = ["file1.md", "file2.md"]
        total_files = 10

        recovery_service.save_indexing_progress(vault_name, processed_files, total_files)

        progress_file = temp_recovery_state.parent / f"indexing_progress_{vault_name}.json"
        assert progress_file.exists()

        with open(progress_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["vault_name"] == vault_name
        assert data["processed_files"] == processed_files
        assert data["total_files"] == total_files
        assert "timestamp" in data

    def test_load_indexing_progress(self, recovery_service, temp_recovery_state):
        """Тест загрузки прогресса индексации."""
        vault_name = "test_vault"
        progress_data = {
            "vault_name": vault_name,
            "processed_files": ["file1.md"],
            "total_files": 5,
            "timestamp": "2024-01-01T00:00:00",
        }

        progress_file = temp_recovery_state.parent / f"indexing_progress_{vault_name}.json"
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(progress_data, f)

        loaded = recovery_service.load_indexing_progress(vault_name)
        assert loaded is not None
        assert loaded["vault_name"] == vault_name
        assert loaded["processed_files"] == ["file1.md"]

    def test_load_indexing_progress_not_found(self, recovery_service):
        """Тест загрузки несуществующего прогресса."""
        loaded = recovery_service.load_indexing_progress("nonexistent_vault")
        assert loaded is None

    def test_clear_indexing_progress(self, recovery_service, temp_recovery_state):
        """Тест очистки прогресса индексации."""
        vault_name = "test_vault"
        progress_file = temp_recovery_state.parent / f"indexing_progress_{vault_name}.json"
        
        # Создаём файл прогресса
        progress_file.write_text('{"test": "data"}', encoding="utf-8")
        assert progress_file.exists()

        recovery_service.clear_indexing_progress(vault_name)
        assert not progress_file.exists()

    def test_save_and_load_state(self, recovery_service, temp_recovery_state):
        """Тест сохранения и загрузки состояния."""
        from datetime import datetime
        from obsidian_kb.recovery import RecoveryState
        
        # Создаём состояние используя настоящий dataclass
        recovery_service.recovery_states["test_op"] = RecoveryState(
            operation="test_op",
            attempts=2,
            last_error="Test error",
            last_attempt_time=datetime.now(),
            recovered=False,
        )

        # Сохраняем
        recovery_service._save_state()
        assert temp_recovery_state.exists()

        # Создаём новый сервис и загружаем
        new_service = RecoveryService(state_file=temp_recovery_state)
        assert "test_op" in new_service.recovery_states
        assert new_service.recovery_states["test_op"].operation == "test_op"
        assert new_service.recovery_states["test_op"].attempts == 2


class TestRecoveryDecorator:
    """Тесты для декоратора with_recovery."""

    @pytest.mark.asyncio
    async def test_with_recovery_decorator_success(self):
        """Тест декоратора with_recovery для успешной операции."""
        call_count = 0

        @with_recovery(operation_name="test_decorator", max_retries=3)
        async def test_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        result = await test_func(5)
        assert result == 10
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_with_recovery_decorator_retry(self):
        """Тест декоратора with_recovery с retry."""
        call_count = 0

        @with_recovery(operation_name="test_retry_decorator", max_retries=3, initial_delay=0.1)
        async def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Error")
            return "success"

        result = await flaky_func()
        assert result == "success"
        assert call_count == 2


class TestGetRecoveryService:
    """Тесты для get_recovery_service."""

    def test_get_recovery_service_singleton(self):
        """Тест что get_recovery_service возвращает singleton."""
        from obsidian_kb.recovery import _recovery_service
        import obsidian_kb.recovery as recovery_module

        # Сбрасываем глобальный экземпляр
        recovery_module._recovery_service = None

        service1 = get_recovery_service()
        service2 = get_recovery_service()

        assert service1 is service2
        assert service1 is not None

