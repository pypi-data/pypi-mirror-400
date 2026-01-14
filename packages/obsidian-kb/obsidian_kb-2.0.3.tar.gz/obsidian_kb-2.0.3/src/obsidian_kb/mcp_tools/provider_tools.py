"""MCP tools для управления LLM провайдерами."""

import asyncio
import logging
import time
from typing import TYPE_CHECKING

from obsidian_kb.config.manager import get_config_manager
from obsidian_kb.providers.factory import ProviderFactory
from obsidian_kb.providers.interfaces import ProviderHealth
from obsidian_kb.providers.yandex.models import (
    format_models_table as format_yandex_models_table,
    get_yandex_model,
    is_valid_yandex_model,
    resolve_yandex_model_id,
)
from obsidian_kb.service_container import get_service_container
from obsidian_kb.types import VaultNotFoundError

if TYPE_CHECKING:
    from obsidian_kb.providers.interfaces import IChatCompletionProvider, IEmbeddingProvider

logger = logging.getLogger(__name__)

# Глобальный контейнер сервисов
services = get_service_container()


# Список поддерживаемых провайдеров
SUPPORTED_PROVIDERS = ["ollama", "yandex"]

# Информация о стоимости провайдеров ($/1M tokens)
PROVIDER_COSTS = {
    "ollama": {
        "embedding": 0.0,  # Бесплатно (локально)
        "chat": 0.0,
    },
    "yandex": {
        "embedding": 0.5,  # Примерная стоимость
        "chat": 2.0,
    },
}


async def list_providers() -> str:
    """Список доступных LLM-провайдеров.

    Returns:
        Markdown таблица с провайдерами:
        - Имя провайдера
        - Тип (embedding / chat / both)
        - Статус (active / available / unavailable)
        - Текущие модели
        - Стоимость ($/1M tokens)
    """
    try:
        lines = ["## Доступные LLM-провайдеры\n"]

        # Получаем текущую конфигурацию
        config_manager = get_config_manager()
        global_config = config_manager.get_config()

        # Модели из конфига (для отображения кастомных настроек)
        config_embedding_model = global_config.providers.embedding_model
        config_chat_model = global_config.providers.chat_model

        # Проверяем каждый провайдер
        provider_info = []

        for provider_name in SUPPORTED_PROVIDERS:
            # Проверяем embedding провайдер
            embedding_available = False
            embedding_status = "unavailable"
            embedding_model = "N/A"
            embedding_dimensions = None
            embedding_latency = None

            try:
                # Передаём модель из конфига, если провайдер активен
                model_for_check = config_embedding_model if global_config.providers.embedding == provider_name else None
                provider = ProviderFactory.get_embedding_provider(provider_name=provider_name, model=model_for_check)
                health = await provider.health_check()
                embedding_available = health.available
                embedding_status = "available" if health.available else "unavailable"
                embedding_model = provider.model
                embedding_dimensions = health.dimensions
                embedding_latency = health.latency_ms
            except Exception as e:
                logger.debug(f"Embedding provider {provider_name} not available: {e}")

            # Проверяем chat провайдер
            chat_available = False
            chat_status = "unavailable"
            chat_model = "N/A"
            chat_latency = None

            try:
                # Передаём модель из конфига, если провайдер активен
                model_for_check = config_chat_model if global_config.providers.chat == provider_name else None
                provider = ProviderFactory.get_chat_provider(provider_name=provider_name, model=model_for_check)
                health = await provider.health_check()
                chat_available = health.available
                chat_status = "available" if health.available else "unavailable"
                chat_model = provider.model
                chat_latency = health.latency_ms
            except Exception as e:
                logger.debug(f"Chat provider {provider_name} not available: {e}")
            
            # Определяем тип и статус
            provider_type = []
            if embedding_available:
                provider_type.append("embedding")
            if chat_available:
                provider_type.append("chat")
            
            if not provider_type:
                provider_type_str = "unavailable"
            else:
                provider_type_str = " / ".join(provider_type)
            
            # Определяем активность
            is_active_embedding = global_config.providers.embedding == provider_name
            is_active_chat = global_config.providers.chat == provider_name
            active_status = []
            if is_active_embedding:
                active_status.append("embedding")
            if is_active_chat:
                active_status.append("chat")
            
            status_str = "active" if active_status else ("available" if provider_type else "unavailable")
            
            # Стоимость
            cost_info = PROVIDER_COSTS.get(provider_name, {})
            embedding_cost = cost_info.get("embedding", 0.0)
            chat_cost = cost_info.get("chat", 0.0)
            
            provider_info.append({
                "name": provider_name,
                "type": provider_type_str,
                "status": status_str,
                "active": ", ".join(active_status) if active_status else "—",
                "embedding_model": embedding_model,
                "embedding_dimensions": embedding_dimensions,
                "embedding_latency": embedding_latency,
                "chat_model": chat_model,
                "chat_latency": chat_latency,
                "embedding_cost": embedding_cost,
                "chat_cost": chat_cost,
            })
        
        # Формируем таблицу
        lines.append("| Провайдер | Тип | Статус | Активен | Embedding модель | Размерность | Chat модель | Embedding $/1M | Chat $/1M |")
        lines.append("|-----------|-----|--------|---------|------------------|-------------|-------------|----------------|-----------|")
        
        for info in provider_info:
            embedding_dims = str(info["embedding_dimensions"]) if info["embedding_dimensions"] else "—"
            embedding_lat = f"{info['embedding_latency']:.0f}ms" if info["embedding_latency"] else "—"
            chat_lat = f"{info['chat_latency']:.0f}ms" if info["chat_latency"] else "—"
            
            status_emoji = {
                "active": "✅",
                "available": "⚪",
                "unavailable": "❌",
            }.get(info["status"], "❓")
            
            lines.append(
                f"| {info['name']} | {info['type']} | {status_emoji} {info['status']} | {info['active']} | "
                f"{info['embedding_model']} | {embedding_dims} | {info['chat_model']} | "
                f"${info['embedding_cost']:.2f} | ${info['chat_cost']:.2f} |"
            )
        
        lines.append("")
        lines.append("### Легенда")
        lines.append("- ✅ **active**: Провайдер активен и используется")
        lines.append("- ⚪ **available**: Провайдер доступен, но не активен")
        lines.append("- ❌ **unavailable**: Провайдер недоступен или не настроен")
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.error(f"Error in list_providers: {e}", exc_info=True)
        return f"❌ Ошибка получения списка провайдеров: {e}"


