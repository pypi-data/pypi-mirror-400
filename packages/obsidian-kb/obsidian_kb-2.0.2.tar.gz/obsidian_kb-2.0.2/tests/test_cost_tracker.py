"""Тесты для CostTracker."""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from obsidian_kb.quality.cost_tracker import CostTracker, OperationType


@pytest.fixture
def cost_tracker(tmp_path):
    """CostTracker для тестов с изолированной БД для каждого теста."""
    # Создаём уникальную БД для каждого теста
    db_path = tmp_path / f"costs_{id(tmp_path)}"
    return CostTracker(db_path=db_path)


@pytest.mark.asyncio
async def test_record_cost_embedding(cost_tracker):
    """Тест записи затрат на embedding операцию."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
        vault_name="test_vault",
    )
    
    # Получаем затраты
    costs = await cost_tracker.get_costs(vault_name="test_vault")
    
    assert costs["total_cost_usd"] > 0
    assert costs["total_input_tokens"] == 1000
    assert costs["record_count"] == 1
    assert "yandex" in costs["by_provider"]


@pytest.mark.asyncio
async def test_record_cost_chat_completion(cost_tracker):
    """Тест записи затрат на chat completion операцию."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandexgpt",
        operation_type=OperationType.CHAT_COMPLETION,
        input_tokens=500,
        output_tokens=200,
        vault_name="test_vault",
    )
    
    costs = await cost_tracker.get_costs(vault_name="test_vault")
    
    assert costs["total_cost_usd"] > 0
    assert costs["total_input_tokens"] == 500
    assert costs["total_output_tokens"] == 200
    assert costs["record_count"] == 1


@pytest.mark.asyncio
async def test_record_cost_ollama_free(cost_tracker):
    """Тест, что Ollama операции бесплатны."""
    await cost_tracker.record_cost(
        provider="ollama",
        model="llama2",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    costs = await cost_tracker.get_costs()
    
    assert costs["total_cost_usd"] == 0.0
    assert costs["total_input_tokens"] == 1000


@pytest.mark.asyncio
async def test_record_cost_with_metadata(cost_tracker):
    """Тест записи затрат с метаданными."""
    metadata = {"job_id": "test-job-1", "operation": "indexing"}
    
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
        metadata=metadata,
    )
    
    costs = await cost_tracker.get_costs()
    assert costs["record_count"] == 1


@pytest.mark.asyncio
async def test_record_cost_custom_cost(cost_tracker):
    """Тест записи затрат с указанной стоимостью."""
    custom_cost = 0.05
    
    await cost_tracker.record_cost(
        provider="custom",
        model="custom-model",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
        cost_usd=custom_cost,
    )
    
    costs = await cost_tracker.get_costs()
    assert costs["total_cost_usd"] == custom_cost


@pytest.mark.asyncio
async def test_get_costs_filter_by_vault(cost_tracker):
    """Тест фильтрации затрат по vault."""
    # Записываем затраты для разных vault'ов
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
        vault_name="vault1",
    )
    
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=2000,
        vault_name="vault2",
    )
    
    # Получаем затраты только для vault1
    costs_vault1 = await cost_tracker.get_costs(vault_name="vault1")
    assert costs_vault1["total_input_tokens"] == 1000
    
    # Получаем затраты только для vault2
    costs_vault2 = await cost_tracker.get_costs(vault_name="vault2")
    assert costs_vault2["total_input_tokens"] == 2000


@pytest.mark.asyncio
async def test_get_costs_filter_by_provider(cost_tracker):
    """Тест фильтрации затрат по провайдеру."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    await cost_tracker.record_cost(
        provider="openai",
        model="text-embedding-ada-002",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    # Получаем затраты только для yandex
    costs_yandex = await cost_tracker.get_costs(provider="yandex")
    assert costs_yandex["record_count"] == 1
    assert "yandex" in costs_yandex["by_provider"]
    
    # Получаем затраты только для openai
    costs_openai = await cost_tracker.get_costs(provider="openai")
    assert costs_openai["record_count"] == 1
    assert "openai" in costs_openai["by_provider"]


@pytest.mark.asyncio
async def test_get_costs_filter_by_operation_type(cost_tracker):
    """Тест фильтрации затрат по типу операции."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandexgpt",
        operation_type=OperationType.CHAT_COMPLETION,
        input_tokens=500,
        output_tokens=200,
    )
    
    # Получаем затраты только для embedding
    costs_embedding = await cost_tracker.get_costs(operation_type=OperationType.EMBEDDING)
    assert costs_embedding["record_count"] == 1
    assert OperationType.EMBEDDING.value in costs_embedding["by_operation"]
    
    # Получаем затраты только для chat_completion
    costs_chat = await cost_tracker.get_costs(operation_type=OperationType.CHAT_COMPLETION)
    assert costs_chat["record_count"] == 1
    assert OperationType.CHAT_COMPLETION.value in costs_chat["by_operation"]


@pytest.mark.asyncio
async def test_get_costs_period_day(cost_tracker):
    """Тест получения затрат за день."""
    # Записываем затраты сейчас
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    costs = await cost_tracker.get_costs(period="day")
    
    assert costs["record_count"] >= 1
    assert "period_start" in costs
    assert "period_end" in costs


