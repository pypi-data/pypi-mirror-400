"""Базовый класс для провайдеров ML моделей.

Предоставляет общую функциональность для управления HTTP сессиями,
конкурентностью и обработкой ошибок.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientTimeout, TCPConnector

from obsidian_kb.providers.interfaces import ProviderHealth

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Базовый класс для всех провайдеров ML моделей.

    Предоставляет:
    - Управление HTTP сессиями и connection pool
    - Ограничение конкурентности через semaphore
    - Базовые свойства (name, model)
    - Шаблон для health_check

    Наследники должны реализовать:
    - name: str
    - model: str
    - health_check() -> ProviderHealth
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: int | float = 30,
        max_concurrent: int = 10,
        connector_limit: int | None = None,
        connector_limit_per_host: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Инициализация базового провайдера.

        Args:
            base_url: Базовый URL API
            model: Название модели
            timeout: Таймаут запросов в секундах
            max_concurrent: Максимальное количество параллельных запросов
            connector_limit: Лимит соединений для TCPConnector
            connector_limit_per_host: Лимит соединений на хост
            headers: Дополнительные HTTP заголовки
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = ClientTimeout(total=timeout)
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._session: aiohttp.ClientSession | None = None
        self._headers = headers or {}

        # TCPConnector с connection pool
        self._connector: TCPConnector | None = None
        if connector_limit or connector_limit_per_host:
            self._connector = TCPConnector(
                limit=connector_limit or 100,
                limit_per_host=connector_limit_per_host or 10,
            )

    @property
    @abstractmethod
    def name(self) -> str:
        """Имя провайдера."""
        ...

    @property
    def model(self) -> str:
        """Название модели."""
        return self._model

    @property
    def base_url(self) -> str:
        """Базовый URL API."""
        return self._base_url

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии.

        Returns:
            aiohttp.ClientSession с настроенным таймаутом и коннектором
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                connector=self._connector,
                headers=self._headers if self._headers else None,
            )
        return self._session

    async def close(self) -> None:
        """Закрытие HTTP сессии и коннектора."""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector and not self._connector.closed:
            await self._connector.close()

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Проверка доступности провайдера.

        Returns:
            ProviderHealth с информацией о статусе провайдера
        """
        ...

    async def _measure_health_check(
        self,
        check_func: Any,
    ) -> ProviderHealth:
        """Обёртка для измерения времени health_check.

        Args:
            check_func: Async функция для проверки

        Returns:
            ProviderHealth с замеренным latency
        """
        start_time = time.time()
        try:
            result = await check_func()
            latency_ms = (time.time() - start_time) * 1000
            if isinstance(result, ProviderHealth):
                result.latency_ms = latency_ms
            return result
        except asyncio.TimeoutError:
            return ProviderHealth(
                available=False,
                latency_ms=None,
                error="Timeout",
            )
        except ClientError as e:
            return ProviderHealth(
                available=False,
                latency_ms=None,
                error=f"Connection error: {e}",
            )
        except Exception as e:
            return ProviderHealth(
                available=False,
                latency_ms=None,
                error=f"Unexpected error: {e}",
            )

    async def __aenter__(self) -> "BaseProvider":
        """Вход в async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Выход из async context manager с закрытием ресурсов."""
        await self.close()