async def set_provider(
    provider_type: str,  # embedding | chat
    provider_name: str,  # ollama | yandex
    vault_name: str | None = None,  # None = глобально
    model: str | None = None,  # None = default для провайдера
) -> str:
    """Установка провайдера для операций.

    Args:
        provider_type: Тип провайдера (embedding | chat)
        provider_name: Имя провайдера (ollama | yandex)
        vault_name: Применить только к vault'у (None = глобально)
        model: Конкретная модель (None = default)

    Returns:
        Подтверждение изменения

    Examples:
        # Глобально переключить embedding на Yandex
        set_provider("embedding", "yandex")

        # Для конкретного vault использовать Yandex
        set_provider("embedding", "yandex", vault_name="naumen-cto", model="text-search-doc/latest")

    ⚠️ При смене embedding провайдера с другой размерностью
       потребуется переиндексация vault'а.
    """
    try:
        # Валидация параметров
        if provider_type not in ("embedding", "chat"):
            return f"❌ Неверный тип провайдера: {provider_type}. Допустимые значения: embedding, chat"

        if provider_name.lower() not in SUPPORTED_PROVIDERS:
            return f"❌ Неподдерживаемый провайдер: {provider_name}. Допустимые: {', '.join(SUPPORTED_PROVIDERS)}"

        provider_name = provider_name.lower()

        # Валидация модели для Yandex chat провайдера
        resolved_model = model
        if provider_name == "yandex" and provider_type == "chat" and model:
            if not is_valid_yandex_model(model):
                # Модель не найдена в реестре
                lines = [
                    f"❌ Неизвестная модель Yandex: `{model}`\n",
                    "### Доступные модели Yandex Cloud\n",
                    format_yandex_models_table(),
                    "\n### Алиасы",
                    "Можно использовать короткие имена: `qwen`, `gemma`, `yandexgpt`, `alice`",
                ]
                return "\n".join(lines)

            # Разрешаем алиас в полный ID
            resolved_model = resolve_yandex_model_id(model)
            model_info = get_yandex_model(model)

        # Проверяем доступность провайдера
        try:
            if provider_type == "embedding":
                test_provider = ProviderFactory.get_embedding_provider(
                    provider_name=provider_name, model=resolved_model
                )
                health = await test_provider.health_check()
                if not health.available:
                    return f"❌ Провайдер {provider_name} недоступен: {health.error or 'Unknown error'}"

                # Проверяем размерность для embedding провайдеров
                new_dimensions = health.dimensions
                if vault_name and new_dimensions:
                    # Проверяем текущую размерность в индексе
                    try:
                        # Получаем текущий провайдер из конфигурации
                        config_manager = get_config_manager()
                        current_config = config_manager.get_config(vault_name)
                        current_provider_name = current_config.providers.embedding

                        if current_provider_name != provider_name:
                            # Получаем размерность текущего провайдера
                            try:
                                current_provider = ProviderFactory.get_embedding_provider(
                                    provider_name=current_provider_name
                                )
                                current_health = await current_provider.health_check()
                                current_dimensions = current_health.dimensions

                                if current_dimensions and current_dimensions != new_dimensions:
                                    warning = (
                                        f"⚠️ **Внимание:** Размерность embedding изменится "
                                        f"({current_dimensions} → {new_dimensions}). "
                                        f"Потребуется переиндексация vault'а.\n\n"
                                    )
                                else:
                                    warning = ""
                            except Exception:
                                warning = ""
                        else:
                            warning = ""
                    except Exception:
                        warning = ""
                else:
                    warning = ""
            else:
                test_provider = ProviderFactory.get_chat_provider(
                    provider_name=provider_name, model=resolved_model
                )
                health = await test_provider.health_check()
                if not health.available:
                    return f"❌ Провайдер {provider_name} недоступен: {health.error or 'Unknown error'}"
                warning = ""
        except Exception as e:
            return f"❌ Ошибка проверки провайдера: {e}"

        # Устанавливаем провайдера через ConfigManager
        config_manager = get_config_manager()

        # Формируем ключ конфигурации
        config_key = f"providers.{provider_type}"

        # Устанавливаем провайдера
        config_manager.set_config(config_key, provider_name, vault_name=vault_name)

        # Если указана модель, устанавливаем её (используем resolved_model для полного ID)
        if resolved_model:
            model_key = f"providers.{provider_type}_model"
            config_manager.set_config(model_key, resolved_model, vault_name=vault_name)

        # Формируем ответ
        scope = f"vault '{vault_name}'" if vault_name else "глобально"
        lines = ["## Провайдер установлен\n"]
        lines.append(f"- **Тип:** {provider_type}")
        lines.append(f"- **Провайдер:** {provider_name}")
        lines.append(f"- **Область:** {scope}")

        # Информация о модели
        if resolved_model and provider_name == "yandex" and provider_type == "chat":
            model_info = get_yandex_model(resolved_model)
            if model_info:
                lines.append(f"- **Модель:** {model_info.name} (`{model_info.id}`)")
                lines.append(f"- **Контекст:** {model_info.context_size:,} токенов".replace(",", " "))
                lines.append(f"- **API:** {'gRPC SDK' if model_info.api_type == 'grpc' else 'OpenAI HTTP'}")
            else:
                lines.append(f"- **Модель:** {resolved_model}")
        elif resolved_model:
            lines.append(f"- **Модель:** {resolved_model}")
        else:
            lines.append("- **Модель:** default для провайдера")

        if warning:
            lines.append(f"\n{warning}")

        lines.append("\n✅ Конфигурация обновлена.")
        
        return "\n".join(lines)
    
    except ValueError as e:
        return f"❌ Ошибка валидации: {e}"
    except Exception as e:
        logger.error(f"Error in set_provider: {e}", exc_info=True)
        return f"❌ Ошибка установки провайдера: {e}"


