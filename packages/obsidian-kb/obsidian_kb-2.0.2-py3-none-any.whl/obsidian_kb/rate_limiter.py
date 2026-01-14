"""Rate Limiter с sliding window алгоритмом для ограничения частоты запросов."""

import asyncio
import logging
import time
from collections import deque
from typing import Deque

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate Limiter с sliding window алгоритмом.
    
    Ограничивает частоту запросов, используя sliding window подход:
    - Отслеживает время каждого запроса в окне времени
    - Автоматически удаляет устаревшие записи
    - Блокирует запросы, если лимит превышен
    """
    
    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        name: str = "RateLimiter",
    ) -> None:
        """Инициализация Rate Limiter.
        
        Args:
            max_requests: Максимальное количество запросов в окне времени
            window_seconds: Размер окна времени в секундах
            name: Имя для логирования
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.name = name
        
        # Очередь временных меток запросов
        self._request_times: Deque[float] = deque()
        self._lock = asyncio.Lock()
        
        logger.debug(
            f"Initialized {self.name}: {max_requests} requests per {window_seconds}s"
        )
    
    async def acquire(self) -> None:
        """Получение разрешения на выполнение запроса.
        
        Блокирует выполнение до тех пор, пока не освободится место в окне.
        """
        async with self._lock:
            current_time = time.time()
            
            # Удаляем устаревшие записи (старше window_seconds)
            while self._request_times and current_time - self._request_times[0] >= self.window_seconds:
                self._request_times.popleft()
            
            # Если лимит превышен, ждём
            if len(self._request_times) >= self.max_requests:
                # Вычисляем время, через которое освободится место
                oldest_request_time = self._request_times[0]
                wait_time = self.window_seconds - (current_time - oldest_request_time) + 0.01  # Небольшая задержка для безопасности
                
                if wait_time > 0:
                    logger.debug(
                        f"{self.name}: Rate limit reached ({len(self._request_times)}/{self.max_requests}), "
                        f"waiting {wait_time:.2f}s"
                    )
                    await asyncio.sleep(wait_time)
                    
                    # После ожидания обновляем время и очищаем устаревшие записи
                    current_time = time.time()
                    while self._request_times and current_time - self._request_times[0] >= self.window_seconds:
                        self._request_times.popleft()
            
            # Добавляем текущий запрос
            self._request_times.append(current_time)
    
    async def __aenter__(self) -> "RateLimiter":
        """Async context manager entry."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        pass
    
    def get_current_rate(self) -> float:
        """Получение текущей частоты запросов (запросов в секунду).
        
        Returns:
            Текущая частота запросов
        """
        current_time = time.time()
        
        # Удаляем устаревшие записи
        while self._request_times and current_time - self._request_times[0] >= self.window_seconds:
            self._request_times.popleft()
        
        if not self._request_times:
            return 0.0
        
        # Вычисляем частоту на основе последнего запроса
        if len(self._request_times) == 1:
            return 1.0 / self.window_seconds
        
        # Средняя частота за окно
        return len(self._request_times) / self.window_seconds
    
    def get_available_slots(self) -> int:
        """Получение количества доступных слотов для запросов.
        
        Returns:
            Количество доступных слотов
        """
        current_time = time.time()
        
        # Удаляем устаревшие записи
        while self._request_times and current_time - self._request_times[0] >= self.window_seconds:
            self._request_times.popleft()
        
        return max(0, self.max_requests - len(self._request_times))
    
    def reset(self) -> None:
        """Сброс всех записей (для тестирования или принудительного сброса)."""
        self._request_times.clear()
        logger.debug(f"{self.name}: Reset")

