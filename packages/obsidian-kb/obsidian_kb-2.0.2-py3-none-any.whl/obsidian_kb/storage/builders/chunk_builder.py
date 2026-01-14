"""ChunkRecordBuilder — построение записей для таблицы chunks."""

from typing import Any

from obsidian_kb.core.data_normalizer import DataNormalizer
from obsidian_kb.types import DocumentChunk


class ChunkRecordBuilder:
    """Построение записей для таблицы chunks.

    Отвечает за создание корректных записей для хранения чанков
    в базе данных LanceDB.
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
        embedding: list[float],
        vault_name: str,
    ) -> dict[str, Any]:
        """Построение записи для таблицы chunks.

        Args:
            chunk: Чанк документа
            embedding: Векторное представление
            vault_name: Имя vault'а

        Returns:
            Словарь с данными для записи в таблицу chunks
        """
        document_id = f"{vault_name}::{chunk.file_path}"

        # Извлекаем chunk_index из id (формат: vault_name::file_path::chunk_index)
        chunk_index = 0
        try:
            chunk_index = int(chunk.id.split("::")[-1])
        except (ValueError, IndexError):
            pass

        return {
            "chunk_id": chunk.id,
            "document_id": document_id,
            "vault_name": vault_name,
            "chunk_index": chunk_index,
            "section": chunk.section,
            "content": chunk.content,
            "vector": embedding,
            "links": chunk.links,
            "inline_tags": chunk.inline_tags,
        }

    def build_batch(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
        vault_name: str,
    ) -> list[dict[str, Any]]:
        """Построение батча записей для таблицы chunks.

        Args:
            chunks: Список чанков документов
            embeddings: Список векторных представлений
            vault_name: Имя vault'а

        Returns:
            Список словарей с данными для записи в таблицу chunks

        Raises:
            ValueError: Если количество чанков не соответствует количеству embeddings
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Number of chunks ({len(chunks)}) doesn't match "
                f"number of embeddings ({len(embeddings)})"
            )

        return [
            self.build_record(chunk, embedding, vault_name)
            for chunk, embedding in zip(chunks, embeddings)
        ]