async def test_provider(
    provider_name: str,
    test_text: str = "Тестовое сообщение для проверки провайдера",
) -> str:
    """Тестирование провайдера.

    Args:
        provider_name: Имя провайдера (ollama | yandex)
        test_text: Текст для теста
    
    Returns:
        Результаты тестирования:
        - Embedding: размерность, latency
        - Chat: ответ модели, latency
        - Ошибки если есть
    """
    try:
        if provider_name.lower() not in SUPPORTED_PROVIDERS:
            return f"❌ Неподдерживаемый провайдер: {provider_name}. Допустимые: {', '.join(SUPPORTED_PROVIDERS)}"
        
        provider_name = provider_name.lower()
        lines = [f"## Тестирование провайдера: {provider_name}\n"]
        lines.append(f"**Тестовый текст:** `{test_text[:50]}...`\n")
        
        # Тестируем embedding провайдер
        lines.append("### Embedding Provider\n")
        try:
            embedding_provider = ProviderFactory.get_embedding_provider(provider_name=provider_name)
            health = await embedding_provider.health_check()
            
            if not health.available:
                lines.append(f"❌ **Недоступен:** {health.error or 'Unknown error'}")
            else:
                # Выполняем тестовый запрос
                start_time = time.time()
                embedding = await embedding_provider.get_embedding(test_text)
                latency_ms = (time.time() - start_time) * 1000
                
                lines.append(f"✅ **Статус:** Доступен")
                lines.append(f"- **Модель:** {embedding_provider.model}")
                lines.append(f"- **Размерность:** {len(embedding)}")
                lines.append(f"- **Latency:** {latency_ms:.1f} ms")
                if health.dimensions:
                    lines.append(f"- **Ожидаемая размерность:** {health.dimensions}")
        except Exception as e:
            lines.append(f"❌ **Ошибка:** {e}")
            logger.debug(f"Error testing embedding provider: {e}", exc_info=True)
        
        lines.append("")
        
        # Тестируем chat провайдер
        lines.append("### Chat Provider\n")
        try:
            chat_provider = ProviderFactory.get_chat_provider(provider_name=provider_name)
            health = await chat_provider.health_check()
            
            if not health.available:
                lines.append(f"❌ **Недоступен:** {health.error or 'Unknown error'}")
            else:
                # Выполняем тестовый запрос
                start_time = time.time()
                response = await chat_provider.complete(
                    messages=[{"role": "user", "content": test_text}],
                    temperature=0.7,
                    max_tokens=50,
                )
                latency_ms = (time.time() - start_time) * 1000
                
                lines.append(f"✅ **Статус:** Доступен")
                lines.append(f"- **Модель:** {chat_provider.model}")
                lines.append(f"- **Latency:** {latency_ms:.1f} ms")
                lines.append(f"- **Ответ:** {response[:100]}...")
        except Exception as e:
            lines.append(f"❌ **Ошибка:** {e}")
            logger.debug(f"Error testing chat provider: {e}", exc_info=True)
        
        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Error in test_provider: {e}", exc_info=True)
        return f"❌ Ошибка тестирования провайдера: {e}"


