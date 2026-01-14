"""Модуль для мониторинга производительности операций."""

import asyncio
import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class OperationMetrics:
    """Метрики для одной операции."""
    
    operation_name: str
    count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    times: deque = field(default_factory=lambda: deque(maxlen=1000))  # Последние 1000 измерений
    
    @property
    def avg_time(self) -> float:
        """Среднее время выполнения."""
        return self.total_time / self.count if self.count > 0 else 0.0
    
    @property
    def p50(self) -> float:
        """50-й перцентиль времени выполнения."""
        return self._percentile(50)
    
    @property
    def p95(self) -> float:
        """95-й перцентиль времени выполнения."""
        return self._percentile(95)
    
    @property
    def p99(self) -> float:
        """99-й перцентиль времени выполнения."""
        return self._percentile(99)
    
    def _percentile(self, percentile: int) -> float:
        """Вычисление перцентиля времени выполнения.
        
        Args:
            percentile: Процент (0-100)
            
        Returns:
            Значение перцентиля
        """
        if not self.times:
            return 0.0
        
        sorted_times = sorted(self.times)
        index = int(len(sorted_times) * percentile / 100)
        index = min(index, len(sorted_times) - 1)
        return sorted_times[index]
    
    def record(self, duration: float) -> None:
        """Запись времени выполнения операции.
        
        Args:
            duration: Время выполнения в секундах
        """
        self.count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.times.append(duration)


@dataclass
class PerformanceReport:
    """Отчет о производительности."""
    
    operation_name: str
    count: int
    avg_time: float
    min_time: float
    max_time: float
    p50: float
    p95: float
    p99: float
    timestamp: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """Монитор производительности операций.
    
    Собирает метрики времени выполнения операций и вычисляет перцентили.
    Поддерживает алерты на медленные операции.
    """
    
    def __init__(
        self,
        alert_threshold_seconds: float = 5.0,
        alert_callback: Any | None = None,
    ) -> None:
        """Инициализация монитора.
        
        Args:
            alert_threshold_seconds: Порог времени выполнения для алерта (в секундах)
            alert_callback: Callback функция для вызова при медленных операциях
                Должна принимать (operation_name: str, duration: float, threshold: float)
        """
        self._metrics: dict[str, OperationMetrics] = defaultdict(
            lambda: OperationMetrics(operation_name="")
        )
        self._lock = asyncio.Lock()
        self.alert_threshold = alert_threshold_seconds
        self.alert_callback = alert_callback
    
    @asynccontextmanager
    async def measure(self, operation_name: str):
        """Измерение времени выполнения операции (context manager).
        
        Args:
            operation_name: Имя операции для измерения
            
        Yields:
            None
            
        Examples:
            >>> monitor = PerformanceMonitor()
            >>> async with monitor.measure("search"):
            ...     results = await search(query)
            >>> report = monitor.get_report("search")
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            await self.record(operation_name, duration)
    
    async def record(self, operation_name: str, duration: float) -> None:
        """Запись времени выполнения операции.
        
        Args:
            operation_name: Имя операции
            duration: Время выполнения в секундах
        """
        async with self._lock:
            if operation_name not in self._metrics:
                self._metrics[operation_name] = OperationMetrics(operation_name=operation_name)
            self._metrics[operation_name].record(duration)
            
            # Проверяем порог для алерта
            if duration > self.alert_threshold:
                self._trigger_alert(operation_name, duration)
    
    def _trigger_alert(self, operation_name: str, duration: float) -> None:
        """Триггер алерта на медленную операцию.
        
        Args:
            operation_name: Имя операции
            duration: Время выполнения в секундах
        """
        alert_message = (
            f"Медленная операция: {operation_name} заняла {duration:.2f}с "
            f"(порог: {self.alert_threshold:.2f}с)"
        )
        logger.warning(alert_message, extra={
            "operation": operation_name,
            "duration": duration,
            "threshold": self.alert_threshold,
            "alert_type": "slow_operation",
        })
        
        # Вызываем callback если есть
        if self.alert_callback:
            try:
                if asyncio.iscoroutinefunction(self.alert_callback):
                    # Для async callback нужно вызывать через asyncio.create_task
                    # Но здесь мы в sync контексте, поэтому просто логируем
                    logger.debug(f"Async alert callback для {operation_name} пропущен (sync контекст)")
                else:
                    self.alert_callback(operation_name, duration, self.alert_threshold)
            except Exception as e:
                logger.error(f"Ошибка при вызове alert callback: {e}")
    
    def get_metrics(self, operation_name: str) -> OperationMetrics | None:
        """Получение метрик для операции.
        
        Args:
            operation_name: Имя операции
            
        Returns:
            Метрики операции или None если операция не найдена
        """
        return self._metrics.get(operation_name)
    
    def get_report(self, operation_name: str) -> PerformanceReport | None:
        """Получение отчета о производительности для операции.
        
        Args:
            operation_name: Имя операции
            
        Returns:
            Отчет о производительности или None если операция не найдена
        """
        metrics = self.get_metrics(operation_name)
        if not metrics or metrics.count == 0:
            return None
        
        return PerformanceReport(
            operation_name=operation_name,
            count=metrics.count,
            avg_time=metrics.avg_time,
            min_time=metrics.min_time if metrics.min_time != float('inf') else 0.0,
            max_time=metrics.max_time,
            p50=metrics.p50,
            p95=metrics.p95,
            p99=metrics.p99,
        )
    
    def get_all_reports(self) -> list[PerformanceReport]:
        """Получение отчетов для всех операций.
        
        Returns:
            Список отчетов о производительности
        """
        reports = []
        for operation_name in self._metrics:
            report = self.get_report(operation_name)
            if report:
                reports.append(report)
        return reports
    
    def reset(self, operation_name: str | None = None) -> None:
        """Сброс метрик.
        
        Args:
            operation_name: Имя операции для сброса (None для сброса всех)
        """
        if operation_name:
            if operation_name in self._metrics:
                del self._metrics[operation_name]
        else:
            self._metrics.clear()
    
    def get_summary(self) -> dict[str, Any]:
        """Получение сводки по всем операциям.
        
        Returns:
            Словарь со сводкой метрик
        """
        summary: dict[str, Any] = {
            "operations": {},
            "total_operations": 0,
        }
        
        for operation_name, metrics in self._metrics.items():
            if metrics.count > 0:
                summary["operations"][operation_name] = {
                    "count": metrics.count,
                    "avg_time": metrics.avg_time,
                    "min_time": metrics.min_time if metrics.min_time != float('inf') else 0.0,
                    "max_time": metrics.max_time,
                    "p50": metrics.p50,
                    "p95": metrics.p95,
                    "p99": metrics.p99,
                }
                summary["total_operations"] += metrics.count
        
        return summary

