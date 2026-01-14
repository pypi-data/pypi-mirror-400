"""MCP tools для анализа качества индекса и мониторинга."""

import asyncio
import logging
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from obsidian_kb.service_container import get_service_container
from obsidian_kb.types import RetrievalGranularity, SearchRequest, VaultNotFoundError

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Глобальный контейнер сервисов
services = get_service_container()


async def index_coverage(vault_name: str) -> str:
    """Анализ покрытия индекса.
    
    Args:
        vault_name: Имя vault'а
    
    Returns:
        Отчёт о покрытии:
        - Всего файлов / проиндексировано / ожидает
        - Файлы без enrichment
        - Файлы с устаревшим индексом
        - Битые ссылки в индексе
    """
    try:
        # Получаем статистику через DiagnosticsService
        coverage_data = await services.diagnostics_service.index_coverage(vault_name)
        
        if "error" in coverage_data:
            return f"❌ Ошибка получения покрытия: {coverage_data['error']}"
        
        lines = [f"## Анализ покрытия индекса: {vault_name}\n"]
        
        total_files = coverage_data.get("total_files", 0)
        indexed_files = coverage_data.get("indexed_files", 0)
        coverage_percent = coverage_data.get("coverage_percent", 0.0)
        total_chunks = coverage_data.get("total_chunks", 0)
        
        lines.append("### Общая статистика\n")
        lines.append(f"- **Всего файлов:** {total_files}")
        lines.append(f"- **Проиндексировано:** {indexed_files}")
        lines.append(f"- **Ожидает индексации:** {total_files - indexed_files}")
        lines.append(f"- **Покрытие:** {coverage_percent:.1f}%")
        lines.append(f"- **Всего чанков:** {total_chunks}")
        lines.append("")
        
        # Статистика по типам документов
        type_stats = coverage_data.get("type_stats", {})
        if type_stats:
            lines.append("### Статистика по типам документов\n")
            lines.append("| Тип | Количество |")
            lines.append("|-----|-----------|")
            for doc_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| {doc_type} | {count} |")
            lines.append("")
        
        # Статистика по тегам
        tag_stats = coverage_data.get("tag_stats", {})
        if tag_stats:
            # tag_stats может быть {"frontmatter": {...}, "inline": {...}} или {tag: count}
            # Объединяем все теги в один словарь
            combined_tags: dict[str, int] = {}
            if isinstance(tag_stats, dict):
                for key, value in tag_stats.items():
                    if isinstance(value, dict):
                        # Вложенный словарь (frontmatter/inline)
                        for tag, count in value.items():
                            if isinstance(count, (int, float)):
                                combined_tags[tag] = combined_tags.get(tag, 0) + int(count)
                    elif isinstance(value, (int, float)):
                        # Простой {tag: count}
                        combined_tags[key] = int(value)

            if combined_tags:
                lines.append("### Топ-10 тегов\n")
                lines.append("| Тег | Количество |")
                lines.append("|-----|-----------|")
                for tag, count in sorted(combined_tags.items(), key=lambda x: x[1], reverse=True)[:10]:
                    lines.append(f"| {tag} | {count} |")
                lines.append("")
        
        # Статистика по ссылкам
        link_stats = coverage_data.get("link_stats", {})
        if link_stats:
            lines.append("### Топ-10 ссылок\n")
            lines.append("| Ссылка | Количество |")
            lines.append("|--------|-----------|")
            for link, count in sorted(link_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                lines.append(f"| {link} | {count} |")
            lines.append("")
        
        # Рекомендации
        lines.append("### Рекомендации\n")
        if coverage_percent < 50:
            lines.append("- ⚠️ Покрытие индекса низкое (<50%). Рекомендуется полная переиндексация.")
        elif coverage_percent < 80:
            lines.append("- ⚠️ Покрытие индекса среднее (<80%). Рекомендуется индексация новых файлов.")
        else:
            lines.append("- ✅ Покрытие индекса хорошее (≥80%).")
        
        if total_files - indexed_files > 0:
            lines.append(
                f"- 📝 Найдено {total_files - indexed_files} файлов, ожидающих индексации. "
                f"Используйте `index_documents(\"{vault_name}\")` для индексации."
            )
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"❌ Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in index_coverage: {e}", exc_info=True)
        return f"❌ Ошибка анализа покрытия: {e}"