async def list_yandex_models() -> str:
    """Список доступных chat моделей Yandex Cloud.

    Returns:
        Markdown таблица с моделями:
        - Название модели
        - ID для API
        - Размер контекста
        - Тип API (gRPC SDK / OpenAI HTTP)

    Модели разделены на две группы:
    - YandexGPT (нативные модели Yandex, gRPC SDK)
    - Open Source (Qwen, Gemma, gpt-oss, OpenAI-compatible HTTP API)

    Для установки модели используйте:
        set_provider(provider_type="chat", provider_name="yandex", model="<model_id>")
    """
    from obsidian_kb.providers.yandex.models import (
        YANDEX_MODEL_ALIASES,
        list_yandex_models as get_models_list,
    )

    lines = ["## Доступные chat модели Yandex Cloud\n"]

    # Таблица моделей
    lines.append("### Модели\n")
    lines.append("| Модель | ID | Контекст | API |")
    lines.append("|--------|-----|----------|-----|")

    for model in get_models_list():
        context_str = f"{model.context_size:,}".replace(",", " ")
        api_str = "gRPC SDK" if model.api_type == "grpc" else "OpenAI HTTP"
        lines.append(f"| {model.name} | `{model.id}` | {context_str} | {api_str} |")

    # Алиасы
    lines.append("\n### Алиасы (короткие имена)\n")
    lines.append("Для удобства можно использовать короткие имена:\n")

    # Группируем алиасы по целевой модели
    alias_groups: dict[str, list[str]] = {}
    for alias, target in YANDEX_MODEL_ALIASES.items():
        if target not in alias_groups:
            alias_groups[target] = []
        alias_groups[target].append(alias)

    for target, aliases in sorted(alias_groups.items()):
        aliases_str = ", ".join(f"`{a}`" for a in sorted(aliases))
        lines.append(f"- {aliases_str} → `{target}`")

    # Примеры использования
    lines.append("\n### Примеры использования\n")
    lines.append("```")
    lines.append('set_provider(provider_type="chat", provider_name="yandex", model="qwen3-235b-a22b-fp8/latest")')
    lines.append('set_provider(provider_type="chat", provider_name="yandex", model="qwen")  # алиас')
    lines.append('set_provider(provider_type="chat", provider_name="yandex", model="yandexgpt/rc")')
    lines.append("```")

    return "\n".join(lines)


