"""Модуль TTLCache — кэш с поддержкой TTL (Time-To-Live)."""

import heapq
import time
from typing import Any


class TTLCache:
    """Простой кэш с поддержкой TTL (Time-To-Live).

    Записи автоматически истекают после указанного времени.
    Очистка устаревших записей происходит при обращении к кэшу.

    Оптимизация Phase 4:
    - Используется heapq для отслеживания expiry, что обеспечивает O(expired)
      вместо O(all) при очистке устаревших записей.

    Пример:
        cache = TTLCache(ttl_seconds=300)  # 5 минут
        cache.set("key", "value")
        cache.get("key")  # "value"
        # Через 5 минут
        cache.get("key")  # None
    """

    def __init__(self, ttl_seconds: float = 300.0, max_size: int = 10000) -> None:
        """Инициализация TTL кэша.

        Args:
            ttl_seconds: Время жизни записи в секундах (по умолчанию 5 минут)
            max_size: Максимальный размер кэша (по умолчанию 10000 записей)
        """
        self._cache: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._last_cleanup = time.monotonic()
        self._cleanup_interval = 60.0  # Очистка не чаще раза в минуту
        # Heap для быстрого доступа к expired записям: (expiry_time, key)
        self._expiry_heap: list[tuple[float, str]] = []

    def get(self, key: str) -> Any | None:
        """Получение значения из кэша.

        Args:
            key: Ключ записи

        Returns:
            Значение или None если ключ не найден или истёк
        """
        self._maybe_cleanup()

        entry = self._cache.get(key)
        if entry is None:
            return None

        value, expiry = entry
        if time.monotonic() > expiry:
            # Запись истекла
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        """Установка значения в кэш.

        Args:
            key: Ключ записи
            value: Значение для сохранения
        """
        self._maybe_cleanup()

        # Удаляем старые записи если превышен лимит
        if len(self._cache) >= self._max_size and key not in self._cache:
            self._evict_oldest()

        expiry = time.monotonic() + self._ttl
        self._cache[key] = (value, expiry)
        # Добавляем в heap для отслеживания expiry
        heapq.heappush(self._expiry_heap, (expiry, key))

    def invalidate(self, key: str) -> None:
        """Инвалидация (удаление) записи из кэша.

        Args:
            key: Ключ записи для удаления
        """
        self._cache.pop(key, None)
        # Не удаляем из heap — будет удалено при cleanup

    def invalidate_prefix(self, prefix: str) -> int:
        """Инвалидация всех записей с указанным префиксом.

        Args:
            prefix: Префикс ключей для удаления

        Returns:
            Количество удалённых записей
        """
        keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)

    def clear(self) -> None:
        """Полная очистка кэша."""
        self._cache.clear()
        self._expiry_heap.clear()

    def _maybe_cleanup(self) -> None:
        """Очистка устаревших записей (не чаще раза в минуту).

        Оптимизация: O(expired) вместо O(all) благодаря использованию heapq.
        """
        now = time.monotonic()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = now

        # Удаляем все истёкшие записи из heap
        while self._expiry_heap and self._expiry_heap[0][0] < now:
            expiry, key = heapq.heappop(self._expiry_heap)
            # Проверяем, что запись всё ещё в кэше и не была обновлена
            if key in self._cache:
                cached_value, cached_expiry = self._cache[key]
                # Удаляем только если expiry совпадает (не было обновления)
                if cached_expiry <= now:
                    del self._cache[key]

    def _evict_oldest(self) -> None:
        """Удаление самых старых записей при превышении лимита."""
        # Сортируем по времени истечения (самые старые первые)
        sorted_items = sorted(
            self._cache.items(), key=lambda x: x[1][1]
        )
        # Удаляем 10% самых старых записей
        to_remove = max(1, len(sorted_items) // 10)
        for key, _ in sorted_items[:to_remove]:
            del self._cache[key]

    def __len__(self) -> int:
        """Количество записей в кэше (включая устаревшие)."""
        return len(self._cache)

    @property
    def stats(self) -> dict[str, Any]:
        """Статистика кэша.

        Returns:
            Словарь со статистикой: size, ttl_seconds, max_size, heap_size
        """
        return {
            "size": len(self._cache),
            "ttl_seconds": self._ttl,
            "max_size": self._max_size,
            "heap_size": len(self._expiry_heap),
        }