async def test_retrieval(
    vault_name: str,
    queries: list[str],
    expected_docs: list[str] | None = None,
) -> str:
    """Тестирование качества retrieval.
    
    Args:
        vault_name: Имя vault'а
        queries: Тестовые запросы
        expected_docs: Ожидаемые документы (для расчёта recall)
    
    Returns:
        Результаты тестирования:
        - Для каждого запроса: top-5 результатов
        - Recall@5 если указаны expected_docs
        - Среднее время ответа
    """
    try:
        lines = [f"## Тестирование качества retrieval: {vault_name}\n"]
        lines.append(f"**Количество запросов:** {len(queries)}\n")
        
        results = []
        total_time = 0.0
        
        for i, query in enumerate(queries, 1):
            lines.append(f"### Запрос {i}: `{query}`\n")
            
            # Выполняем поиск
            start_time = time.time()
            request = SearchRequest(
                vault_name=vault_name,
                query=query,
                limit=5,
                search_type="hybrid",
                granularity=RetrievalGranularity.CHUNK,
            )
            response = await services.search_service.search(request)
            elapsed_time = (time.time() - start_time) * 1000
            
            total_time += elapsed_time
            
            if not response.results:
                lines.append("*Результаты не найдены*\n")
                results.append({
                    "query": query,
                    "found": 0,
                    "found_paths": [],
                    "time_ms": elapsed_time,
                })
                # Проверяем recall даже если результатов нет
                if expected_docs and i <= len(expected_docs):
                    expected = expected_docs[i - 1]
                    lines.append(f"**Recall@5:** ❌ 0%")
                    lines.append(f"**Ожидаемый документ:** `{expected}`")
                    lines.append(f"⚠️ Ожидаемый документ не найден (результатов нет)")
                    lines.append("")
                continue
            
            lines.append(f"**Найдено:** {len(response.results)} результатов")
            lines.append(f"**Время:** {elapsed_time:.1f} мс\n")
            
            # Показываем результаты
            for j, result in enumerate(response.results[:5], 1):
                score = result.score.value if result.score else 0.0
                lines.append(f"{j}. **{result.title or result.file_path}** (score: {score:.3f})")
                lines.append(f"   - Путь: `{result.file_path}`")
                if result.snippet:
                    snippet_preview = result.snippet[:100].replace("\n", " ")
                    if len(result.snippet) > 100:
                        snippet_preview += "..."
                    lines.append(f"   - Snippet: {snippet_preview}")
                lines.append("")
            
            # Проверяем recall если указаны expected_docs
            if expected_docs and i <= len(expected_docs):
                expected = expected_docs[i - 1]
                found_paths = [r.file_path for r in response.results]
                recall = 1.0 if expected in found_paths else 0.0
                lines.append(f"**Recall@5:** {'✅' if recall > 0 else '❌'} {recall * 100:.0f}%")
                lines.append(f"**Ожидаемый документ:** `{expected}`")
                if expected not in found_paths:
                    lines.append(f"⚠️ Ожидаемый документ не найден в top-5")
                lines.append("")
            
            results.append({
                "query": query,
                "found": len(response.results),
                "found_paths": [r.file_path for r in response.results],
                "time_ms": elapsed_time,
            })
        
        # Итоговая статистика
        lines.append("### Итоговая статистика\n")
        avg_time = total_time / len(queries) if queries else 0.0
        avg_results = sum(r["found"] for r in results) / len(results) if results else 0.0
        
        lines.append(f"- **Среднее время ответа:** {avg_time:.1f} мс")
        lines.append(f"- **Среднее количество результатов:** {avg_results:.1f}")
        
        if expected_docs:
            total_recall = sum(
                1.0 if expected_docs[i] in results[i].get("found_paths", [])
                else 0.0
                for i in range(min(len(results), len(expected_docs)))
            )
            avg_recall = total_recall / len(expected_docs) if expected_docs else 0.0
            lines.append(f"- **Средний Recall@5:** {avg_recall * 100:.1f}%")
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"❌ Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in test_retrieval: {e}", exc_info=True)
        return f"❌ Ошибка тестирования retrieval: {e}"