async def provider_health() -> str:
    """Проверка здоровья всех провайдеров.
    
    Returns:
        Статус каждого провайдера:
        - ✅ Available
        - ⚠️ Degraded (высокий latency)
        - ❌ Unavailable
    """
    try:
        lines = ["## Проверка здоровья провайдеров\n"]
        
        # Пороги для определения статуса
        LATENCY_THRESHOLD_MS = 5000  # 5 секунд = degraded
        LATENCY_ERROR_MS = 30000  # 30 секунд = error
        
        provider_health_info = []
        
        for provider_name in SUPPORTED_PROVIDERS:
            # Проверяем embedding провайдер
            embedding_status = "unavailable"
            embedding_latency = None
            embedding_error = None
            
            try:
                provider = ProviderFactory.get_embedding_provider(provider_name=provider_name)
                health = await provider.health_check()
                
                if health.available:
                    embedding_latency = health.latency_ms
                    if embedding_latency is None:
                        # Выполняем тестовый запрос для измерения latency
                        start_time = time.time()
                        await provider.get_embedding("test")
                        embedding_latency = (time.time() - start_time) * 1000
                    
                    if embedding_latency > LATENCY_ERROR_MS:
                        embedding_status = "error"
                    elif embedding_latency > LATENCY_THRESHOLD_MS:
                        embedding_status = "degraded"
                    else:
                        embedding_status = "available"
                else:
                    embedding_error = health.error
            except Exception as e:
                embedding_error = str(e)
            
            # Проверяем chat провайдер
            chat_status = "unavailable"
            chat_latency = None
            chat_error = None
            
            try:
                provider = ProviderFactory.get_chat_provider(provider_name=provider_name)
                health = await provider.health_check()
                
                if health.available:
                    chat_latency = health.latency_ms
                    if chat_latency is None:
                        # Выполняем тестовый запрос для измерения latency
                        start_time = time.time()
                        await provider.complete(
                            messages=[{"role": "user", "content": "test"}],
                            max_tokens=10,
                        )
                        chat_latency = (time.time() - start_time) * 1000
                    
                    if chat_latency > LATENCY_ERROR_MS:
                        chat_status = "error"
                    elif chat_latency > LATENCY_THRESHOLD_MS:
                        chat_status = "degraded"
                    else:
                        chat_status = "available"
                else:
                    chat_error = health.error
            except Exception as e:
                chat_error = str(e)
            
            provider_health_info.append({
                "name": provider_name,
                "embedding_status": embedding_status,
                "embedding_latency": embedding_latency,
                "embedding_error": embedding_error,
                "chat_status": chat_status,
                "chat_latency": chat_latency,
                "chat_error": chat_error,
            })
        
        # Формируем таблицу
        lines.append("| Провайдер | Embedding | Latency | Chat | Latency |")
        lines.append("|-----------|-----------|---------|------|---------|")
        
        for info in provider_health_info:
            # Статус embedding
            embedding_emoji = {
                "available": "✅",
                "degraded": "⚠️",
                "error": "❌",
                "unavailable": "❌",
            }.get(info["embedding_status"], "❓")
            
            embedding_status_str = f"{embedding_emoji} {info['embedding_status']}"
            if info["embedding_error"]:
                embedding_status_str += f" ({info['embedding_error'][:30]}...)"
            
            embedding_latency_str = (
                f"{info['embedding_latency']:.0f}ms" if info["embedding_latency"] is not None else "—"
            )
            
            # Статус chat
            chat_emoji = {
                "available": "✅",
                "degraded": "⚠️",
                "error": "❌",
                "unavailable": "❌",
            }.get(info["chat_status"], "❓")
            
            chat_status_str = f"{chat_emoji} {info['chat_status']}"
            if info["chat_error"]:
                chat_status_str += f" ({info['chat_error'][:30]}...)"
            
            chat_latency_str = (
                f"{info['chat_latency']:.0f}ms" if info["chat_latency"] is not None else "—"
            )
            
            lines.append(
                f"| {info['name']} | {embedding_status_str} | {embedding_latency_str} | "
                f"{chat_status_str} | {chat_latency_str} |"
            )
        
        lines.append("")
        lines.append("### Легенда")
        lines.append("- ✅ **available**: Провайдер доступен и работает нормально")
        lines.append("- ⚠️ **degraded**: Провайдер доступен, но latency высокая (>5s)")
        lines.append("- ❌ **error/unavailable**: Провайдер недоступен или ошибка")
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.error(f"Error in provider_health: {e}", exc_info=True)
        return f"❌ Ошибка проверки здоровья провайдеров: {e}"


