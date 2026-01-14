"""Адаптивный rate limiter для провайдеров.

Автоматически адаптируется к лимитам API:
- При 429 ошибке: уменьшает RPS в 2 раза
- После N успешных запросов: увеличивает RPS на 10%
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RateLimitState:
    """Состояние rate limiter."""

    current_rps: float  # Текущий RPS
    max_rps: float  # Максимальный RPS
    min_rps: float  # Минимальный RPS
    last_429_time: float | None = None  # Время последнего 429
    consecutive_success: int = 0  # Последовательных успехов


@dataclass
class RateLimitStats:
    """Статистика rate limiter."""

    total_requests: int = 0
    successful_requests: int = 0
    rate_limited_requests: int = 0
    current_rps: float = 0.0
    rps_decreases: int = 0
    rps_increases: int = 0


class AdaptiveRateLimiter:
    """Адаптивный rate limiter с экспоненциальным backoff.

    Особенности:
    - При 429 ошибке: уменьшаем RPS в 2 раза (min_rps = 1)
    - После N успешных запросов: увеличиваем RPS на 10% (до max_rps)
    - Семафор для ограничения параллельных запросов
    - Минимальный интервал между запросами

    Пример использования:
        limiter = AdaptiveRateLimiter(initial_rps=10.0)

        async def make_request():
            await limiter.acquire()
            try:
                result = await api_call()
                limiter.record_success()
                return result
            except RateLimitError:
                limiter.record_rate_limit()
                raise
    """

    def __init__(
        self,
        initial_rps: float = 10.0,
        max_rps: float = 100.0,
        min_rps: float = 1.0,
        recovery_threshold: int = 50,
        enabled: bool = True,
    ) -> None:
        """Инициализация rate limiter.

        Args:
            initial_rps: Начальный RPS (requests per second)
            max_rps: Максимальный RPS (после восстановления)
            min_rps: Минимальный RPS (после серии 429 ошибок)
            recovery_threshold: Количество успешных запросов для увеличения RPS
            enabled: Включён ли адаптивный rate limiting (если False, работает как простой семафор)
        """
        self._enabled = enabled
        self._state = RateLimitState(
            current_rps=initial_rps,
            max_rps=max_rps,
            min_rps=min_rps,
        )
        self._recovery_threshold = recovery_threshold
        self._semaphore = asyncio.Semaphore(max(1, int(initial_rps)))
        self._last_request_time = 0.0
        self._lock = asyncio.Lock()

        # Статистика
        self._stats = RateLimitStats(current_rps=initial_rps)

    @property
    def enabled(self) -> bool:
        """Включён ли адаптивный rate limiting."""
        return self._enabled

    @property
    def current_rps(self) -> float:
        """Текущий RPS."""
        return self._state.current_rps

    @property
    def stats(self) -> RateLimitStats:
        """Статистика rate limiter."""
        self._stats.current_rps = self._state.current_rps
        return self._stats

    async def acquire(self) -> None:
        """Ожидание слота для запроса.

        Если rate limiting включён, ждём минимальный интервал между запросами.
        Семафор ограничивает количество параллельных запросов.
        """
        await self._semaphore.acquire()

        if self._enabled:
            async with self._lock:
                # Минимальный интервал между запросами
                min_interval = 1.0 / self._state.current_rps
                now = time.monotonic()
                elapsed = now - self._last_request_time

                if elapsed < min_interval:
                    await asyncio.sleep(min_interval - elapsed)

                self._last_request_time = time.monotonic()

        self._stats.total_requests += 1

    def release(self) -> None:
        """Освобождение слота (вызывается после завершения запроса)."""
        self._semaphore.release()

    def record_success(self) -> None:
        """Записать успешный запрос.

        Если включён адаптивный rate limiting, увеличивает счётчик успешных запросов.
        После достижения recovery_threshold увеличивает RPS на 10%.
        """
        self._stats.successful_requests += 1

        if not self._enabled:
            return

        self._state.consecutive_success += 1

        if self._state.consecutive_success >= self._recovery_threshold:
            self._increase_rps()
            self._state.consecutive_success = 0

    def record_rate_limit(self) -> None:
        """Записать 429 ошибку.

        Уменьшает RPS в 2 раза (но не ниже min_rps).
        Сбрасывает счётчик успешных запросов.
        """
        self._stats.rate_limited_requests += 1

        if not self._enabled:
            return

        self._state.last_429_time = time.monotonic()
        self._state.consecutive_success = 0
        self._decrease_rps()

    def _decrease_rps(self) -> None:
        """Уменьшить RPS в 2 раза."""
        new_rps = max(self._state.min_rps, self._state.current_rps / 2)

        if new_rps != self._state.current_rps:
            logger.warning(
                f"Rate limit hit, reducing RPS: {self._state.current_rps:.1f} → {new_rps:.1f}"
            )
            self._state.current_rps = new_rps
            self._update_semaphore()
            self._stats.rps_decreases += 1

    def _increase_rps(self) -> None:
        """Увеличить RPS на 10%."""
        new_rps = min(self._state.max_rps, self._state.current_rps * 1.1)

        if new_rps != self._state.current_rps:
            logger.info(
                f"Increasing RPS after {self._recovery_threshold} successful requests: "
                f"{self._state.current_rps:.1f} → {new_rps:.1f}"
            )
            self._state.current_rps = new_rps
            self._update_semaphore()
            self._stats.rps_increases += 1

    def _update_semaphore(self) -> None:
        """Обновить семафор под новый RPS.

        Создаём новый семафор с обновлённым лимитом.
        Это безопасно, так как семафор используется только для acquire/release.
        """
        self._semaphore = asyncio.Semaphore(max(1, int(self._state.current_rps)))

    def reset(self) -> None:
        """Сброс состояния rate limiter.

        Восстанавливает начальный RPS и сбрасывает статистику.
        """
        initial_rps = self._state.max_rps
        self._state = RateLimitState(
            current_rps=initial_rps,
            max_rps=self._state.max_rps,
            min_rps=self._state.min_rps,
        )
        self._semaphore = asyncio.Semaphore(max(1, int(initial_rps)))
        self._stats = RateLimitStats(current_rps=initial_rps)
        self._last_request_time = 0.0

    async def __aenter__(self) -> "AdaptiveRateLimiter":
        """Context manager для автоматического acquire/release."""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Освобождение слота при выходе из context manager."""
        self.release()
