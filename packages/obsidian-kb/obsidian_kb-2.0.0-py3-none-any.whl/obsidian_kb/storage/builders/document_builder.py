"""DocumentRecordBuilder — построение записей для таблиц documents и properties."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from obsidian_kb.core.data_normalizer import DataNormalizer
from obsidian_kb.types import DocumentChunk

logger = logging.getLogger(__name__)


class DocumentRecordBuilder:
    """Построение записей для таблиц documents и document_properties.

    Отвечает за создание корректных записей для хранения информации
    о документах в базе данных LanceDB.
    """

    def __init__(self, normalizer: DataNormalizer | None = None) -> None:
        """Инициализация builder'а.

        Args:
            normalizer: DataNormalizer для нормализации данных (опционально)
        """
        self._normalizer = normalizer or DataNormalizer()

    def build_record(
        self,
        chunk: DocumentChunk,
        vault_name: str,
        content_hash: str | None = None,
    ) -> dict[str, Any]:
        """Построение записи для таблицы documents.

        Args:
            chunk: Чанк документа (используется для получения метаданных файла)
            vault_name: Имя vault'а
            content_hash: SHA256 хеш содержимого файла (опционально)

        Returns:
            Словарь с данными для записи в таблицу documents
        """
        document_id = f"{vault_name}::{chunk.file_path}"

        # Вычисляем content_hash если не указан
        if content_hash is None:
            content_hash = self._compute_file_content_hash(chunk.file_path)

        return {
            "document_id": document_id,
            "vault_name": vault_name,
            "file_path": chunk.file_path,
            "file_path_full": str(self._get_full_path(chunk.file_path)),
            "file_name": Path(chunk.file_path).name,
            "file_extension": Path(chunk.file_path).suffix,
            "content_type": self._detect_content_type(chunk.file_path),
            "title": chunk.title,
            "created_at": chunk.created_at.isoformat() if chunk.created_at else "",
            "modified_at": chunk.modified_at.isoformat(),
            "file_size": self._get_file_size(chunk.file_path),
            "chunk_count": 0,  # Будет обновлено после подсчета чанков
            "content_hash": content_hash,
        }

    def build_properties_records(
        self,
        chunk: DocumentChunk,
        vault_name: str,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Построение записей для таблицы document_properties.

        Args:
            chunk: Чанк документа
            vault_name: Имя vault'а
            document_id: ID документа (опционально, вычислится автоматически)

        Returns:
            Список словарей с данными для записи в таблицу document_properties
        """
        if document_id is None:
            document_id = f"{vault_name}::{chunk.file_path}"

        properties: list[dict[str, Any]] = []
        if isinstance(chunk.metadata, dict):
            for key, value in chunk.metadata.items():
                # Пропускаем теги (они в metadata.frontmatter_tags)
                if key == "tags":
                    continue

                # Нормализация значения
                normalized_value = self._normalizer.normalize_property_value(value)
                property_id = f"{document_id}::{key}"

                properties.append(
                    {
                        "property_id": property_id,
                        "document_id": document_id,
                        "vault_name": vault_name,
                        "property_key": key,
                        "property_value": normalized_value,
                        "property_value_raw": str(value),
                        "property_type": self._normalizer.get_property_type(value),
                    }
                )
        return properties

    def build_metadata_record(
        self,
        chunk: DocumentChunk,
        vault_name: str,
    ) -> dict[str, Any]:
        """Построение записи для таблицы metadata.

        Args:
            chunk: Чанк документа
            vault_name: Имя vault'а

        Returns:
            Словарь с данными для записи в таблицу metadata
        """
        document_id = f"{vault_name}::{chunk.file_path}"
        metadata_serializable = self._normalizer.serialize_metadata(chunk.metadata)
        return {
            "document_id": document_id,
            "vault_name": vault_name,
            "metadata_json": json.dumps(metadata_serializable, default=str),
            "frontmatter_tags": chunk.frontmatter_tags,
            "metadata_hash": self._normalizer.compute_metadata_hash(chunk.metadata),
        }

    def _get_full_path(self, file_path: str) -> Path:
        """Получение полного пути к файлу.

        Args:
            file_path: Относительный путь к файлу

        Returns:
            Полный абсолютный путь
        """
        # TODO: Реализовать получение полного пути на основе vault_path
        # Пока возвращаем относительный путь
        return Path(file_path)

    def _detect_content_type(self, file_path: str) -> str:
        """Определение типа контента файла.

        Args:
            file_path: Путь к файлу

        Returns:
            Тип контента (markdown, pdf, image, etc.)
        """
        ext = Path(file_path).suffix.lower()
        if ext == ".md":
            return "markdown"
        elif ext == ".pdf":
            return "pdf"
        elif ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]:
            return "image"
        else:
            return "unknown"

    def _get_file_size(self, file_path: str) -> int:
        """Получение размера файла в байтах.

        Args:
            file_path: Путь к файлу

        Returns:
            Размер файла в байтах (0 если файл не найден)
        """
        # TODO: Реализовать получение размера файла на основе vault_path
        # Пока возвращаем 0
        return 0

    def _compute_file_content_hash(self, file_path: str) -> str:
        """Вычисление SHA256 хеша содержимого файла.

        Args:
            file_path: Путь к файлу (может быть относительным или абсолютным)

        Returns:
            SHA256 хеш в hex формате
        """
        try:
            # Пытаемся получить полный путь
            full_path = self._get_full_path(file_path)
            if not full_path.exists():
                # Если файл не найден, возвращаем пустой хеш
                return ""

            sha256 = hashlib.sha256()
            with open(full_path, "rb") as f:
                # Читаем файл блоками для эффективности
                while data := f.read(8192):
                    sha256.update(data)

            return sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute content hash for {file_path}: {e}")
            return ""