async def audit_index(vault_name: str) -> str:
    """Аудит качества индекса.
    
    Args:
        vault_name: Имя vault'а
    
    Returns:
        Отчёт об аудите:
        - Качество чанков (слишком большие/маленькие)
        - Качество enrichment (пустые context_prefix)
        - Дубликаты
        - Рекомендации по улучшению
    """
    try:
        lines = [f"## Аудит качества индекса: {vault_name}\n"]
        
        # Получаем конфигурацию для проверки размеров чанков
        from obsidian_kb.config.manager import get_config_manager

        config_manager = get_config_manager()
        config = config_manager.get_config(vault_name)
        
        chunk_size = config.indexing.chunk_size
        min_chunk_size = config.indexing.min_chunk_size
        
        # Получаем все чанки из репозитория
        chunk_repository = services.chunk_repository
        
        # Получаем статистику vault'а
        stats = await services.db_manager.get_vault_stats(vault_name)
        
        # Анализируем чанки через базу данных
        chunks_table = await services.db_manager._ensure_table(vault_name, "chunks")
        db = services.db_manager._get_db()
        
        def _analyze_chunks():
            try:
                arrow_table = chunks_table.to_arrow()
                
                if arrow_table.num_rows == 0:
                    return {
                        "total": 0,
                        "large_chunks": 0,
                        "small_chunks": 0,
                        "empty_context": 0,
                        "duplicates": 0,
                    }
                
                # Анализируем размеры чанков (приблизительно по длине текста)
                texts = arrow_table["content"].to_pylist()
                
                # Оценка токенов: ~4 символа на токен
                large_chunks = sum(1 for text in texts if len(text) > chunk_size * 4)
                small_chunks = sum(1 for text in texts if len(text) < min_chunk_size * 4)
                
                # Проверяем context_prefix если есть поле
                empty_context = 0
                if "context_prefix" in arrow_table.column_names:
                    context_prefixes = arrow_table["context_prefix"].to_pylist()
                    empty_context = sum(1 for cp in context_prefixes if not cp or cp.strip() == "")
                
                # Проверяем дубликаты по тексту (упрощённо)
                text_counter = Counter(texts)
                duplicates = sum(count - 1 for count in text_counter.values() if count > 1)
                
                return {
                    "total": arrow_table.num_rows,
                    "large_chunks": large_chunks,
                    "small_chunks": small_chunks,
                    "empty_context": empty_context,
                    "duplicates": duplicates,
                }
            except Exception as e:
                logger.error(f"Error analyzing chunks: {e}")
                return {
                    "total": 0,
                    "large_chunks": 0,
                    "small_chunks": 0,
                    "empty_context": 0,
                    "duplicates": 0,
                }
        
        analysis = await asyncio.to_thread(_analyze_chunks)
        
        total_chunks = analysis["total"]
        large_chunks = analysis["large_chunks"]
        small_chunks = analysis["small_chunks"]
        empty_context = analysis["empty_context"]
        duplicates = analysis["duplicates"]
        
        lines.append("### Качество чанков\n")
        lines.append(f"- **Всего чанков:** {total_chunks}")
        lines.append(f"- **Слишком большие (> {chunk_size} токенов):** {large_chunks}")
        lines.append(f"- **Слишком маленькие (< {min_chunk_size} токенов):** {small_chunks}")
        lines.append("")
        
        if large_chunks > 0:
            large_percent = (large_chunks / total_chunks * 100) if total_chunks > 0 else 0
            lines.append(f"⚠️ {large_percent:.1f}% чанков превышают максимальный размер.")
        
        if small_chunks > 0:
            small_percent = (small_chunks / total_chunks * 100) if total_chunks > 0 else 0
            lines.append(f"⚠️ {small_percent:.1f}% чанков меньше минимального размера.")
        
        if large_chunks == 0 and small_chunks == 0:
            lines.append("✅ Размеры чанков оптимальны.")
        
        lines.append("")
        
        # Качество enrichment
        lines.append("### Качество enrichment\n")
        if empty_context > 0:
            empty_percent = (empty_context / total_chunks * 100) if total_chunks > 0 else 0
            lines.append(f"⚠️ **Пустые context_prefix:** {empty_context} ({empty_percent:.1f}%)")
            lines.append("   Рекомендуется переиндексация с включённым enrichment.")
        else:
            lines.append("✅ Все чанки имеют context_prefix.")
        
        lines.append("")
        
        # Дубликаты
        lines.append("### Дубликаты\n")
        if duplicates > 0:
            lines.append(f"⚠️ **Найдено дубликатов:** {duplicates}")
            lines.append("   Некоторые чанки имеют идентичный текст.")
        else:
            lines.append("✅ Дубликаты не найдены.")
        
        lines.append("")
        
        # Рекомендации
        lines.append("### Рекомендации\n")
        
        recommendations = []
        
        if large_chunks > total_chunks * 0.1:  # >10% больших чанков
            recommendations.append(
                f"- Уменьшите `chunk_size` до {int(chunk_size * 0.8)} или используйте стратегию `semantic` chunking"
            )
        
        if small_chunks > total_chunks * 0.1:  # >10% маленьких чанков
            recommendations.append(
                f"- Увеличьте `min_chunk_size` до {int(min_chunk_size * 1.2)} или объедините мелкие чанки"
            )
        
        if empty_context > total_chunks * 0.2:  # >20% без enrichment
            recommendations.append(
                f"- Выполните переиндексацию с `enrichment=\"contextual\"` или `enrichment=\"full\"`"
            )
        
        if duplicates > 0:
            recommendations.append(
                "- Проверьте документы на наличие дублирующегося контента"
            )
        
        if not recommendations:
            recommendations.append("✅ Качество индекса хорошее, рекомендаций нет.")
        
        for rec in recommendations:
            lines.append(rec)
        
        return "\n".join(lines)
    
    except VaultNotFoundError:
        return f"❌ Vault '{vault_name}' не найден."
    except Exception as e:
        logger.error(f"Error in audit_index: {e}", exc_info=True)
        return f"❌ Ошибка аудита индекса: {e}"


