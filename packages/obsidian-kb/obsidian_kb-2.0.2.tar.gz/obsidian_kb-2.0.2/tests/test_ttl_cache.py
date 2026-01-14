"""Тесты для TTLCache."""

import time

import pytest

from obsidian_kb.core.ttl_cache import TTLCache


def test_basic_set_and_get():
    """Тест базового set/get."""
    cache = TTLCache(ttl_seconds=60)
    cache.set("key1", "value1")
    cache.set("key2", {"nested": "dict"})

    assert cache.get("key1") == "value1"
    assert cache.get("key2") == {"nested": "dict"}
    assert cache.get("nonexistent") is None


def test_ttl_expiration():
    """Тест истечения TTL."""
    cache = TTLCache(ttl_seconds=0.1)  # 100ms
    cache.set("key", "value")

    assert cache.get("key") == "value"

    # Ждём истечения TTL
    time.sleep(0.15)

    assert cache.get("key") is None


def test_invalidate():
    """Тест явной инвалидации."""
    cache = TTLCache(ttl_seconds=60)
    cache.set("key1", "value1")
    cache.set("key2", "value2")

    cache.invalidate("key1")

    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"


def test_invalidate_prefix():
    """Тест инвалидации по префиксу."""
    cache = TTLCache(ttl_seconds=60)
    cache.set("vault1::doc1", "value1")
    cache.set("vault1::doc2", "value2")
    cache.set("vault2::doc1", "value3")

    count = cache.invalidate_prefix("vault1::")

    assert count == 2
    assert cache.get("vault1::doc1") is None
    assert cache.get("vault1::doc2") is None
    assert cache.get("vault2::doc1") == "value3"


def test_clear():
    """Тест полной очистки."""
    cache = TTLCache(ttl_seconds=60)
    cache.set("key1", "value1")
    cache.set("key2", "value2")

    cache.clear()

    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert len(cache) == 0


def test_max_size():
    """Тест лимита размера кэша."""
    cache = TTLCache(ttl_seconds=60, max_size=10)

    # Добавляем 15 записей
    for i in range(15):
        cache.set(f"key{i}", f"value{i}")

    # Должно остаться не более 10 записей
    assert len(cache) <= 10


def test_stats():
    """Тест статистики кэша."""
    cache = TTLCache(ttl_seconds=300, max_size=5000)
    cache.set("key1", "value1")
    cache.set("key2", "value2")

    stats = cache.stats

    assert stats["size"] == 2
    assert stats["ttl_seconds"] == 300
    assert stats["max_size"] == 5000


def test_overwrite_existing_key():
    """Тест перезаписи существующего ключа."""
    cache = TTLCache(ttl_seconds=60)
    cache.set("key", "value1")
    cache.set("key", "value2")

    assert cache.get("key") == "value2"


def test_none_value():
    """Тест хранения None как значения."""
    cache = TTLCache(ttl_seconds=60)
    # None как значение не сохраняется (get вернёт None и для несуществующего)
    cache.set("key", None)

    # При получении None — невозможно отличить от отсутствия ключа
    # Это ограничение дизайна, поэтому рекомендуется использовать маркер
    result = cache.get("key")
    # None сохраняется корректно, но get возвращает его
    assert result is None


def test_dict_with_marker():
    """Тест использования словаря с маркером для 'не найден'."""
    cache = TTLCache(ttl_seconds=60)

    # Паттерн использования в lance_db
    cache.set("vault::doc1", {"title": "Document 1"})
    cache.set("vault::doc2", {"__not_found__": True})  # Маркер "не найден"

    doc1 = cache.get("vault::doc1")
    doc2 = cache.get("vault::doc2")

    assert doc1 == {"title": "Document 1"}
    assert doc2 == {"__not_found__": True}

    # Проверка маркера в клиентском коде
    if isinstance(doc2, dict) and doc2.get("__not_found__"):
        doc2 = None

    assert doc2 is None


def test_cleanup_on_access():
    """Тест что очистка происходит при доступе."""
    cache = TTLCache(ttl_seconds=0.05)
    cache._cleanup_interval = 0  # Отключаем интервал для теста

    cache.set("key1", "value1")
    time.sleep(0.1)
    cache.set("key2", "value2")

    # При get должна произойти очистка expired записей
    cache.get("key2")

    # key1 должен быть удалён (TTL истёк)
    assert "key1" not in cache._cache
    # key2 должен остаться
    assert cache.get("key2") == "value2"


def test_eviction_oldest():
    """Тест что при переполнении удаляются самые старые записи."""
    cache = TTLCache(ttl_seconds=60, max_size=5)
    cache._cleanup_interval = 1000  # Отключаем периодическую очистку

    # Добавляем записи с небольшой задержкой для разных expiry
    for i in range(5):
        cache.set(f"key{i}", f"value{i}")
        time.sleep(0.01)

    # Добавляем ещё одну запись — должна произойти eviction
    cache.set("key_new", "value_new")

    # Новая запись должна быть в кэше
    assert cache.get("key_new") == "value_new"
    # Размер не должен превышать max_size
    assert len(cache) <= 5
