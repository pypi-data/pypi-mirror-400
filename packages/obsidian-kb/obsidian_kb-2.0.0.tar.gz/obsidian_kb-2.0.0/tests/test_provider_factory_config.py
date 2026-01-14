"""Тесты для ProviderFactory с интеграцией ConfigManager.

Проверяем, что модели правильно читаются из ConfigManager.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from obsidian_kb.config.manager import ConfigManager, reset_config_manager
from obsidian_kb.config.schema import ProviderConfig, VaultConfig
from obsidian_kb.providers.factory import ProviderFactory


class TestProviderFactoryWithConfigManager:
    """Тесты для ProviderFactory с использованием ConfigManager."""

    @pytest.fixture
    def temp_config_dir(self):
        """Создание временной директории для конфигурации."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def config_manager_with_custom_model(self, temp_config_dir):
        """ConfigManager с кастомной моделью для chat."""
        manager = ConfigManager(base_path=temp_config_dir)
        # Устанавливаем кастомную модель
        manager.set_config("providers.chat_model", "qwen3-235b-a22b-fp8/latest")
        manager.set_config("providers.chat", "yandex")
        return manager

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Сбрасываем singleton перед каждым тестом."""
        reset_config_manager()
        yield
        reset_config_manager()

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_get_chat_provider_uses_config_manager_model(
        self, mock_sdk, config_manager_with_custom_model, temp_config_dir
    ):
        """Проверяем, что get_chat_provider использует модель из ConfigManager."""
        # Мокаем get_config_manager чтобы он возвращал наш ConfigManager
        with patch(
            "obsidian_kb.providers.factory.get_config_manager",
            return_value=config_manager_with_custom_model,
        ), patch.object(
            ProviderFactory,
            "get_chat_provider",
            wraps=ProviderFactory.get_chat_provider,
        ):
            # Мокаем Yandex credentials
            with patch(
                "obsidian_kb.providers.factory.settings"
            ) as mock_settings:
                mock_settings.yandex_folder_id = "test_folder"
                mock_settings.yandex_api_key = "test_key"
                mock_settings.yandex_chat_model = "default-model"  # Дефолт в settings
                mock_settings.yandex_instance_id = None

                provider = ProviderFactory.get_chat_provider(provider_name="yandex")

                # Должна использоваться модель из ConfigManager, а не из settings
                assert provider.model == "qwen3-235b-a22b-fp8/latest"

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_get_chat_provider_explicit_model_overrides_config(
        self, mock_sdk, config_manager_with_custom_model, temp_config_dir
    ):
        """Проверяем, что явно указанная модель перезаписывает модель из ConfigManager."""
        with patch(
            "obsidian_kb.providers.factory.get_config_manager",
            return_value=config_manager_with_custom_model,
        ), patch(
            "obsidian_kb.providers.factory.settings"
        ) as mock_settings:
            mock_settings.yandex_folder_id = "test_folder"
            mock_settings.yandex_api_key = "test_key"
            mock_settings.yandex_instance_id = None

            # Явно указываем модель
            provider = ProviderFactory.get_chat_provider(
                provider_name="yandex",
                model="explicit-model/latest",
            )

            # Должна использоваться явно указанная модель
            assert provider.model == "explicit-model/latest"

    @patch("obsidian_kb.providers.yandex.chat_provider.AsyncYCloudML")
    def test_get_chat_provider_falls_back_to_settings(
        self, mock_sdk, temp_config_dir
    ):
        """Проверяем fallback на settings, если модель не указана в ConfigManager."""
        # ConfigManager без кастомной модели
        empty_manager = ConfigManager(base_path=temp_config_dir)

        with patch(
            "obsidian_kb.providers.factory.get_config_manager",
            return_value=empty_manager,
        ), patch(
            "obsidian_kb.providers.factory.settings"
        ) as mock_settings:
            mock_settings.yandex_folder_id = "test_folder"
            mock_settings.yandex_api_key = "test_key"
            mock_settings.yandex_chat_model = "settings-default-model"
            mock_settings.yandex_instance_id = None

            provider = ProviderFactory.get_chat_provider(provider_name="yandex")

            # Должна использоваться модель из settings
            assert provider.model == "settings-default-model"


class TestConfigManagerModelPersistence:
    """Тесты для сохранения/загрузки модели через ConfigManager."""

    @pytest.fixture
    def temp_config_dir(self):
        """Создание временной директории для конфигурации."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_set_and_get_chat_model(self, temp_config_dir):
        """Проверяем, что модель сохраняется и читается правильно."""
        manager = ConfigManager(base_path=temp_config_dir)

        # Устанавливаем модель
        manager.set_config("providers.chat_model", "qwen3-235b-a22b-fp8/latest")

        # Читаем обратно
        config = manager.get_config()
        assert config.providers.chat_model == "qwen3-235b-a22b-fp8/latest"

    def test_model_persists_after_reload(self, temp_config_dir):
        """Проверяем, что модель сохраняется на диск и читается после перезагрузки."""
        # Первый manager устанавливает модель
        manager1 = ConfigManager(base_path=temp_config_dir)
        manager1.set_config("providers.chat_model", "qwen3-235b-a22b-fp8/latest")

        # Второй manager читает с диска
        manager2 = ConfigManager(base_path=temp_config_dir)
        config = manager2.get_config()
        assert config.providers.chat_model == "qwen3-235b-a22b-fp8/latest"

    def test_vault_specific_model(self, temp_config_dir):
        """Проверяем vault-specific модель."""
        manager = ConfigManager(base_path=temp_config_dir)

        # Глобальная модель
        manager.set_config("providers.chat_model", "global-model")

        # Vault-specific модель
        manager.set_config(
            "providers.chat_model", "vault-specific-model", vault_name="test-vault"
        )

        # Глобальная конфигурация
        global_config = manager.get_config()
        assert global_config.providers.chat_model == "global-model"

        # Vault-specific конфигурация (должна перезаписать global)
        vault_config = manager.get_config(vault_name="test-vault")
        assert vault_config.providers.chat_model == "vault-specific-model"
