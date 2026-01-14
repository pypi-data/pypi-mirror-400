#!/usr/bin/env python3
"""Скрипт для проверки статуса фоновых задач индексации."""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from obsidian_kb.indexing.job_queue import BackgroundJobQueue, JobStatus
from obsidian_kb.mcp_server import get_job_queue


async def main():
    """Показать список всех фоновых задач."""
    job_queue = get_job_queue()
    
    if not job_queue:
        print("❌ Очередь фоновых задач недоступна.")
        print("   Убедитесь, что MCP сервер запущен.")
        return
    
    # Получаем все задачи
    jobs = await job_queue.list_jobs()
    
    if not jobs:
        print("✅ Нет активных фоновых задач.")
        return
    
    # Группируем по статусам
    status_groups: dict[JobStatus, list] = {}
    for job in jobs:
        if job.status not in status_groups:
            status_groups[job.status] = []
        status_groups[job.status].append(job)
    
    status_order = [JobStatus.RUNNING, JobStatus.PENDING, JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    status_names = {
        JobStatus.RUNNING: "🟢 Выполняются",
        JobStatus.PENDING: "⏳ Ожидают",
        JobStatus.COMPLETED: "✅ Завершены",
        JobStatus.FAILED: "❌ Ошибки",
        JobStatus.CANCELLED: "🚫 Отменены",
    }
    
    print(f"\n📊 Всего задач: {len(jobs)}\n")
    
    for status in status_order:
        if status not in status_groups:
            continue
        
        jobs_list = status_groups[status]
        print(f"{status_names[status]} ({len(jobs_list)})")
        print("-" * 60)
        
        for job in jobs_list[:20]:  # Показываем до 20 задач на статус
            print(f"\n  ID: {job.id}")
            print(f"  Vault: {job.vault_name}")
            print(f"  Операция: {job.operation}")
            print(f"  Прогресс: {job.progress * 100:.1f}%")
            print(f"  Создана: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if job.started_at:
                print(f"  Начата: {job.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if job.completed_at:
                print(f"  Завершена: {job.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if job.error:
                print(f"  ⚠️  Ошибка: {job.error}")
            if job.result:
                result = job.result
                print(f"  📄 Документов: {result.documents_processed}/{result.documents_total}")
                print(f"  📦 Чанков создано: {result.chunks_created}")
        
        if len(jobs_list) > 20:
            print(f"\n  ... и ещё {len(jobs_list) - 20} задач")
        
        print()


if __name__ == "__main__":
    asyncio.run(main())

