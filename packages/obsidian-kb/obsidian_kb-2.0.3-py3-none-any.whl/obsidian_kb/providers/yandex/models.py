"""Реестр моделей Yandex Cloud AI Studio.

Содержит список доступных моделей с метаданными:
- Название и ID модели
- Размер контекста
- Тип API (gRPC SDK или OpenAI-compatible HTTP)

Документация:
- Модели: https://yandex.cloud/ru/docs/ai-studio/concepts/generation/models
- OpenAI API: https://yandex.cloud/ru/docs/ai-studio/concepts/openai-compatibility

Актуально на: январь 2026
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class YandexModel:
    """Описание модели Yandex Cloud."""

    id: str  # ID модели для API (например, "yandexgpt/latest")
    name: str  # Человекочитаемое название
    context_size: int  # Размер контекста в токенах
    api_type: Literal["grpc", "openai"]  # Тип API: gRPC SDK или OpenAI-compatible
    description: str | None = None  # Дополнительное описание


# Реестр chat моделей Yandex Cloud
YANDEX_CHAT_MODELS: dict[str, YandexModel] = {
    # YandexGPT модели (gRPC SDK)
    "aliceai-llm": YandexModel(
        id="aliceai-llm",
        name="Alice AI LLM",
        context_size=32_768,
        api_type="grpc",
        description="Модель Alice AI",
    ),
    "yandexgpt/rc": YandexModel(
        id="yandexgpt/rc",
        name="YandexGPT Pro 5.1",
        context_size=32_768,
        api_type="grpc",
        description="Release Candidate - новейшая версия",
    ),
    "yandexgpt/latest": YandexModel(
        id="yandexgpt/latest",
        name="YandexGPT Pro 5",
        context_size=32_768,
        api_type="grpc",
        description="Стабильная версия YandexGPT Pro",
    ),
    "yandexgpt-lite": YandexModel(
        id="yandexgpt-lite",
        name="YandexGPT Lite 5",
        context_size=32_768,
        api_type="grpc",
        description="Облегчённая версия, быстрее и дешевле",
    ),
    # Open Source модели (OpenAI-compatible HTTP API)
    "qwen3-235b-a22b-fp8/latest": YandexModel(
        id="qwen3-235b-a22b-fp8/latest",
        name="Qwen3 235B",
        context_size=262_144,
        api_type="openai",
        description="Qwen3 235B - большой контекст 262K токенов",
    ),
    "gpt-oss-120b/latest": YandexModel(
        id="gpt-oss-120b/latest",
        name="gpt-oss-120b",
        context_size=131_072,
        api_type="openai",
        description="Open source модель 120B параметров",
    ),
    "gpt-oss-20b/latest": YandexModel(
        id="gpt-oss-20b/latest",
        name="gpt-oss-20b",
        context_size=131_072,
        api_type="openai",
        description="Open source модель 20B параметров, быстрая",
    ),
    "gemma-3-27b-it/latest": YandexModel(
        id="gemma-3-27b-it/latest",
        name="Gemma 3 27B",
        context_size=131_072,
        api_type="openai",
        description="Google Gemma 3 27B Instruct",
    ),
}

# Алиасы для удобства (короткие имена → полные ID)
YANDEX_MODEL_ALIASES: dict[str, str] = {
    # YandexGPT
    "yandexgpt": "yandexgpt/latest",
    "yandexgpt-pro": "yandexgpt/latest",
    "yandexgpt-pro-5": "yandexgpt/latest",
    "yandexgpt-pro-5.1": "yandexgpt/rc",
    "yandexgpt-lite-5": "yandexgpt-lite",
    "alice": "aliceai-llm",
    # Open Source
    "qwen": "qwen3-235b-a22b-fp8/latest",
    "qwen3": "qwen3-235b-a22b-fp8/latest",
    "qwen3-235b": "qwen3-235b-a22b-fp8/latest",
    "gpt-oss-120b": "gpt-oss-120b/latest",
    "gpt-oss-20b": "gpt-oss-20b/latest",
    "gemma": "gemma-3-27b-it/latest",
    "gemma-3": "gemma-3-27b-it/latest",
    "gemma-3-27b": "gemma-3-27b-it/latest",
}


def get_yandex_model(model_id: str) -> YandexModel | None:
    """Получить модель по ID или алиасу.

    Args:
        model_id: ID модели или алиас

    Returns:
        YandexModel или None если модель не найдена
    """
    # Нормализуем ID
    model_id_lower = model_id.lower().strip()

    # Проверяем алиасы
    if model_id_lower in YANDEX_MODEL_ALIASES:
        model_id_lower = YANDEX_MODEL_ALIASES[model_id_lower]

    # Ищем в реестре
    return YANDEX_CHAT_MODELS.get(model_id_lower)


def is_valid_yandex_model(model_id: str) -> bool:
    """Проверить, является ли модель валидной.

    Args:
        model_id: ID модели или алиас

    Returns:
        True если модель существует в реестре
    """
    return get_yandex_model(model_id) is not None


def resolve_yandex_model_id(model_id: str) -> str | None:
    """Разрешить алиас в полный ID модели.

    Args:
        model_id: ID модели или алиас

    Returns:
        Полный ID модели или None если не найден
    """
    model = get_yandex_model(model_id)
    return model.id if model else None


def list_yandex_models() -> list[YandexModel]:
    """Получить список всех доступных моделей.

    Returns:
        Список моделей, отсортированный по имени
    """
    return sorted(YANDEX_CHAT_MODELS.values(), key=lambda m: m.name)


def format_models_table() -> str:
    """Форматировать таблицу моделей для отображения.

    Returns:
        Markdown таблица с моделями
    """
    lines = [
        "| Модель | ID | Контекст | API |",
        "|--------|-----|----------|-----|",
    ]

    for model in list_yandex_models():
        context_str = f"{model.context_size:,}".replace(",", " ")
        api_str = "gRPC SDK" if model.api_type == "grpc" else "OpenAI HTTP"
        lines.append(f"| {model.name} | `{model.id}` | {context_str} | {api_str} |")

    return "\n".join(lines)
