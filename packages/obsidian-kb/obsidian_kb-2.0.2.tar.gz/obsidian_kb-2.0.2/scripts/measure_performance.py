#!/usr/bin/env python3
"""Скрипт для измерения производительности индексирования и поиска."""

import asyncio
import time
from pathlib import Path

from obsidian_kb.embedding_service import EmbeddingService
from obsidian_kb.lance_db import LanceDBManager
from obsidian_kb.vault_indexer import VaultIndexer


async def measure_indexing(vault_path: Path, vault_name: str):
    """Измерение времени индексирования."""
    print(f"\n📊 Измерение индексирования: {vault_name}")
    print("=" * 60)
    
    # Сканирование файлов
    start = time.time()
    indexer = VaultIndexer(vault_path, vault_name)
    chunks = await indexer.scan_all()
    scan_time = time.time() - start
    
    print(f"✅ Сканирование: {len(chunks)} чанков за {scan_time:.2f} сек")
    print(f"   Скорость: {len(chunks)/scan_time:.1f} чанков/сек")
    
    if not chunks:
        return
    
    # Получение embeddings (тест на небольшом количестве)
    test_size = min(50, len(chunks))
    start = time.time()
    embedding_service = EmbeddingService()
    texts = [c.content for c in chunks[:test_size]]
    embeddings = await embedding_service.get_embeddings_batch(texts)
    embed_time = time.time() - start
    await embedding_service.close()
    
    print(f"✅ Embeddings ({test_size} чанков): {embed_time:.2f} сек")
    print(f"   Скорость: {test_size/embed_time:.1f} чанков/сек")
    print(f"   Экстраполяция на все {len(chunks)} чанков: ~{len(chunks)*embed_time/test_size:.1f} сек")
    
    # Запись в БД (тест на небольшом количестве)
    start = time.time()
    db_manager = LanceDBManager()
    await db_manager.upsert_chunks(vault_name, chunks[:test_size], embeddings)
    db_time = time.time() - start
    
    print(f"✅ Запись в БД ({test_size} чанков): {db_time:.2f} сек")
    print(f"   Экстраполяция на все {len(chunks)} чанков: ~{len(chunks)*db_time/test_size:.1f} сек")
    
    total_estimated = scan_time + (len(chunks)*embed_time/test_size) + (len(chunks)*db_time/test_size)
    print(f"\n⏱️  Оценочное время полного индексирования: {total_estimated:.1f} сек ({total_estimated/60:.1f} мин)")


async def measure_search(vault_name: str, query: str = "технологии"):
    """Измерение времени поиска."""
    print(f"\n🔍 Измерение поиска: {vault_name}")
    print("=" * 60)
    
    db_manager = LanceDBManager()
    embedding_service = EmbeddingService()
    
    # Embedding запроса
    start = time.time()
    query_embedding = await embedding_service.get_embedding(query)
    embed_time = time.time() - start
    
    # Поиск
    start = time.time()
    results = await db_manager.hybrid_search(vault_name, query_embedding, query, limit=10)
    search_time = time.time() - start
    
    await embedding_service.close()
    
    print(f"✅ Embedding запроса: {embed_time*1000:.1f} мс")
    print(f"✅ Поиск (hybrid): {search_time*1000:.1f} мс")
    print(f"✅ Всего: {(embed_time + search_time)*1000:.1f} мс")
    print(f"✅ Найдено результатов: {len(results)}")
    
    if (embed_time + search_time) * 1000 > 200:
        print("⚠️  Время поиска превышает целевое значение 200 мс")


async def main():
    """Основная функция."""
    print("🚀 Измерение производительности obsidian-kb\n")
    
    # Тестируем на примере vault'а
    # Замените на путь к вашему vault'у
    vault_path = Path("/path/to/your/vault")
    vault_name = "example-vault"
    
    if vault_path.exists():
        await measure_indexing(vault_path, vault_name)
        await measure_search(vault_name)
    else:
        print(f"⚠️  Vault не найден: {vault_path}")


if __name__ == "__main__":
    asyncio.run(main())

