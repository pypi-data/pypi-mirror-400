"""Тесты для embedding_service.py."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from obsidian_kb.embedding_service import EmbeddingService
from obsidian_kb.providers.exceptions import ProviderConnectionError


# Используем фикстуру embedding_service из conftest.py
# Она автоматически закрывает сессию после теста


@pytest.mark.asyncio
async def test_get_embedding_success(embedding_service):
    """Тест успешного получения embedding."""
    mock_embedding = [0.1] * 768

    with patch.object(embedding_service, "_request_with_retry", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"embedding": mock_embedding}

        result = await embedding_service.get_embedding("test text")

        assert result == mock_embedding
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "http://localhost:11434/api/embeddings"
        assert call_args[0][1]["model"] == "nomic-embed-text"
        assert call_args[0][1]["prompt"] == "test text"


@pytest.mark.asyncio
async def test_get_embedding_empty_text(embedding_service):
    """Тест получения embedding для пустого текста."""
    with pytest.raises(ValueError, match="cannot be empty"):
        await embedding_service.get_embedding("")


@pytest.mark.asyncio
async def test_get_embedding_whitespace_only(embedding_service):
    """Тест получения embedding для текста только с пробелами."""
    with pytest.raises(ValueError, match="cannot be empty"):
        await embedding_service.get_embedding("   ")


@pytest.mark.asyncio
async def test_get_embedding_empty_response(embedding_service):
    """Тест обработки пустого ответа от Ollama."""
    with patch.object(embedding_service, "_request_with_retry", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"embedding": []}

        with pytest.raises(ProviderConnectionError, match="Empty embedding"):
            await embedding_service.get_embedding("test text")


@pytest.mark.asyncio
async def test_get_embedding_connection_error(embedding_service):
    """Тест обработки ошибки соединения."""
    with patch.object(embedding_service, "_request_with_retry", new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = ProviderConnectionError("Connection failed")

        with pytest.raises(ProviderConnectionError, match="Connection failed"):
            await embedding_service.get_embedding("test text")


@pytest.mark.asyncio
async def test_get_embeddings_batch_success(embedding_service):
    """Тест успешного получения батча embeddings."""
    texts = ["text1", "text2", "text3"]
    mock_embeddings = [[0.1] * 768, [0.2] * 768, [0.3] * 768]

    with patch.object(embedding_service, "get_embedding", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = mock_embeddings

        result = await embedding_service.get_embeddings_batch(texts)

        assert len(result) == 3
        assert result == mock_embeddings
        assert mock_get.call_count == 3


@pytest.mark.asyncio
async def test_get_embeddings_batch_empty_list(embedding_service):
    """Тест получения embeddings для пустого списка."""
    result = await embedding_service.get_embeddings_batch([])
    assert result == []


@pytest.mark.asyncio
async def test_get_embeddings_batch_with_empty_texts(embedding_service):
    """Тест получения embeddings для списка с пустыми текстами."""
    texts = ["text1", "", "   ", "text2"]
    mock_embeddings = [[0.1] * 768, [0.2] * 768]

    with patch.object(embedding_service, "get_embedding", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = mock_embeddings

        result = await embedding_service.get_embeddings_batch(texts)

        assert len(result) == 4
        # Первый и последний должны быть реальными embeddings
        assert result[0] == mock_embeddings[0]
        assert result[3] == mock_embeddings[1]
        # Пустые тексты должны дать нулевые векторы
        assert result[1] == [0.0] * 768
        assert result[2] == [0.0] * 768


@pytest.mark.asyncio
async def test_get_embeddings_batch_all_empty(embedding_service):
    """Тест получения embeddings для списка только с пустыми текстами."""
    with pytest.raises(ValueError, match="All texts are empty"):
        await embedding_service.get_embeddings_batch(["", "   ", "\t"])


@pytest.mark.asyncio
async def test_get_embeddings_batch_with_errors(embedding_service):
    """Тест обработки ошибок при получении embeddings."""
    texts = ["text1", "text2"]
    mock_embedding = [0.1] * 768

    with patch.object(embedding_service, "get_embedding", new_callable=AsyncMock) as mock_get:
        # Первый успешен, второй с ошибкой
        mock_get.side_effect = [mock_embedding, ProviderConnectionError("Error")]

        result = await embedding_service.get_embeddings_batch(texts)

        assert len(result) == 2
        assert result[0] == mock_embedding
        # При ошибке должен быть нулевой вектор
        assert result[1] == [0.0] * 768


@pytest.mark.asyncio
async def test_get_embeddings_batch_large_batch(embedding_service):
    """Тест обработки большого батча (больше batch_size)."""
    # Создаём список из 15 текстов (batch_size по умолчанию 10)
    texts = [f"text{i}" for i in range(15)]
    mock_embeddings = [[0.1] * 768] * 15

    with patch.object(embedding_service, "get_embedding", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = mock_embeddings

        result = await embedding_service.get_embeddings_batch(texts)

        assert len(result) == 15
        assert mock_get.call_count == 15


@pytest.mark.asyncio
async def test_health_check_success(embedding_service):
    """Тест успешной проверки здоровья."""
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "models": [
                {"name": "nomic-embed-text"},
                {"name": "other-model"},
            ]
        }
    )

    # Правильный мок для async context manager
    mock_get = AsyncMock()
    mock_get.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get.__aexit__ = AsyncMock(return_value=None)

    mock_session_obj = AsyncMock()
    mock_session_obj.get = MagicMock(return_value=mock_get)

    with patch.object(embedding_service, "_get_session", new_callable=AsyncMock) as mock_session:
        mock_session.return_value = mock_session_obj

        result = await embedding_service.health_check()

        assert result is True


@pytest.mark.asyncio
async def test_health_check_model_not_found(embedding_service):
    """Тест проверки здоровья когда модель не найдена.

    health_check создаёт собственную aiohttp.ClientSession,
    поэтому патчим aiohttp.ClientSession напрямую.
    """
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "models": [
                {"name": "other-model"},
            ]
        }
    )

    mock_get = AsyncMock()
    mock_get.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get.__aexit__ = AsyncMock(return_value=None)

    mock_session_obj = MagicMock()
    mock_session_obj.get = MagicMock(return_value=mock_get)
    mock_session_obj.__aenter__ = AsyncMock(return_value=mock_session_obj)
    mock_session_obj.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session_obj):
        result = await embedding_service.health_check()

        assert result is False


@pytest.mark.asyncio
async def test_health_check_timeout(embedding_service):
    """Тест проверки здоровья при таймауте."""
    from unittest.mock import patch

    mock_session_obj = AsyncMock()
    mock_session_obj.get = AsyncMock(side_effect=asyncio.TimeoutError())
    mock_session_obj.__aenter__ = AsyncMock(return_value=mock_session_obj)
    mock_session_obj.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session_obj):
        result = await embedding_service.health_check()

        assert result is False


@pytest.mark.asyncio
async def test_health_check_connection_error(embedding_service):
    """Тест проверки здоровья при ошибке соединения."""
    from unittest.mock import patch

    mock_session_obj = AsyncMock()
    mock_session_obj.get = AsyncMock(side_effect=aiohttp.ClientError())
    mock_session_obj.__aenter__ = AsyncMock(return_value=mock_session_obj)
    mock_session_obj.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session_obj):
        result = await embedding_service.health_check()

        assert result is False


@pytest.mark.asyncio
async def test_request_with_retry_success(embedding_service):
    """Тест успешного запроса с retry."""
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"embedding": [0.1] * 768})
    mock_response.text = AsyncMock(return_value="")

    mock_post = AsyncMock()
    mock_post.__aenter__ = AsyncMock(return_value=mock_response)
    mock_post.__aexit__ = AsyncMock(return_value=None)

    mock_session_obj = AsyncMock()
    mock_session_obj.post = MagicMock(return_value=mock_post)

    with patch.object(embedding_service, "_get_session", new_callable=AsyncMock) as mock_session:
        mock_session.return_value = mock_session_obj

        result = await embedding_service._request_with_retry(
            "http://localhost:11434/api/embeddings",
            {"model": "test", "prompt": "test"},
        )

        assert result == {"embedding": [0.1] * 768}


@pytest.mark.asyncio
async def test_request_with_retry_timeout(embedding_service):
    """Тест retry при таймауте."""
    from unittest.mock import MagicMock

    # Первые две попытки с таймаутом, третья успешна
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"embedding": [0.1] * 768})
    mock_response.text = AsyncMock(return_value="")

    mock_post_success = AsyncMock()
    mock_post_success.__aenter__ = AsyncMock(return_value=mock_response)
    mock_post_success.__aexit__ = AsyncMock(return_value=None)

    mock_session_obj = AsyncMock()
    mock_session_obj.post = MagicMock(
        side_effect=[
            asyncio.TimeoutError(),
            asyncio.TimeoutError(),
            mock_post_success,
        ]
    )

    with patch.object(embedding_service, "_get_session", new_callable=AsyncMock) as mock_session:
        mock_session.return_value = mock_session_obj

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await embedding_service._request_with_retry(
                "http://localhost:11434/api/embeddings",
                {"model": "test", "prompt": "test"},
                max_retries=3,
            )

            assert result == {"embedding": [0.1] * 768}


@pytest.mark.asyncio
async def test_request_with_retry_max_retries_exceeded(embedding_service):
    """Тест превышения максимального количества попыток."""
    from unittest.mock import MagicMock

    # Создаём мок, который выбрасывает TimeoutError при входе в контекстный менеджер
    mock_post = AsyncMock()
    mock_post.__aenter__ = AsyncMock(side_effect=asyncio.TimeoutError())
    mock_post.__aexit__ = AsyncMock(return_value=None)

    mock_session_obj = AsyncMock()
    mock_session_obj.post = MagicMock(return_value=mock_post)

    with patch.object(embedding_service, "_get_session", new_callable=AsyncMock) as mock_session:
        mock_session.return_value = mock_session_obj

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(ProviderConnectionError, match="timeout after all retries"):
                await embedding_service._request_with_retry(
                    "http://localhost:11434/api/embeddings",
                    {"model": "test", "prompt": "test"},
                    max_retries=2,
                )


@pytest.mark.asyncio
async def test_request_with_retry_404_error(embedding_service):
    """Тест обработки 404 ошибки (модель не найдена)."""
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.text = AsyncMock(return_value="Model not found")

    mock_post = AsyncMock()
    mock_post.__aenter__ = AsyncMock(return_value=mock_response)
    mock_post.__aexit__ = AsyncMock(return_value=None)

    mock_session_obj = AsyncMock()
    mock_session_obj.post = MagicMock(return_value=mock_post)

    with patch.object(embedding_service, "_get_session", new_callable=AsyncMock) as mock_session:
        mock_session.return_value = mock_session_obj

        with pytest.raises(ProviderConnectionError, match="Model not found"):
            await embedding_service._request_with_retry(
                "http://localhost:11434/api/embeddings",
                {"model": "test", "prompt": "test"},
            )


@pytest.mark.asyncio
async def test_close_session(embedding_service):
    """Тест закрытия сессии."""
    mock_session = AsyncMock()
    mock_session.closed = False
    embedding_service._session = mock_session

    await embedding_service.close()

    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_close_session_already_closed(embedding_service: EmbeddingService):
    """Тест закрытия уже закрытой сессии."""
    mock_session = AsyncMock()
    mock_session.closed = True
    embedding_service._session = mock_session

    await embedding_service.close()

    mock_session.close.assert_not_called()


@pytest.mark.asyncio
async def test_close_no_session(embedding_service: EmbeddingService):
    """Тест закрытия когда сессии нет."""
    embedding_service._session = None

    # Не должно быть ошибки
    await embedding_service.close()


@pytest.mark.asyncio
async def test_get_embedding_long_text(embedding_service):
    """Тест получения embedding для длинного текста (до 6000 символов для nomic-embed-text)."""
    # Создаем текст длиной 6000 символов
    long_text = "A" * 6000
    mock_embedding = [0.1] * 768

    with patch.object(embedding_service, "_request_with_retry", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"embedding": mock_embedding}

        result = await embedding_service.get_embedding(long_text)

        assert result == mock_embedding
        assert len(result) == 768
        # Проверяем, что текст не был обрезан (6000 символов в пределах лимита)
        call_args = mock_request.call_args
        assert len(call_args[0][1]["prompt"]) == 6000


@pytest.mark.asyncio
async def test_get_embedding_very_long_text_truncated(embedding_service):
    """Тест обрезки очень длинного текста (более 6000 символов)."""
    # Создаем текст длиной 7000 символов (должен быть обрезан до 6000)
    very_long_text = "B" * 7000
    mock_embedding = [0.1] * 768

    with patch.object(embedding_service, "_request_with_retry", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"embedding": mock_embedding}

        result = await embedding_service.get_embedding(very_long_text)

        assert result == mock_embedding
        assert len(result) == 768
        # Проверяем, что текст был обрезан до 6000 символов
        call_args = mock_request.call_args
        assert len(call_args[0][1]["prompt"]) == 6000

