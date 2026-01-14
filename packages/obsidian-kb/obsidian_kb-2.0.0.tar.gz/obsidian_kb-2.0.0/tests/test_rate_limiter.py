"""Тесты для AdaptiveRateLimiter."""

import asyncio

import pytest

from obsidian_kb.providers.rate_limiter import (
    AdaptiveRateLimiter,
    RateLimitState,
    RateLimitStats,
)


class TestRateLimitState:
    """Тесты для RateLimitState."""

    def test_create_state(self):
        """Тест создания состояния."""
        state = RateLimitState(
            current_rps=10.0,
            max_rps=100.0,
            min_rps=1.0,
        )
        assert state.current_rps == 10.0
        assert state.max_rps == 100.0
        assert state.min_rps == 1.0
        assert state.last_429_time is None
        assert state.consecutive_success == 0

    def test_state_with_optional_fields(self):
        """Тест создания состояния с опциональными полями."""
        state = RateLimitState(
            current_rps=5.0,
            max_rps=50.0,
            min_rps=0.5,
            last_429_time=12345.0,
            consecutive_success=10,
        )
        assert state.last_429_time == 12345.0
        assert state.consecutive_success == 10


class TestRateLimitStats:
    """Тесты для RateLimitStats."""

    def test_create_stats(self):
        """Тест создания статистики."""
        stats = RateLimitStats()
        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.rate_limited_requests == 0
        assert stats.current_rps == 0.0
        assert stats.rps_decreases == 0
        assert stats.rps_increases == 0

    def test_stats_with_values(self):
        """Тест создания статистики с начальными значениями."""
        stats = RateLimitStats(
            total_requests=100,
            successful_requests=95,
            rate_limited_requests=5,
            current_rps=10.0,
        )
        assert stats.total_requests == 100
        assert stats.successful_requests == 95
        assert stats.rate_limited_requests == 5


class TestAdaptiveRateLimiter:
    """Тесты для AdaptiveRateLimiter."""

    def test_create_limiter(self):
        """Тест создания rate limiter."""
        limiter = AdaptiveRateLimiter(
            initial_rps=10.0,
            max_rps=100.0,
            min_rps=1.0,
            recovery_threshold=50,
        )
        assert limiter.current_rps == 10.0
        assert limiter.enabled is True

    def test_create_disabled_limiter(self):
        """Тест создания отключённого rate limiter."""
        limiter = AdaptiveRateLimiter(enabled=False)
        assert limiter.enabled is False

    @pytest.mark.asyncio
    async def test_acquire_and_release(self):
        """Тест acquire и release."""
        limiter = AdaptiveRateLimiter(initial_rps=10.0)
        await limiter.acquire()
        limiter.release()

        # Проверяем что статистика обновилась
        assert limiter.stats.total_requests == 1

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Тест использования как context manager."""
        limiter = AdaptiveRateLimiter(initial_rps=10.0)

        async with limiter:
            pass

        assert limiter.stats.total_requests == 1

    def test_record_success(self):
        """Тест записи успешного запроса."""
        limiter = AdaptiveRateLimiter(initial_rps=10.0)
        limiter.record_success()

        assert limiter.stats.successful_requests == 1

    def test_record_rate_limit(self):
        """Тест записи 429 ошибки."""
        limiter = AdaptiveRateLimiter(initial_rps=10.0, min_rps=1.0)
        initial_rps = limiter.current_rps

        limiter.record_rate_limit()

        assert limiter.stats.rate_limited_requests == 1
        assert limiter.current_rps == initial_rps / 2  # RPS уменьшается в 2 раза
        assert limiter.stats.rps_decreases == 1

    def test_decrease_rps_respects_min(self):
        """Тест что RPS не опускается ниже минимума."""
        limiter = AdaptiveRateLimiter(initial_rps=2.0, min_rps=1.0)

        limiter.record_rate_limit()  # 2.0 -> 1.0
        assert limiter.current_rps == 1.0

        limiter.record_rate_limit()  # Должен остаться 1.0
        assert limiter.current_rps == 1.0

    def test_increase_rps_after_recovery(self):
        """Тест увеличения RPS после recovery_threshold успехов."""
        limiter = AdaptiveRateLimiter(
            initial_rps=10.0,
            max_rps=100.0,
            recovery_threshold=5,
        )

        # Записываем 4 успеха (меньше threshold)
        for _ in range(4):
            limiter.record_success()

        assert limiter.current_rps == 10.0  # Без изменений

        # Записываем 5-й успех (достигаем threshold)
        limiter.record_success()

        assert limiter.current_rps == 11.0  # +10%
        assert limiter.stats.rps_increases == 1

    def test_increase_rps_respects_max(self):
        """Тест что RPS не превышает максимум."""
        limiter = AdaptiveRateLimiter(
            initial_rps=95.0,
            max_rps=100.0,
            recovery_threshold=1,
        )

        limiter.record_success()  # 95 -> 100 (не 104.5)
        assert limiter.current_rps == 100.0

        limiter.record_success()  # Должен остаться 100.0
        assert limiter.current_rps == 100.0

    def test_rate_limit_resets_success_counter(self):
        """Тест что 429 сбрасывает счётчик успехов."""
        limiter = AdaptiveRateLimiter(
            initial_rps=10.0,
            recovery_threshold=5,
        )

        # Записываем 4 успеха
        for _ in range(4):
            limiter.record_success()

        # Получаем 429 - счётчик сбрасывается
        limiter.record_rate_limit()

        # Записываем ещё 4 успеха - не должно быть увеличения
        for _ in range(4):
            limiter.record_success()

        assert limiter.stats.rps_increases == 0

    def test_disabled_limiter_no_adaptation(self):
        """Тест что отключённый limiter не адаптируется."""
        limiter = AdaptiveRateLimiter(
            initial_rps=10.0,
            min_rps=1.0,
            recovery_threshold=1,
            enabled=False,
        )

        limiter.record_rate_limit()
        assert limiter.current_rps == 10.0  # Без изменений

        limiter.record_success()
        assert limiter.current_rps == 10.0  # Без изменений

    def test_reset(self):
        """Тест сброса состояния."""
        limiter = AdaptiveRateLimiter(
            initial_rps=10.0,
            max_rps=100.0,
            min_rps=1.0,
        )

        # Изменяем состояние
        limiter.record_rate_limit()  # Уменьшаем RPS
        limiter.record_success()

        assert limiter.current_rps == 5.0
        assert limiter.stats.rate_limited_requests == 1
        assert limiter.stats.successful_requests == 1

        # Сбрасываем
        limiter.reset()

        assert limiter.current_rps == 100.0  # Сброс к max_rps
        assert limiter.stats.rate_limited_requests == 0
        assert limiter.stats.successful_requests == 0

    def test_stats_property(self):
        """Тест свойства stats."""
        limiter = AdaptiveRateLimiter(initial_rps=15.0)

        stats = limiter.stats
        assert stats.current_rps == 15.0
        assert isinstance(stats, RateLimitStats)

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Тест параллельных запросов."""
        limiter = AdaptiveRateLimiter(initial_rps=5.0)
        request_count = 10
        completed = []

        async def make_request(i: int):
            async with limiter:
                completed.append(i)
                await asyncio.sleep(0.01)

        # Запускаем параллельные запросы
        await asyncio.gather(*[make_request(i) for i in range(request_count)])

        assert len(completed) == request_count
        assert limiter.stats.total_requests == request_count

    @pytest.mark.asyncio
    async def test_rate_limiting_enforces_interval(self):
        """Тест что rate limiter соблюдает минимальный интервал."""
        limiter = AdaptiveRateLimiter(initial_rps=100.0)  # 10ms между запросами

        import time

        times = []

        async def make_request():
            async with limiter:
                times.append(time.monotonic())

        # Делаем несколько запросов подряд
        for _ in range(3):
            await make_request()

        # Проверяем что интервалы между запросами >= 10ms
        for i in range(1, len(times)):
            interval = times[i] - times[i - 1]
            assert interval >= 0.009  # ~10ms с погрешностью