@pytest.mark.asyncio
async def test_get_costs_period_week(cost_tracker):
    """Тест получения затрат за неделю."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    costs = await cost_tracker.get_costs(period="week")
    
    assert costs["record_count"] >= 1


@pytest.mark.asyncio
async def test_get_costs_period_month(cost_tracker):
    """Тест получения затрат за месяц."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    costs = await cost_tracker.get_costs(period="month")
    
    assert costs["record_count"] >= 1


@pytest.mark.asyncio
async def test_get_costs_period_all(cost_tracker):
    """Тест получения всех затрат."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    costs = await cost_tracker.get_costs(period="all")
    
    assert costs["record_count"] >= 1


@pytest.mark.asyncio
async def test_get_costs_breakdown_by_provider(cost_tracker):
    """Тест разбивки затрат по провайдерам."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    await cost_tracker.record_cost(
        provider="openai",
        model="text-embedding-ada-002",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    costs = await cost_tracker.get_costs()
    
    assert "yandex" in costs["by_provider"]
    assert "openai" in costs["by_provider"]
    assert len(costs["by_provider"]) == 2


@pytest.mark.asyncio
async def test_get_costs_breakdown_by_vault(cost_tracker):
    """Тест разбивки затрат по vault'ам."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
        vault_name="vault1",
    )
    
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=2000,
        vault_name="vault2",
    )
    
    costs = await cost_tracker.get_costs()
    
    assert "vault1" in costs["by_vault"]
    assert "vault2" in costs["by_vault"]
    assert len(costs["by_vault"]) == 2


@pytest.mark.asyncio
async def test_get_costs_breakdown_by_operation(cost_tracker):
    """Тест разбивки затрат по типам операций."""
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
    )
    
    await cost_tracker.record_cost(
        provider="yandex",
        model="yandexgpt",
        operation_type=OperationType.CHAT_COMPLETION,
        input_tokens=500,
        output_tokens=200,
    )
    
    costs = await cost_tracker.get_costs()
    
    assert OperationType.EMBEDDING.value in costs["by_operation"]
    assert OperationType.CHAT_COMPLETION.value in costs["by_operation"]
    assert len(costs["by_operation"]) == 2


@pytest.mark.asyncio
async def test_calculate_cost_yandex_embedding(cost_tracker):
    """Тест вычисления стоимости для Yandex embedding."""
    cost = cost_tracker._calculate_cost(
        provider="yandex",
        model="yandex-embedding",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1_000_000,  # 1M токенов
        output_tokens=0,
    )
    
    # Примерная стоимость: ~$0.01 за 1M токенов
    assert cost > 0
    assert cost < 0.02  # Должно быть около $0.01


@pytest.mark.asyncio
async def test_calculate_cost_yandex_chat(cost_tracker):
    """Тест вычисления стоимости для Yandex chat completion."""
    cost = cost_tracker._calculate_cost(
        provider="yandex",
        model="yandexgpt",
        operation_type=OperationType.CHAT_COMPLETION,
        input_tokens=1000,
        output_tokens=1000,
    )
    
    # Примерная стоимость: ~$0.002 за 1K входных + ~$0.006 за 1K выходных = ~$0.008
    assert cost > 0
    assert cost < 0.01


@pytest.mark.asyncio
async def test_calculate_cost_openai_embedding(cost_tracker):
    """Тест вычисления стоимости для OpenAI embedding."""
    cost = cost_tracker._calculate_cost(
        provider="openai",
        model="text-embedding-ada-002",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
        output_tokens=0,
    )
    
    # Примерная стоимость: $0.0001 за 1K токенов
    assert cost > 0
    assert cost < 0.001


@pytest.mark.asyncio
async def test_calculate_cost_openai_chat_gpt4(cost_tracker):
    """Тест вычисления стоимости для OpenAI GPT-4."""
    cost = cost_tracker._calculate_cost(
        provider="openai",
        model="gpt-4",
        operation_type=OperationType.CHAT_COMPLETION,
        input_tokens=1000,
        output_tokens=1000,
    )
    
    # Примерная стоимость: ~$0.03 за 1K входных + ~$0.06 за 1K выходных = ~$0.09
    assert cost > 0
    assert cost < 0.1


@pytest.mark.asyncio
async def test_calculate_cost_unknown_provider(cost_tracker):
    """Тест вычисления стоимости для неизвестного провайдера."""
    cost = cost_tracker._calculate_cost(
        provider="unknown",
        model="unknown-model",
        operation_type=OperationType.EMBEDDING,
        input_tokens=1000,
        output_tokens=0,
    )
    
    # Должно вернуть 0 для неизвестного провайдера
    assert cost == 0.0


@pytest.mark.asyncio
async def test_get_costs_empty(cost_tracker):
    """Тест получения затрат для пустой БД."""
    costs = await cost_tracker.get_costs()
    
    assert costs["total_cost_usd"] == 0.0
    assert costs["total_input_tokens"] == 0
    assert costs["total_output_tokens"] == 0
    assert costs["record_count"] == 0
    assert len(costs["by_provider"]) == 0
    assert len(costs["by_vault"]) == 0
    assert len(costs["by_operation"]) == 0