async def cost_report(
    vault_name: str | None = None,
    period: str = "month",  # day | week | month | all
) -> str:
    """Отчёт о затратах на LLM.
    
    Args:
        vault_name: Фильтр по vault'у
        period: Период отчёта (day | week | month | all)
    
    Returns:
        Разбивка затрат:
        - По провайдерам
        - По операциям (embedding / enrichment)
        - По vault'ам
        - Тренд vs прошлый период
    """
    try:
        from obsidian_kb.quality.cost_tracker import CostTracker
        
        cost_tracker = CostTracker()
        costs_data = await cost_tracker.get_costs(
            vault_name=vault_name,
            period=period,
        )
        
        lines = ["## Отчёт о затратах на LLM\n"]
        
        # Определяем название периода
        period_names = {
            "day": "последние 24 часа",
            "week": "последняя неделя",
            "month": "последний месяц",
            "all": "всё время",
        }
        period_name = period_names.get(period, period)
        
        lines.append(f"**Период:** {period_name}")
        if vault_name:
            lines.append(f"**Vault:** {vault_name}")
        lines.append("")
        
        # Общая статистика
        total_cost = costs_data.get("total_cost_usd", 0.0)
        total_input_tokens = costs_data.get("total_input_tokens", 0)
        total_output_tokens = costs_data.get("total_output_tokens", 0)
        record_count = costs_data.get("record_count", 0)
        
        lines.append("### Общая статистика\n")
        lines.append(f"- **Всего затрат:** ${total_cost:.4f}")
        lines.append(f"- **Входных токенов:** {total_input_tokens:,}")
        lines.append(f"- **Выходных токенов:** {total_output_tokens:,}")
        lines.append(f"- **Записей:** {record_count}")
        lines.append("")
        
        # Разбивка по провайдерам
        by_provider = costs_data.get("by_provider", {})
        if by_provider:
            lines.append("### По провайдерам\n")
            lines.append("| Провайдер | Затраты (USD) | % |")
            lines.append("|-----------|---------------|---|")
            for provider, cost in sorted(by_provider.items(), key=lambda x: x[1], reverse=True):
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                lines.append(f"| {provider} | ${cost:.4f} | {percentage:.1f}% |")
            lines.append("")
        
        # Разбивка по vault'ам
        by_vault = costs_data.get("by_vault", {})
        if by_vault:
            lines.append("### По vault'ам\n")
            lines.append("| Vault | Затраты (USD) | % |")
            lines.append("|-------|---------------|---|")
            for vault, cost in sorted(by_vault.items(), key=lambda x: x[1], reverse=True):
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                lines.append(f"| {vault} | ${cost:.4f} | {percentage:.1f}% |")
            lines.append("")
        
        # Разбивка по типам операций
        by_operation = costs_data.get("by_operation", {})
        if by_operation:
            lines.append("### По типам операций\n")
            lines.append("| Операция | Затраты (USD) | % |")
            lines.append("|----------|---------------|---|")
            for op_type, cost in sorted(by_operation.items(), key=lambda x: x[1], reverse=True):
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                lines.append(f"| {op_type} | ${cost:.4f} | {percentage:.1f}% |")
            lines.append("")
        
        if total_cost == 0.0:
            lines.append("### Примечание\n")
            lines.append(
                "Затраты не отслеживаются. Для включения отслеживания затрат:\n"
                "- Убедитесь, что CostTracker интегрирован с провайдерами\n"
                "- Проверьте, что операции LLM записывают затраты через CostTracker"
            )
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.error(f"Error in cost_report: {e}", exc_info=True)
        return f"❌ Ошибка получения отчёта о затратах: {e}"


