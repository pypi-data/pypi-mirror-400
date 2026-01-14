# Оптимизация поиска и Fine-tuning

## Содержание

1. [Текущее состояние](#текущее-состояние)
2. [Использование через MCP с агентами](#использование-через-mcp-с-агентами)
3. [Улучшения для Fine-tuning](#улучшения-для-fine-tuning)
4. [RAG (Retrieval-Augmented Generation) практики](#rag-retrieval-augmented-generation-практики)
5. [Оптимизация ранжирования](#оптимизация-ранжирования)
6. [Оптимизация для агентных сценариев](#оптимизация-для-агентных-сценариев)
7. [Рекомендации по реализации](#рекомендации-по-реализации)

## Текущее состояние

### Существующие возможности

- ✅ Векторный поиск (semantic search) через embeddings
- ✅ Полнотекстовый поиск (BM25/FTS)
- ✅ Гибридный поиск с простым взвешиванием (alpha = 0.7)
- ✅ Расширенные фильтры (теги, даты, тип документа, wikilinks)
- ✅ Метрики использования для анализа
- ✅ MCP сервер для интеграции с Claude, Cursor и другими агентами

### Ограничения

- Простое линейное объединение scores в hybrid search
- Нет адаптивного ранжирования на основе обратной связи
- Нет query expansion и query rewriting
- Нет re-ranking модели
- Ограниченная персонализация
- Не оптимизировано для агентных запросов (могут быть менее точными)

## Использование через MCP с агентами

### Контекст использования

**obsidian-kb** используется как **MCP (Model Context Protocol) сервер** в связке с:
- **Claude Desktop** - для доступа к знаниям через Claude AI
- **Cursor** - для интеграции с IDE
- **Другие агенты** - любые системы, поддерживающие MCP протокол

### Особенности агентных запросов

#### 1. Генерация запросов агентом

Агенты (LLM) генерируют поисковые запросы, что создаёт специфические особенности:

- **Менее точные формулировки**: Агенты могут использовать более общие термины
- **Контекстно-зависимые запросы**: Запросы зависят от текущего диалога
- **Множественные уточняющие запросы**: Агенты могут делать несколько запросов для уточнения
- **Структурированные запросы**: Агенты могут использовать фильтры (теги, даты) более активно

**Примеры агентных запросов:**
```
"найди информацию о Python async"
"что написано про тестирование с тегом #testing"
"найди заметки про проект X созданные в прошлом месяце"
```

#### 2. Обработка результатов агентом

Результаты поиска используются агентом для:
- **Генерации ответов** (RAG - Retrieval-Augmented Generation)
- **Извлечения фактов** из найденных документов
- **Синтеза информации** из нескольких источников
- **Ответов на вопросы** на основе контекста

**Требования к результатам:**
- **Релевантность**: Топ-K результаты должны быть максимально релевантными
- **Контекст**: Результаты должны содержать достаточно контекста для понимания
- **Структурированность**: Формат должен быть удобен для парсинга агентом
- **Скорость**: Быстрый ответ важен для интерактивности

### Оптимизации для агентных сценариев

#### 1. Query Normalization для агентов

Агенты могут генерировать запросы с лишними словами или неоптимальной формулировкой:

```python
class AgentQueryNormalizer:
    """Нормализация запросов от агентов."""
    
    def normalize(self, query: str) -> str:
        """Нормализация агентного запроса."""
        # Убираем служебные слова агентов
        agent_patterns = [
            r"найди\s+",
            r"найти\s+",
            r"покажи\s+",
            r"ищи\s+",
            r"find\s+",
            r"search\s+for\s+",
            r"show\s+me\s+",
            r"что\s+написано\s+про\s+",
            r"информация\s+о\s+",
        ]
        
        normalized = query
        for pattern in agent_patterns:
            normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE)
        
        return normalized.strip()
```

#### 2. Контекстное извлечение для RAG

Для RAG сценариев важно извлекать не только релевантные чанки, но и контекст вокруг них:

```python
async def retrieve_for_rag(
    db_manager: LanceDBManager,
    vault_name: str,
    query: str,
    limit: int = 5,
    context_window: int = 2,
    min_context_length: int = 500
) -> list[SearchResult]:
    """Извлечение результатов с расширенным контекстом для RAG.
    
    Args:
        context_window: Количество соседних чанков для включения
        min_context_length: Минимальная длина контекста в символах
    """
    # Обычный поиск
    results = await db_manager.hybrid_search(...)
    
    # Для каждого результата добавляем контекст
    enriched = []
    for result in results:
        # Находим соседние чанки того же файла
        context = await get_surrounding_context(
            db_manager, vault_name, result, context_window
        )
        
        # Объединяем контекст с результатом
        enriched_content = f"{context}\n\n{result.content}\n\n{context}"
        
        enriched.append(
            SearchResult(
                **{**result.__dict__, 'content': enriched_content}
            )
        )
    
    return enriched
```

#### 3. Многоэтапный поиск для агентов

Агенты могут делать последовательные запросы. Оптимизируем для этого сценария:

```python
class AgentSearchSession:
    """Сессия поиска для агента с кэшированием."""
    
    def __init__(self):
        self.query_cache: dict[str, list[SearchResult]] = {}
        self.related_queries: dict[str, list[str]] = {}
    
    async def search_with_fallback(
        self,
        query: str,
        vault_name: str,
        limit: int = 10
    ) -> list[SearchResult]:
        """Поиск с fallback стратегией для агентов."""
        
        # Попытка 1: Точный поиск
        results = await db_manager.hybrid_search(...)
        
        if len(results) < limit:
            # Попытка 2: Расширенный поиск
            expanded = await query_expander.expand(query, vault_name)
            for expanded_query in expanded[1:]:  # Пропускаем оригинал
                more_results = await db_manager.hybrid_search(...)
                results.extend(more_results)
        
        # Дедупликация
        results = deduplicate_results(results)
        
        return results[:limit]
```

#### 4. Оптимизация формата ответов для агентов

Текущий формат markdown хорош, но можно улучшить для парсинга агентом:

```python
def format_for_agent(
    results: list[SearchResult],
    query: str,
    include_metadata: bool = True,
    include_full_content: bool = False
) -> str:
    """Форматирование результатов специально для агентов.
    
    Args:
        include_metadata: Включать метаданные (теги, даты)
        include_full_content: Включать полный контент вместо превью
    """
    lines = []
    
    for idx, result in enumerate(results, 1):
        # Структурированный формат для легкого парсинга
        lines.append(f"## Result {idx}")
        lines.append(f"Title: {result.title}")
        lines.append(f"File: {result.file_path}")
        lines.append(f"Relevance: {result.score:.3f}")
        
        if include_metadata:
            lines.append(f"Tags: {', '.join(result.tags)}")
            if result.modified_at:
                lines.append(f"Modified: {result.modified_at.isoformat()}")
        
        # Контент (полный или превью)
        if include_full_content:
            lines.append(f"Content:\n{result.content}")
        else:
            lines.append(f"Preview:\n{result.content[:300]}...")
        
        lines.append("---")
    
    return "\n".join(lines)
```

## Улучшения для Fine-tuning

### 1. Адаптивное взвешивание в Hybrid Search

**Проблема**: Фиксированный `alpha = 0.7` не оптимален для всех типов запросов.

**Решение**: Динамическое определение alpha на основе характеристик запроса.

```python
# Пример реализации
def calculate_adaptive_alpha(query: str, query_vector: list[float]) -> float:
    """Вычисление адаптивного alpha на основе запроса."""
    # Факторы:
    # 1. Длина запроса (короткие запросы -> больше векторного поиска)
    # 2. Наличие специальных терминов (технические -> больше FTS)
    # 3. Исторические метрики для похожих запросов
    
    base_alpha = 0.7
    
    # Короткие запросы (< 3 слов) лучше работают с векторным поиском
    word_count = len(query.split())
    if word_count < 3:
        base_alpha = 0.8
    elif word_count > 10:
        base_alpha = 0.6
    
    # Технические термины (цифры, коды) -> больше FTS
    has_technical = bool(re.search(r'\d+|#[A-Za-z]+|`[^`]+`', query))
    if has_technical:
        base_alpha -= 0.1
    
    return max(0.3, min(0.9, base_alpha))
```

### 2. Query Expansion и Rewriting

**Проблема**: Пользовательские запросы могут быть неоптимальными для поиска.

**Решение**: Расширение и переформулирование запросов.

```python
class QueryExpander:
    """Расширение поисковых запросов."""
    
    def __init__(self, embedding_service, db_manager):
        self.embedding_service = embedding_service
        self.db_manager = db_manager
    
    async def expand_query(self, query: str, vault_name: str) -> list[str]:
        """Расширение запроса синонимами и связанными терминами."""
        # 1. Находим похожие термины из индекса
        # 2. Используем wikilinks для расширения контекста
        # 3. Добавляем синонимы из тегов
        
        expanded = [query]
        
        # Находим похожие документы для извлечения терминов
        query_embedding = await self.embedding_service.get_embedding(query)
        similar = await self.db_manager.vector_search(
            vault_name, query_embedding, limit=5
        )
        
        # Извлекаем ключевые термины из похожих документов
        for result in similar:
            # Простое извлечение ключевых слов (можно улучшить через TF-IDF)
            words = re.findall(r'\b\w{4,}\b', result.content.lower())
            # Добавляем уникальные термины
            for word in set(words[:5]):  # Топ-5 слов
                if word not in query.lower():
                    expanded.append(word)
        
        return expanded[:5]  # Ограничиваем количество
```

### 3. Re-ranking модель

**Проблема**: Первоначальное ранжирование может быть неоптимальным.

**Решение**: Двухэтапный поиск с re-ranking.

```python
class ReRanker:
    """Re-ranking результатов поиска."""
    
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
    
    async def rerank(
        self, 
        query: str, 
        results: list[SearchResult],
        top_k: int = 10
    ) -> list[SearchResult]:
        """Переранжирование результатов на основе cross-encoder подхода."""
        
        if len(results) <= top_k:
            return results
        
        # Получаем embedding запроса
        query_embedding = await self.embedding_service.get_embedding(query)
        
        # Вычисляем улучшенные scores
        reranked = []
        for result in results:
            # Получаем embedding результата
            result_embedding = await self.embedding_service.get_embedding(
                result.content[:500]  # Ограничиваем для производительности
            )
            
            # Комбинируем оригинальный score с cross-encoder score
            cross_score = cosine_similarity([query_embedding], [result_embedding])[0][0]
            
            # Взвешенная комбинация
            final_score = 0.6 * result.score + 0.4 * cross_score
            
            reranked.append(
                SearchResult(
                    **{**result.__dict__, 'score': final_score}
                )
            )
        
        # Сортируем и возвращаем топ-k
        reranked.sort(key=lambda x: x.score, reverse=True)
        return reranked[:top_k]
```

### 4. Обучение на основе обратной связи (Learning to Rank)

**Проблема**: Нет механизма обучения на основе пользовательских предпочтений.

**Решение**: Система сбора и использования обратной связи.

```python
@dataclass
class SearchFeedback:
    """Обратная связь по результатам поиска."""
    query: str
    clicked_result_id: str
    timestamp: datetime
    vault_name: str
    search_type: str

class FeedbackLearner:
    """Обучение на основе обратной связи."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.feedback_cache: dict[str, dict[str, float]] = {}  # query -> result_id -> score
    
    async def record_feedback(self, feedback: SearchFeedback):
        """Запись обратной связи."""
        # Сохраняем в БД метрик или отдельную таблицу
        # Обновляем локальный кэш для быстрого доступа
        
        key = f"{feedback.vault_name}::{feedback.query}"
        if key not in self.feedback_cache:
            self.feedback_cache[key] = {}
        
        # Увеличиваем score для кликнутого результата
        self.feedback_cache[key][feedback.clicked_result_id] = \
            self.feedback_cache[key].get(feedback.clicked_result_id, 0) + 1
    
    def apply_feedback_boost(
        self, 
        query: str, 
        vault_name: str,
        results: list[SearchResult]
    ) -> list[SearchResult]:
        """Применение boost на основе обратной связи."""
        key = f"{vault_name}::{query}"
        
        if key not in self.feedback_cache:
            return results
        
        feedback_scores = self.feedback_cache[key]
        
        boosted = []
        for result in results:
            boost = feedback_scores.get(result.chunk_id, 0)
            # Логарифмический boost для избежания перекосов
            boost_factor = 1.0 + (0.1 * math.log(1 + boost))
            
            boosted.append(
                SearchResult(
                    **{**result.__dict__, 'score': result.score * boost_factor}
                )
            )
        
        # Пересортировка после boost
        boosted.sort(key=lambda x: x.score, reverse=True)
        return boosted
```

## RAG (Retrieval-Augmented Generation) практики

### 1. Контекстное извлечение с окном

**Проблема**: Чанки могут терять контекст.

**Решение**: Извлечение соседних чанков для лучшего контекста.

```python
async def retrieve_with_context(
    db_manager: LanceDBManager,
    vault_name: str,
    query: str,
    limit: int = 5,
    context_window: int = 2
) -> list[SearchResult]:
    """Извлечение результатов с контекстными чанками."""
    
    # Обычный поиск
    results = await db_manager.hybrid_search(
        vault_name, query_embedding, query, limit=limit
    )
    
    # Для каждого результата находим соседние чанки
    enriched_results = []
    for result in results:
        # Извлекаем индекс чанка из chunk_id
        chunk_id_parts = result.chunk_id.split("::")
        if len(chunk_id_parts) >= 3:
            file_path = chunk_id_parts[1]
            chunk_index = int(chunk_id_parts[2])
            
            # Находим соседние чанки того же файла
            context_chunks = await db_manager.get_chunks_by_file(
                vault_name, file_path
            )
            
            # Фильтруем соседние чанки
            context_indices = range(
                max(0, chunk_index - context_window),
                min(len(context_chunks), chunk_index + context_window + 1)
            )
            
            # Объединяем контекст
            context_text = "\n\n".join([
                context_chunks[i].content 
                for i in context_indices 
                if i != chunk_index
            ])
            
            # Создаём обогащённый результат
            enriched = SearchResult(
                **{**result.__dict__, 'context': context_text}
            )
            enriched_results.append(enriched)
        else:
            enriched_results.append(result)
    
    return enriched_results
```

### 2. Многоэтапный поиск (Multi-stage Retrieval)

**Проблема**: Один этап поиска может пропустить релевантные документы.

**Решение**: Каскадный поиск с расширением на каждом этапе.

```python
async def multi_stage_search(
    db_manager: LanceDBManager,
    vault_name: str,
    query: str,
    stages: list[dict] = None
) -> list[SearchResult]:
    """Многоэтапный поиск с постепенным уточнением."""
    
    if stages is None:
        # Стандартные этапы
        stages = [
            {"type": "hybrid", "limit": 50, "alpha": 0.7},  # Широкий поиск
            {"type": "rerank", "limit": 20},  # Re-ranking
            {"type": "context", "limit": 10},  # Добавление контекста
        ]
    
    current_results = []
    
    # Этап 1: Широкий поиск
    stage1 = stages[0]
    if stage1["type"] == "hybrid":
        query_embedding = await embedding_service.get_embedding(query)
        current_results = await db_manager.hybrid_search(
            vault_name, query_embedding, query,
            limit=stage1["limit"],
            alpha=stage1.get("alpha", 0.7)
        )
    
    # Этап 2: Re-ranking
    if len(stages) > 1 and stage1["type"] == "rerank":
        reranker = ReRanker(embedding_service)
        current_results = await reranker.rerank(
            query, current_results, top_k=stage2["limit"]
        )
    
    # Этап 3: Добавление контекста
    if len(stages) > 2:
        current_results = await retrieve_with_context(
            db_manager, vault_name, query,
            limit=stage3["limit"]
        )
    
    return current_results
```

### 3. Query Decomposition

**Проблема**: Сложные запросы требуют разбиения на подзапросы.

**Решение**: Декомпозиция запроса на подзапросы.

```python
class QueryDecomposer:
    """Декомпозиция сложных запросов."""
    
    async def decompose(self, query: str) -> list[str]:
        """Разбиение запроса на подзапросы."""
        
        # Простая эвристика: разбиение по союзам
        # "И" -> все подзапросы должны быть в результате
        # "ИЛИ" -> хотя бы один подзапрос
        
        # Пример: "Python async OR JavaScript promises"
        if " OR " in query.upper():
            return [q.strip() for q in query.upper().split(" OR ")]
        
        # Пример: "Python AND async AND asyncio"
        if " AND " in query.upper():
            return [q.strip() for q in query.upper().split(" AND ")]
        
        # По умолчанию возвращаем исходный запрос
        return [query]
    
    async def search_decomposed(
        self,
        db_manager: LanceDBManager,
        vault_name: str,
        query: str
    ) -> list[SearchResult]:
        """Поиск с декомпозицией."""
        
        subqueries = await self.decompose(query)
        
        if len(subqueries) == 1:
            # Обычный поиск
            return await db_manager.hybrid_search(...)
        
        # Поиск по каждому подзапросу
        all_results = []
        for subquery in subqueries:
            results = await db_manager.hybrid_search(...)
            all_results.extend(results)
        
        # Объединение результатов
        # Для "AND" - пересечение
        # Для "OR" - объединение с дедупликацией
        
        return deduplicate_and_merge(all_results)
```

### 4. Semantic Chunking

**Проблема**: Фиксированный размер чанков может разрывать семантические единицы.

**Решение**: Семантическое разбиение на основе структуры документа.

```python
class SemanticChunker:
    """Семантическое разбиение документов."""
    
    def chunk_semantically(self, content: str, max_size: int = 1000) -> list[str]:
        """Разбиение с учётом семантической структуры."""
        
        chunks = []
        
        # 1. Разбиение по заголовкам (H1-H3)
        sections = self._split_by_headers(content)
        
        for section in sections:
            if len(section) <= max_size:
                chunks.append(section)
            else:
                # 2. Разбиение по параграфам
                paragraphs = section.split('\n\n')
                current_chunk = []
                current_size = 0
                
                for para in paragraphs:
                    para_size = len(para)
                    if current_size + para_size > max_size and current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                        current_chunk = [para]
                        current_size = para_size
                    else:
                        current_chunk.append(para)
                        current_size += para_size
                
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_by_headers(self, content: str) -> list[str]:
        """Разбиение по заголовкам markdown."""
        lines = content.split('\n')
        sections = []
        current_section = []
        
        for line in lines:
            if line.strip().startswith('#'):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
```

## Оптимизация ранжирования

### 1. Feature Engineering для ранжирования

Добавление дополнительных признаков для улучшения ранжирования:

```python
@dataclass
class RankingFeatures:
    """Признаки для ранжирования."""
    vector_score: float
    fts_score: float
    title_match: float  # Совпадение в заголовке
    tag_match: float  # Совпадение тегов
    recency: float  # Свежесть документа
    popularity: float  # Популярность (на основе кликов)
    link_count: int  # Количество ссылок на документ
    content_length: int  # Длина контента
    section_relevance: float  # Релевантность секции

def extract_features(
    result: SearchResult,
    query: str,
    query_embedding: list[float]
) -> RankingFeatures:
    """Извлечение признаков для ранжирования."""
    
    # Title match
    title_lower = result.title.lower()
    query_lower = query.lower()
    title_match = sum(1 for word in query_lower.split() if word in title_lower) / len(query_lower.split())
    
    # Tag match
    tag_match = sum(1 for tag in result.tags if any(word in tag.lower() for word in query_lower.split())) / max(len(result.tags), 1)
    
    # Recency (0-1, где 1 = самый свежий)
    if result.modified_at:
        days_old = (datetime.now() - result.modified_at).days
        recency = max(0, 1 - (days_old / 365))  # Нормализация на год
    
    return RankingFeatures(
        vector_score=result.score,
        fts_score=result.score,  # Уже объединённый в hybrid
        title_match=title_match,
        tag_match=tag_match,
        recency=recency or 0.5,
        popularity=0.5,  # Из feedback системы
        link_count=len(result.links),
        content_length=len(result.content),
        section_relevance=0.5
    )
```

### 2. Learning to Rank модель

Использование простой модели для обучения ранжированию:

```python
class SimpleRankingModel:
    """Простая модель ранжирования на основе признаков."""
    
    def __init__(self):
        # Веса признаков (можно обучить на данных)
        self.weights = {
            'vector_score': 0.3,
            'fts_score': 0.2,
            'title_match': 0.15,
            'tag_match': 0.1,
            'recency': 0.1,
            'popularity': 0.1,
            'link_count': 0.05,
        }
    
    def predict_score(self, features: RankingFeatures) -> float:
        """Предсказание финального score."""
        
        score = (
            self.weights['vector_score'] * features.vector_score +
            self.weights['fts_score'] * features.fts_score +
            self.weights['title_match'] * features.title_match +
            self.weights['tag_match'] * features.tag_match +
            self.weights['recency'] * features.recency +
            self.weights['popularity'] * features.popularity +
            self.weights['link_count'] * min(features.link_count / 10, 1.0)  # Нормализация
        )
        
        return min(1.0, max(0.0, score))
    
    def train(self, training_data: list[tuple[RankingFeatures, float]]):
        """Обучение модели на данных (упрощённая версия)."""
        # Можно использовать градиентный спуск или другие методы
        # Для простоты оставляем ручную настройку весов
        pass
```

## Рекомендации по реализации

### Приоритет 1: Быстрые улучшения

1. **Адаптивное alpha** - легко реализовать, сразу улучшит качество
2. **Feature-based ranking** - добавить признаки для ранжирования
3. **Query expansion** - базовое расширение запросов

### Приоритет 2: Среднесрочные улучшения

1. **Re-ranking модель** - требует дополнительных вычислений, но улучшает качество
2. **Feedback система** - сбор и использование обратной связи
3. **Semantic chunking** - улучшение разбиения документов

### Приоритет 3: Долгосрочные улучшения

1. **Learning to Rank** - полноценная модель обучения
2. **Multi-stage retrieval** - сложная система поиска
3. **Query decomposition** - интеллектуальная декомпозиция запросов

### Метрики для оценки

- **Precision@K** - точность топ-K результатов
- **Recall@K** - полнота топ-K результатов
- **MRR (Mean Reciprocal Rank)** - средний обратный ранг первого релевантного результата
- **NDCG (Normalized Discounted Cumulative Gain)** - нормализованный накопленный дисконтированный выигрыш
- **Время выполнения** - производительность поиска

### A/B тестирование

Рекомендуется внедрить A/B тестирование для сравнения различных подходов:

```python
class ABTestManager:
    """Менеджер A/B тестирования."""
    
    def __init__(self):
        self.variants = {
            'control': {'alpha': 0.7, 'rerank': False},
            'variant_a': {'alpha': 0.8, 'rerank': True},
            'variant_b': {'alpha': 0.6, 'rerank': True, 'query_expansion': True},
        }
    
    def get_variant(self, user_id: str) -> str:
        """Получение варианта для пользователя."""
        # Простое хеширование для стабильности
        hash_val = hash(user_id) % 100
        if hash_val < 33:
            return 'control'
        elif hash_val < 66:
            return 'variant_a'
        else:
            return 'variant_b'
```

## Оптимизация для агентных сценариев

### Особенности работы с агентами

При использовании obsidian-kb через MCP с Claude, Cursor и другими агентами возникают специфические требования:

1. **Агенты генерируют запросы** - запросы могут быть менее точными, но более контекстными
2. **Агенты обрабатывают результаты** - результаты используются для RAG (Retrieval-Augmented Generation)
3. **Множественные запросы** - агенты могут делать последовательные уточняющие запросы
4. **Скорость важна** - быстрый ответ критичен для интерактивности

### Рекомендации для агентных сценариев

#### 1. Настройка оптимизатора для агентов

```python
# Оптимальная конфигурация для агентов
optimizer = SearchOptimizer(
    embedding_service=embedding_service,
    db_manager=db_manager,
    enable_rerank=True,  # Важно для точности топ-K
    enable_query_expansion=False,  # Может замедлить, агенты сами уточняют
    enable_feature_ranking=True,  # Быстро и эффективно
)

# Использование с адаптивным alpha
results = await optimizer.optimize_search(
    vault_name=vault_name,
    query=query,
    query_vector=query_embedding,
    limit=10,  # Для агентов достаточно 5-10 результатов
    adaptive_alpha=True,  # Адаптация под тип запроса
)
```

#### 2. Query Normalization для агентов

Агенты могут использовать служебные слова, которые нужно убрать:

```python
def normalize_agent_query(query: str) -> str:
    """Нормализация запроса от агента."""
    # Паттерны, которые агенты часто добавляют
    patterns = [
        r"найди\s+",
        r"найти\s+",
        r"покажи\s+",
        r"ищи\s+",
        r"find\s+",
        r"search\s+for\s+",
        r"show\s+me\s+",
        r"что\s+написано\s+про\s+",
        r"информация\s+о\s+",
        r"расскажи\s+про\s+",
    ]
    
    normalized = query
    for pattern in patterns:
        normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE)
    
    return normalized.strip()
```

#### 3. Контекстное извлечение для RAG

Для RAG важно извлекать не только релевантные чанки, но и контекст:

```python
async def retrieve_with_context_for_rag(
    db_manager: LanceDBManager,
    vault_name: str,
    query: str,
    limit: int = 5,
    context_window: int = 1  # Один соседний чанк с каждой стороны
) -> list[SearchResult]:
    """Извлечение с контекстом для RAG."""
    
    # Обычный поиск
    results = await db_manager.hybrid_search(...)
    
    # Добавляем контекст к каждому результату
    enriched = []
    for result in results:
        # Получаем соседние чанки того же файла
        context = await get_surrounding_chunks(
            db_manager, vault_name, result, context_window
        )
        
        # Объединяем: контекст -> результат -> контекст
        enriched_content = f"{context}\n\n{result.content}\n\n{context}"
        
        enriched.append(
            SearchResult(
                **{**result.__dict__, 'content': enriched_content}
            )
        )
    
    return enriched
```

#### 4. Оптимизация формата для агентов

Текущий формат markdown хорош, но можно улучшить структуру:

```python
def format_for_agent_rag(
    results: list[SearchResult],
    query: str,
    include_full_content: bool = False
) -> str:
    """Форматирование результатов для RAG агентов.
    
    Args:
        include_full_content: Если True, возвращает полный контент
    """
    if not results:
        return f"## Результаты поиска: \"{query}\"\n\n*Результаты не найдены*"
    
    lines = [f"## Результаты поиска: \"{query}\"\n"]
    
    for idx, result in enumerate(results, 1):
        lines.append(f"### Документ {idx}: {result.title}")
        lines.append(f"**Файл:** `{result.file_path}`")
        lines.append(f"**Релевантность:** {result.score:.3f}")
        
        if result.tags:
            lines.append(f"**Теги:** {', '.join(result.tags)}")
        
        lines.append("")
        
        # Контент (полный для RAG или превью)
        if include_full_content:
            lines.append(f"**Содержание:**\n{result.content}")
        else:
            preview = result.content[:400] + "..." if len(result.content) > 400 else result.content
            lines.append(f"**Превью:**\n{preview}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    lines.append(f"*Найдено {len(results)} результатов*")
    
    return "\n".join(lines)
```

#### 5. Кэширование для множественных запросов

Агенты часто делают похожие запросы. Кэширование помогает:

```python
from functools import lru_cache
import hashlib

class AgentQueryCache:
    """Кэш для агентных запросов."""
    
    def __init__(self, max_size: int = 100):
        self.cache: dict[str, list[SearchResult]] = {}
        self.max_size = max_size
    
    def _cache_key(self, vault_name: str, query: str) -> str:
        """Генерация ключа кэша."""
        key_str = f"{vault_name}::{query.lower().strip()}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get_or_search(
        self,
        vault_name: str,
        query: str,
        search_func: Callable
    ) -> list[SearchResult]:
        """Получить из кэша или выполнить поиск."""
        key = self._cache_key(vault_name, query)
        
        if key in self.cache:
            logger.debug(f"Cache hit for query: {query[:50]}")
            return self.cache[key]
        
        # Выполняем поиск
        results = await search_func()
        
        # Сохраняем в кэш
        if len(self.cache) >= self.max_size:
            # Удаляем самый старый
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = results
        return results
```

### Метрики для агентных сценариев

Важно отслеживать специфические метрики:

```python
@dataclass
class AgentSearchMetrics:
    """Метрики для агентных запросов."""
    query: str
    vault_name: str
    result_count: int
    execution_time_ms: float
    agent_type: str  # "claude", "cursor", etc.
    query_normalized: bool  # Была ли нормализация
    cache_hit: bool  # Попадание в кэш
    rerank_applied: bool  # Применён ли re-ranking
```

### Рекомендации по настройке

#### Для Claude Desktop

```python
# Оптимальная конфигурация
settings.enable_search_optimizer = True
settings.enable_rerank = True  # Важно для качества
settings.enable_query_expansion = False  # Claude сам уточняет
settings.enable_feature_ranking = True
settings.adaptive_alpha = True
```

#### Для Cursor IDE

```python
# Более быстрая конфигурация (важна скорость)
settings.enable_search_optimizer = True
settings.enable_rerank = False  # Можно отключить для скорости
settings.enable_query_expansion = False
settings.enable_feature_ranking = True
settings.adaptive_alpha = True
```

### Интеграция с MCP сервером

Пример обновления `mcp_server.py`:

```python
from obsidian_kb.search_optimizer_integration import optimized_search

@mcp.tool()
async def search_vault(vault_name: str, query: str, limit: int = 10, search_type: str = "hybrid") -> str:
    """Поиск в Obsidian vault (оптимизирован для агентов)."""
    
    # Нормализация агентного запроса
    normalized_query = normalize_agent_query(query)
    
    # Использование оптимизатора если включен
    if settings.enable_search_optimizer:
        query_embedding = await embedding_service.get_embedding(normalized_query)
        results = await optimized_search(
            db_manager=db_manager,
            embedding_service=embedding_service,
            vault_name=vault_name,
            query=normalized_query,
            limit=limit,
            search_type=search_type,
            use_optimizer=True,
        )
    else:
        # Стандартный поиск
        results = await db_manager.hybrid_search(...)
    
    # Форматирование для агента
    return format_for_agent_rag(results, query, include_full_content=False)
```

## Заключение

Предложенные улучшения можно внедрять постепенно, начиная с простых и переходя к более сложным. Важно собирать метрики и обратную связь для непрерывного улучшения качества поиска.

**Особое внимание** следует уделить оптимизации для агентных сценариев, так как:
- Агенты генерируют запросы автоматически
- Результаты используются для RAG генерации
- Скорость ответа критична для интерактивности
- Множественные запросы требуют эффективного кэширования