async def estimate_cost(
    vault_name: str,
    operation: str = "reindex",  # reindex | index_new | enrich
    enrichment: str = "contextual",
) -> str:
    """Оценка стоимости операции.
    
    Args:
        vault_name: Имя vault'а
        operation: Тип операции (reindex | index_new | enrich)
        enrichment: Уровень обогащения (none | contextual | full)
    
    Returns:
        Оценка стоимости:
        - По текущему провайдеру
        - Сравнение с альтернативами
        - Разбивка (embedding / chat completion)
    """
    try:
        # Получаем конфигурацию vault'а
        config_manager = get_config_manager()
        config = config_manager.get_config(vault_name)
        
        # Получаем статистику vault'а
        try:
            stats = await services.db_manager.get_vault_stats(vault_name)
            total_chunks = stats.chunk_count
            total_documents = stats.file_count
        except Exception:
            # Если статистика недоступна, используем оценки
            total_chunks = 1000  # Примерная оценка
            total_documents = 100
        
        # Определяем количество операций в зависимости от типа операции
        if operation == "reindex":
            # Полная переиндексация - все документы и чанки
            embedding_ops = total_chunks
            # Для enrichment нужно оценить количество запросов
            if enrichment == "none":
                chat_ops = 0
            elif enrichment == "contextual":
                # Context prefix для каждого чанка
                chat_ops = total_chunks
            elif enrichment == "full":
                # Context prefix + summary для каждого документа
                chat_ops = total_chunks + total_documents
            else:
                chat_ops = total_chunks
        elif operation == "index_new":
            # Индексация новых файлов - оцениваем 10% от общего количества
            embedding_ops = int(total_chunks * 0.1)
            if enrichment == "none":
                chat_ops = 0
            elif enrichment == "contextual":
                chat_ops = embedding_ops
            elif enrichment == "full":
                chat_ops = embedding_ops + int(total_documents * 0.1)
            else:
                chat_ops = embedding_ops
        elif operation == "enrich":
            # Только обогащение существующих чанков
            embedding_ops = 0
            if enrichment == "none":
                chat_ops = 0
            elif enrichment == "contextual":
                chat_ops = total_chunks
            elif enrichment == "full":
                chat_ops = total_chunks + total_documents
            else:
                chat_ops = total_chunks
        else:
            return f"❌ Неизвестный тип операции: {operation}. Допустимые: reindex, index_new, enrich"
        
        # Получаем текущие провайдеры
        current_embedding_provider = config.providers.embedding
        current_chat_provider = config.providers.chat
        
        # Оцениваем стоимость для текущих провайдеров
        embedding_cost_per_1m = PROVIDER_COSTS.get(current_embedding_provider, {}).get("embedding", 0.0)
        chat_cost_per_1m = PROVIDER_COSTS.get(current_chat_provider, {}).get("chat", 0.0)
        
        # Оценка токенов (примерная)
        # Embedding: ~100 токенов на чанк
        # Chat completion: ~200 токенов на запрос (context prefix) или ~500 токенов (summary)
        embedding_tokens = embedding_ops * 100
        if enrichment == "contextual":
            chat_tokens = chat_ops * 200
        elif enrichment == "full":
            # Context prefix + summary
            contextual_tokens = total_chunks * 200
            summary_tokens = total_documents * 500
            chat_tokens = contextual_tokens + summary_tokens
        else:
            chat_tokens = 0
        
        # Стоимость в долларах
        embedding_cost = (embedding_tokens / 1_000_000) * embedding_cost_per_1m
        chat_cost = (chat_tokens / 1_000_000) * chat_cost_per_1m
        total_cost = embedding_cost + chat_cost
        
        lines = [f"## Оценка стоимости операции\n"]
        lines.append(f"- **Vault:** {vault_name}")
        lines.append(f"- **Операция:** {operation}")
        lines.append(f"- **Обогащение:** {enrichment}")
        lines.append(f"- **Документов:** {total_documents}")
        lines.append(f"- **Чанков:** {total_chunks}\n")
        
        lines.append("### Текущие провайдеры\n")
        lines.append(f"- **Embedding:** {current_embedding_provider} (${embedding_cost_per_1m:.2f}/1M tokens)")
        lines.append(f"- **Chat:** {current_chat_provider} (${chat_cost_per_1m:.2f}/1M tokens)\n")
        
        lines.append("### Оценка стоимости\n")
        lines.append("| Компонент | Операций | Токенов | Стоимость |")
        lines.append("|-----------|----------|---------|-----------|")
        
        if embedding_ops > 0:
            lines.append(
                f"| Embedding | {embedding_ops:,} | {embedding_tokens:,} | ${embedding_cost:.4f} |"
            )
        
        if chat_ops > 0:
            lines.append(
                f"| Chat Completion | {chat_ops:,} | {chat_tokens:,} | ${chat_cost:.4f} |"
            )
        
        lines.append(f"| **Итого** | — | — | **${total_cost:.4f}** |")
        lines.append("")
        
        # Сравнение с альтернативами
        lines.append("### Сравнение с альтернативными провайдерами\n")
        lines.append("| Провайдер | Embedding | Chat | Итого |")
        lines.append("|-----------|-----------|------|-------|")
        
        for alt_provider in SUPPORTED_PROVIDERS:
            alt_embedding_cost_per_1m = PROVIDER_COSTS.get(alt_provider, {}).get("embedding", 0.0)
            alt_chat_cost_per_1m = PROVIDER_COSTS.get(alt_provider, {}).get("chat", 0.0)
            
            alt_embedding_cost = (embedding_tokens / 1_000_000) * alt_embedding_cost_per_1m
            alt_chat_cost = (chat_tokens / 1_000_000) * alt_chat_cost_per_1m
            alt_total_cost = alt_embedding_cost + alt_chat_cost
            
            marker = " ← текущий" if alt_provider == current_embedding_provider else ""
            
            lines.append(
                f"| {alt_provider}{marker} | ${alt_embedding_cost:.4f} | ${alt_chat_cost:.4f} | ${alt_total_cost:.4f} |"
            )
        
        lines.append("")
        lines.append("> **Примечание:** Оценка основана на приблизительных значениях токенов.")
        lines.append("> Реальная стоимость может отличаться в зависимости от размера документов.")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"❌ Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in estimate_cost: {e}", exc_info=True)
        return f"❌ Ошибка оценки стоимости: {e}"