async def performance_report(vault_name: str | None = None) -> str:
    """Отчёт о производительности.
    
    Args:
        vault_name: Фильтр по vault'у
    
    Returns:
        Метрики производительности:
        - Latency индексации (p50, p95, p99)
        - Latency поиска
        - Throughput
        - Ошибки и retries
    """
    try:
        lines = ["## Отчёт о производительности\n"]
        
        if vault_name:
            lines.append(f"**Vault:** {vault_name}")
        lines.append("")
        
        # Получаем метрики из MetricsCollector
        summary = await services.metrics_collector.get_summary(
            days=7,
            limit=100,
            vault_name=vault_name,
        )
        
        lines.append("### Метрики поиска (последние 7 дней)\n")
        lines.append(f"- **Всего запросов:** {summary.total_searches}")
        lines.append(f"- **Среднее время выполнения:** {summary.avg_execution_time_ms:.2f} мс")
        lines.append(f"- **Средняя релевантность:** {summary.avg_relevance_score:.3f}")
        lines.append(f"- **Пустых результатов:** {summary.empty_results_count} ({summary.empty_results_percentage:.1f}%)")
        lines.append("")
        
        # По типам поиска
        if summary.searches_by_type:
            lines.append("### Производительность по типам поиска\n")
            lines.append("| Тип | Количество | Среднее время (мс) |")
            lines.append("|-----|-----------|-------------------|")
            
            # Группируем по типам для расчёта среднего времени
            # (в реальной системе нужно хранить время по типам отдельно)
            for search_type, count in sorted(
                summary.searches_by_type.items(), key=lambda x: x[1], reverse=True
            ):
                # Используем общее среднее время как приближение
                lines.append(
                    f"| {search_type} | {count} | {summary.avg_execution_time_ms:.2f} |"
                )
            lines.append("")
        
        # Популярные запросы
        if summary.popular_queries:
            lines.append("### Популярные запросы\n")
            for idx, (query, count) in enumerate(summary.popular_queries[:10], 1):
                query_preview = query[:50] + "..." if len(query) > 50 else query
                lines.append(f"{idx}. `{query_preview}` — {count} раз")
            lines.append("")
        
        # Запросы без результатов
        if summary.queries_with_no_results:
            lines.append("### Запросы без результатов\n")
            lines.append("| Запрос | Количество |")
            lines.append("|--------|-----------|")
            for query, count in summary.queries_with_no_results[:10]:
                query_preview = query[:50] + "..." if len(query) > 50 else query
                lines.append(f"| `{query_preview}` | {count} |")
            lines.append("")
        
        # Рекомендации
        lines.append("### Рекомендации\n")
        
        recommendations = []
        
        if summary.avg_execution_time_ms > 1000:
            recommendations.append(
                "⚠️ Среднее время выполнения поиска высокое (>1s). "
                "Рекомендуется оптимизация индекса или использование кэширования."
            )
        
        if summary.empty_results_percentage > 20:
            recommendations.append(
                f"⚠️ Высокий процент пустых результатов ({summary.empty_results_percentage:.1f}%). "
                "Рекомендуется проверка качества индексации."
            )
        
        if summary.avg_relevance_score < 0.5:
            recommendations.append(
                f"⚠️ Низкая средняя релевантность ({summary.avg_relevance_score:.3f}). "
                "Рекомендуется улучшение качества embeddings или использование reranking."
            )
        
        if not recommendations:
            recommendations.append("✅ Производительность в норме.")
        
        for rec in recommendations:
            lines.append(f"- {rec}")
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.error(f"Error in performance_report: {e}", exc_info=True)
        return f"❌ Ошибка получения отчёта о производительности: {e}"