class TestAdaptiveRateLimiterEdgeCases:
    """Тесты граничных случаев."""

    def test_very_low_rps(self):
        """Тест с очень низким RPS."""
        limiter = AdaptiveRateLimiter(
            initial_rps=0.5,
            min_rps=0.1,
        )
        assert limiter.current_rps == 0.5

    def test_very_high_rps(self):
        """Тест с очень высоким RPS."""
        limiter = AdaptiveRateLimiter(
            initial_rps=1000.0,
            max_rps=10000.0,
        )
        assert limiter.current_rps == 1000.0

    def test_equal_min_max_rps(self):
        """Тест когда min == max."""
        limiter = AdaptiveRateLimiter(
            initial_rps=10.0,
            max_rps=10.0,
            min_rps=10.0,
        )

        limiter.record_rate_limit()
        assert limiter.current_rps == 10.0  # Не изменится

        for _ in range(100):
            limiter.record_success()
        assert limiter.current_rps == 10.0  # Не изменится

    def test_recovery_threshold_one(self):
        """Тест с recovery_threshold = 1."""
        limiter = AdaptiveRateLimiter(
            initial_rps=10.0,
            max_rps=100.0,
            recovery_threshold=1,
        )

        limiter.record_success()
        assert limiter.current_rps == 11.0  # Сразу увеличивается

    @pytest.mark.asyncio
    async def test_multiple_rate_limits_in_row(self):
        """Тест нескольких 429 подряд."""
        limiter = AdaptiveRateLimiter(
            initial_rps=100.0,
            min_rps=1.0,
        )

        # Серия 429 ошибок
        limiter.record_rate_limit()  # 100 -> 50
        limiter.record_rate_limit()  # 50 -> 25
        limiter.record_rate_limit()  # 25 -> 12.5
        limiter.record_rate_limit()  # 12.5 -> 6.25
        limiter.record_rate_limit()  # 6.25 -> 3.125
        limiter.record_rate_limit()  # 3.125 -> 1.5625
        limiter.record_rate_limit()  # 1.5625 -> 1.0 (min)

        assert limiter.current_rps == 1.0
        assert limiter.stats.rps_decreases == 7
