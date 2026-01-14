"""Стратегия поиска на уровне документов."""

import asyncio
import hashlib
import logging
import time
from typing import TYPE_CHECKING, Any

from obsidian_kb.search.strategies.base import BaseSearchStrategy
from obsidian_kb.types import DocumentSearchResult, RelevanceScore

if TYPE_CHECKING:
    from obsidian_kb.interfaces import IChunkRepository, IDocumentRepository

logger = logging.getLogger(__name__)

# ОПТИМИЗАЦИЯ: Кэш для часто используемых SQL предфильтраций
# Простой LRU-подобный кэш с ограничением размера
_sql_prefilter_cache: dict[str, set[str]] = {}
_cache_max_size = 100  # Максимальное количество записей в кэше


def _get_cache_key(vault_name: str, keywords: frozenset[str], procedural_keywords: frozenset[str] | None) -> str:
    """Генерация ключа кэша для SQL предфильтрации."""
    key_parts = [vault_name]
    key_parts.extend(sorted(keywords))
    if procedural_keywords:
        key_parts.extend(sorted(procedural_keywords))
    key_str = "|".join(key_parts)
    return hashlib.md5(key_str.encode()).hexdigest()


def _get_cached_prefilter(cache_key: str) -> set[str] | None:
    """Получение результата из кэша."""
    return _sql_prefilter_cache.get(cache_key)


def _set_cached_prefilter(cache_key: str, result: set[str]) -> None:
    """Сохранение результата в кэш с ограничением размера."""
    global _sql_prefilter_cache
    # Если кэш переполнен, удаляем старые записи (FIFO)
    if len(_sql_prefilter_cache) >= _cache_max_size:
        # Удаляем первую запись (старейшую)
        first_key = next(iter(_sql_prefilter_cache))
        del _sql_prefilter_cache[first_key]
    _sql_prefilter_cache[cache_key] = result


class DocumentLevelStrategy(BaseSearchStrategy):
    """Стратегия поиска, возвращающая полные документы.
    
    Используется для:
    - Запросов только с метаданными (tags, type, dates)
    - Known-item запросов
    - Procedural запросов (возвращает полный документ)
    """

    def __init__(
        self,
        document_repo: "IDocumentRepository",
        chunk_repo: "IChunkRepository | None" = None,
    ) -> None:
        """Инициализация стратегии.
        
        Args:
            document_repo: Репозиторий документов
            chunk_repo: Репозиторий чанков (опционально, для текстового поиска)
        """
        super().__init__(document_repo)
        self._chunks = chunk_repo

    @property
    def name(self) -> str:
        """Имя стратегии."""
        return "document_level"

    async def search(
        self,
        vault_name: str,
        query: str,
        parsed_filters: dict[str, Any],
        limit: int = 10,
        options: dict[str, Any] | None = None,
    ) -> list[DocumentSearchResult]:
        """Выполнение поиска на уровне документов.
        
        Args:
            vault_name: Имя vault'а
            query: Текстовый запрос (может быть пустым для metadata-only запросов)
            parsed_filters: Извлечённые фильтры
            limit: Максимум результатов
            options: Дополнительные опции (include_content, max_content_length)
        """
        options = options or {}
        include_content = options.get("include_content", True)
        max_content_length = options.get("max_content_length", 10000)
        
        try:
            start_time = time.time()
            # 1. Получаем document_ids через фильтры
            filter_time_start = time.time()
            document_ids = await self._apply_filters(vault_name, parsed_filters)
            filter_time = (time.time() - filter_time_start) * 1000
            
            # 2. Обработка текстового запроса
            if query and query.strip():
                if self._chunks:
                    if document_ids:
                        # Смешанный запрос: фильтры + текст
                        # Выполняем FTS поиск среди документов, отфильтрованных по фильтрам
                        chunk_results = await self._chunks.fts_search(
                            vault_name, query, limit=limit * 3, filter_document_ids=document_ids
                        )
                        
                        # Группируем FTS результаты по документам
                        doc_ids_from_fts = set()
                        if chunk_results:
                            for chunk_result in chunk_results:
                                doc_ids_from_fts.add(chunk_result.chunk.document_id)
                            logger.debug(f"FTS search with filters found {len(doc_ids_from_fts)} documents for query: {query}")
                        
                        # Также проверяем метаданные (title, properties) для документов, отфильтрованных по фильтрам
                        # Это важно для случаев, когда запрос ищет имя человека, которое может быть только в title/properties
                        query_lower = query.lower().strip()
                        matching_doc_ids_from_metadata = set()
                        person_doc_ids = set()  # Документы с type:person для приоритизации
                        
                        # Получаем документы для проверки метаданных
                        docs_to_check = await self._documents.get_many(vault_name, document_ids)
                        
                        # ОПТИМИЗАЦИЯ: Батчинг для получения свойств документов
                        doc_ids_to_check = [doc.document_id for doc in docs_to_check]
                        properties_map_check: dict[str, dict[str, Any]] = {}
                        
                        batch_size_check = 20
                        for i in range(0, len(doc_ids_to_check), batch_size_check):
                            batch_ids_check = doc_ids_to_check[i:i + batch_size_check]
                            
                            tasks_check = [
                                self._documents.get_properties(vault_name, doc_id)
                                for doc_id in batch_ids_check
                            ]
                            
                            batch_results_check = await asyncio.gather(*tasks_check, return_exceptions=True)
                            
                            for idx, doc_id in enumerate(batch_ids_check):
                                props_result_check = batch_results_check[idx]
                                if isinstance(props_result_check, Exception):
                                    logger.debug(f"Error getting properties for {doc_id}: {props_result_check}")
                                    properties_map_check[doc_id] = {}
                                else:
                                    properties_map_check[doc_id] = props_result_check if isinstance(props_result_check, dict) else {}
                        
                        for doc in docs_to_check:
                            # Используем свойства из батча
                            properties = properties_map_check.get(doc.document_id, {})
                            
                            # Проверяем, является ли документ профилем человека
                            is_person = properties.get("type") == "person"
                            if is_person:
                                person_doc_ids.add(doc.document_id)
                            
                            # Проверяем title (особенно важно для профилей людей)
                            if doc.title:
                                title_lower = doc.title.lower()
                                if query_lower in title_lower:
                                    matching_doc_ids_from_metadata.add(doc.document_id)
                                    # Для профилей людей проверяем точное совпадение имени/фамилии
                                    if is_person:
                                        # Разбиваем запрос и title на слова для проверки совпадения имен
                                        query_words = set(query_lower.split())
                                        title_words = set(title_lower.split())
                                        # Если хотя бы одно слово из запроса совпадает с title, это хорошее совпадение
                                        if query_words & title_words:
                                            person_doc_ids.add(doc.document_id)
                                    continue
                            
                            # Проверяем file_path
                            if doc.file_path and query_lower in doc.file_path.lower():
                                matching_doc_ids_from_metadata.add(doc.document_id)
                                continue
                            
                            # Проверяем properties (name, role, title и т.д.)
                            try:
                                for prop_key, prop_value in properties.items():
                                    if isinstance(prop_value, str):
                                        prop_lower = prop_value.lower()
                                        # Для профилей людей проверяем точное совпадение в name, role, title
                                        if is_person and prop_key in ["name", "role", "title"]:
                                            if query_lower in prop_lower or any(word in prop_lower for word in query_lower.split()):
                                                matching_doc_ids_from_metadata.add(doc.document_id)
                                                person_doc_ids.add(doc.document_id)
                                                break
                                        elif query_lower in prop_lower:
                                            matching_doc_ids_from_metadata.add(doc.document_id)
                                            break
                                    elif isinstance(prop_value, list):
                                        for item in prop_value:
                                            if isinstance(item, str) and query_lower in item.lower():
                                                matching_doc_ids_from_metadata.add(doc.document_id)
                                                if is_person:
                                                    person_doc_ids.add(doc.document_id)
                                                break
                            except Exception as e:
                                logger.debug(f"Error checking properties for {doc.document_id}: {e}")
                        
                        # Объединяем результаты FTS и метаданных
                        # Сохраняем информацию о том, какие документы найдены через метаданные для приоритизации
                        document_ids = doc_ids_from_fts | matching_doc_ids_from_metadata
                        
                        if matching_doc_ids_from_metadata:
                            logger.debug(f"Metadata search found {len(matching_doc_ids_from_metadata)} additional documents for query: {query}")
                        
                        if person_doc_ids:
                            logger.debug(f"Found {len(person_doc_ids)} person profiles matching query: {query}")
                        
                        # Для PROCEDURAL запросов дополнительно ищем документы с релевантными названиями
                        # даже если они не найдены через FTS или метаданные
                        import re
                        procedural_keywords = {"guide", "template", "шаблон", "гайд", "инструкция", "how", "как"}
                        query_words_set = set(query_lower.split()) if query_lower else set()
                        has_procedural_keywords_check = bool(query_words_set & procedural_keywords)
                        
                        if has_procedural_keywords_check and query_words_set and document_ids:
                            # ОПТИМИЗАЦИЯ: Для смешанных запросов проверяем только уже найденные документы
                            # (не нужно получать все документы vault'а, так как уже есть фильтры)
                            docs_to_check_procedural = await self._documents.get_many(vault_name, document_ids)
                            content_keywords_check = query_words_set - procedural_keywords
                            relevant_doc_ids_procedural = set()
                            
                            for doc in docs_to_check_procedural:
                                title_lower_check = (doc.title or "").lower()
                                file_path_lower_check = (doc.file_path or "").lower()
                                file_name_check = file_path_lower_check.split('/')[-1] if '/' in file_path_lower_check else file_path_lower_check
                                file_name_without_ext_check = file_name_check.rsplit('.', 1)[0] if '.' in file_name_check else file_name_check
                                
                                # Нормализуем названия
                                file_name_normalized_check = file_name_without_ext_check.replace("-", " ").replace("_", " ")
                                file_name_words_check = set(file_name_normalized_check.split())
                                title_words_check = set(title_lower_check.split())
                                file_name_normalized_lower_check = file_name_normalized_check.lower()
                                file_path_normalized_check = file_path_lower_check.replace("-", " ").replace("_", " ")
                                
                                # Проверяем совпадение ключевых слов
                                matched_check = False
                                if content_keywords_check:
                                    # Проверяем точное совпадение слов
                                    if content_keywords_check & file_name_words_check or content_keywords_check & title_words_check:
                                        matched_check = True
                                    # Проверяем частичное совпадение
                                    for keyword in content_keywords_check:
                                        keyword_normalized = keyword.replace("-", " ")
                                        if (keyword in file_name_normalized_lower_check or 
                                            keyword_normalized in file_name_normalized_lower_check or
                                            keyword in file_path_normalized_check or
                                            keyword in title_lower_check or
                                            keyword in file_name_without_ext_check.lower() or
                                            keyword.replace("-", "_") in file_name_without_ext_check.lower()):
                                            matched_check = True
                                            break
                                    # Дополнительная проверка для ключевых слов с дефисами
                                    for keyword in content_keywords_check:
                                        if "-" in keyword:
                                            keyword_underscore = keyword.replace("-", "_")
                                            if (keyword_underscore in file_name_without_ext_check.lower() or
                                                keyword_underscore in file_path_lower_check):
                                                matched_check = True
                                                break
                                
                                # Если есть совпадение ключевых слов и procedural keywords в названии
                                if matched_check:
                                    if (procedural_keywords & file_name_words_check or 
                                        procedural_keywords & title_words_check or
                                        any(kw in file_name_normalized_lower_check for kw in procedural_keywords) or
                                        any(kw in title_lower_check for kw in procedural_keywords)):
                                        relevant_doc_ids_procedural.add(doc.document_id)
                                        logger.debug(f"Found relevant PROCEDURAL document by name (with filters): {doc.file_path}")
                            
                            # Сохраняем информацию о релевантных документах для сортировки
                            if relevant_doc_ids_procedural:
                                if not hasattr(self, '_temp_procedural_relevant_doc_ids'):
                                    self._temp_procedural_relevant_doc_ids = set()
                                self._temp_procedural_relevant_doc_ids.update(relevant_doc_ids_procedural)
                                logger.debug(f"Added {len(relevant_doc_ids_procedural)} relevant PROCEDURAL documents by name (with filters)")
                        
                        if not document_ids:
                            logger.debug(f"No matches found in text or metadata for query: {query} among {len(document_ids)} filtered documents")
                            return []
                        
                        # Сохраняем информацию о метаданных совпадениях и профилях людей для сортировки результатов
                        # (будет использовано при создании результатов)
                        metadata_matches = matching_doc_ids_from_metadata
                        self._temp_person_doc_ids = person_doc_ids
                    else:
                        # Только текстовый запрос, без фильтров
                        # Для KNOWN_ITEM запросов (например, "README.md") сначала проверяем точное совпадение имени файла
                        # Также проверяем профили людей для запросов типа "Имя Фамилия"
                        query_lower = query.lower().strip()
                        exact_filename_matches = set()
                        person_doc_ids = set()  # Профили людей для приоритизации
                        
                        # Проверяем, является ли запрос KNOWN_ITEM (по паттернам)
                        import re
                        # Паттерны для KNOWN_ITEM (из IntentDetector)
                        FILE_PATTERNS = [
                            r'^[A-Za-z0-9_-]+\.(md|txt|pdf|docx?)$',  # README.md, file.txt
                            r'^[A-Z]{2,}-\d+$',  # ADR-001, PROJ-123
                            r'^[a-z]+-[a-z]+$',  # smrm-ecosystem
                        ]
                        ID_PATTERN = r'\b[A-Za-z]{2,}-\d+\b'  # ADR-001, adr-001, PROJ-123
                        
                        is_known_item_query = (
                            any(re.search(p, query, re.IGNORECASE) for p in FILE_PATTERNS) or
                            re.search(ID_PATTERN, query) or
                            # Проверяем, похож ли запрос на ID (только буквы и дефисы, без пробелов)
                            (len(query.split()) == 1 and re.match(r'^[a-z0-9_-]+$', query_lower))
                        )
                        
                        # ОПТИМИЗАЦИЯ: Раннее определение процедурных запросов для оптимизации
                        procedural_keywords = {"guide", "template", "шаблон", "гайд", "инструкция", "how", "как"}
                        query_words = set(query_lower.split()) if query_lower else set()
                        has_procedural_keywords = bool(query_words & procedural_keywords)
                        
                        # ОПТИМИЗАЦИЯ: Используем прямой поиск по имени файла вместо медленного FTS поиска
                        # Для KNOWN_ITEM запросов сначала проверяем точное совпадение имени файла
                        if is_known_item_query:
                            # Точный поиск по имени файла
                            exact_filename_matches = await self._documents.find_by_filename(
                                vault_name, query, exact_match=True
                            )
                            logger.debug(f"Filename search (optimized) found {len(exact_filename_matches)} documents for query: {query}")
                            
                            # Для KNOWN_ITEM запросов, если точного совпадения нет, не делаем fallback
                            # Возвращаем пустой результат сразу
                            if not exact_filename_matches:
                                logger.debug(f"KNOWN_ITEM query '{query}' did not find exact match, returning empty results")
                                document_ids = set()
                                return []
                        
                        # Для проверки профилей людей и не-KNOWN_ITEM запросов получаем все документы
                        # ОПТИМИЗАЦИЯ: Используем прямой запрос к таблице documents вместо FTS поиска
                        # Проверяем только если не нашли точного совпадения для KNOWN_ITEM или это не KNOWN_ITEM запрос
                        if not exact_filename_matches:
                            all_doc_ids = await self._documents.get_all_document_ids(vault_name)
                            
                            if all_doc_ids:
                                docs_to_check = await self._documents.get_many(vault_name, all_doc_ids)
                                
                                # ОПТИМИЗАЦИЯ: Батчинг для получения свойств документов
                                doc_ids_to_check_person = [doc.document_id for doc in docs_to_check]
                                properties_map_person: dict[str, dict[str, Any]] = {}
                                
                                batch_size_person = 20
                                for i in range(0, len(doc_ids_to_check_person), batch_size_person):
                                    batch_ids_person = doc_ids_to_check_person[i:i + batch_size_person]
                                    
                                    tasks_person = [
                                        self._documents.get_properties(vault_name, doc_id)
                                        for doc_id in batch_ids_person
                                    ]
                                    
                                    batch_results_person = await asyncio.gather(*tasks_person, return_exceptions=True)
                                    
                                    for idx, doc_id in enumerate(batch_ids_person):
                                        props_result_person = batch_results_person[idx]
                                        if isinstance(props_result_person, Exception):
                                            logger.debug(f"Error getting properties for {doc_id}: {props_result_person}")
                                            properties_map_person[doc_id] = {}
                                        else:
                                            properties_map_person[doc_id] = props_result_person if isinstance(props_result_person, dict) else {}
                                
                                for doc in docs_to_check:
                                    # Для не-KNOWN_ITEM запросов проверяем частичное совпадение имени файла
                                    if not is_known_item_query:
                                        file_name = doc.file_path.split('/')[-1] if '/' in doc.file_path else doc.file_path
                                        file_name_lower = file_name.lower()
                                        if query_lower in file_name_lower:
                                            exact_filename_matches.add(doc.document_id)
                                            logger.debug(f"Partial filename match: {doc.file_path} matches {query}")
                                    
                                    # Используем свойства из батча
                                    properties = properties_map_person.get(doc.document_id, {})
                                    
                                    # Проверяем, является ли документ профилем человека
                                    try:
                                        if properties.get("type") == "person":
                                            # Проверяем совпадение имени/фамилии в title и properties
                                            if doc.title:
                                                title_lower = doc.title.lower()
                                                query_words = set(query_lower.split())
                                                title_words = set(title_lower.split())
                                                # Если хотя бы одно слово из запроса совпадает с title, это профиль человека
                                                if query_words & title_words:
                                                    person_doc_ids.add(doc.document_id)
                                            
                                            # Проверяем properties (name, role)
                                            for prop_key in ["name", "role", "title"]:
                                                prop_value = properties.get(prop_key)
                                                if isinstance(prop_value, str):
                                                    prop_lower = prop_value.lower()
                                                    if query_lower in prop_lower or any(word in prop_lower for word in query_lower.split()):
                                                        person_doc_ids.add(doc.document_id)
                                                        break
                                    except Exception as e:
                                        logger.debug(f"Error checking person properties for {doc.document_id}: {e}")
                        
                        if exact_filename_matches:
                            document_ids = exact_filename_matches
                            logger.debug(f"Filename search found {len(document_ids)} documents for query: {query}")
                        elif person_doc_ids:
                            # Если найдены профили людей, используем их
                            document_ids = person_doc_ids
                            self._temp_person_doc_ids = person_doc_ids
                            logger.debug(f"Person profile search found {len(document_ids)} documents for query: {query}")
                        elif is_known_item_query:
                            # Для KNOWN_ITEM запросов, если точного совпадения нет, не делаем fallback
                            # Возвращаем пустой результат
                            logger.debug(f"KNOWN_ITEM query '{query}' did not find exact match, returning empty results")
                            document_ids = set()
                        elif has_procedural_keywords:
                            # ОПТИМИЗАЦИЯ: Для процедурных запросов пропускаем FTS поиск
                            # и сразу переходим к проверке документов по названиям
                            # Это значительно ускоряет процедурные запросы, так как для них важнее названия
                            logger.debug(f"PROCEDURAL query detected, skipping FTS search and checking documents by name: {query}")
                            document_ids = set()
                        else:
                            # Fallback на FTS поиск по контенту (только для не-KNOWN_ITEM и не-процедурных запросов)
                            chunk_results = await self._chunks.fts_search(
                                vault_name, query, limit=limit * 3
                            )
                            doc_ids_from_chunks = set()
                            if chunk_results:
                                # Группируем по документам
                                for chunk_result in chunk_results:
                                    doc_ids_from_chunks.add(chunk_result.chunk.document_id)
                                logger.debug(f"FTS search found {len(doc_ids_from_chunks)} documents for query: {query}")
                            
                            # Инициализируем document_ids с результатами FTS (если есть)
                            document_ids = doc_ids_from_chunks.copy() if doc_ids_from_chunks else set()
                        
                        # Для PROCEDURAL запросов всегда проверяем все документы vault'а по названиям
                        # Это важно, так как релевантные документы могут не попасть в FTS результаты
                        # ОПТИМИЗАЦИЯ: Используем SQL-запросы для предварительной фильтрации документов
                        if has_procedural_keywords and query_words:
                            content_keywords = query_words - procedural_keywords
                            
                            # ОПТИМИЗАЦИЯ: Используем SQL-запросы для предварительной фильтрации
                            # Это значительно сокращает количество документов, которые нужно проверять
                            if content_keywords:
                                # ОПТИМИЗАЦИЯ: Проверяем кэш перед выполнением SQL-запроса
                                cache_key = _get_cache_key(vault_name, frozenset(content_keywords), 
                                                           frozenset(procedural_keywords) if procedural_keywords else None)
                                cached_result = _get_cached_prefilter(cache_key)
                                
                                if cached_result is not None:
                                    logger.debug(f"Using cached SQL prefiltering result ({len(cached_result)} documents) for PROCEDURAL query: {query}")
                                    prefiltered_doc_ids = cached_result
                                else:
                                    # Предварительно фильтруем документы через SQL-запросы
                                    # Используем OR логику для более широкой фильтрации, затем уточняем в Python
                                    # ОПТИМИЗАЦИЯ: Добавляем LIMIT для ограничения количества результатов на уровне SQL
                                    # Используем limit * 1.8 для процедурных запросов (баланс между точностью и покрытием)
                                    sql_limit = int(limit * 1.8) if limit else None
                                    prefiltered_doc_ids = await self._documents.find_by_keywords_in_name(
                                        vault_name, content_keywords, procedural_keywords, 
                                        require_all_keywords=False, limit=sql_limit
                                    )
                                    # Сохраняем результат в кэш
                                    _set_cached_prefilter(cache_key, prefiltered_doc_ids)
                                    logger.debug(f"SQL prefiltering (OR logic, limit={sql_limit}) found {len(prefiltered_doc_ids)} documents for PROCEDURAL query: {query}")
                            else:
                                # Если нет content_keywords, используем все документы
                                prefiltered_doc_ids = await self._documents.get_all_document_ids(vault_name)
                            
                            if prefiltered_doc_ids:
                                # ОПТИМИЗАЦИЯ: Получаем документы батчами для проверки названий
                                # Это позволяет обрабатывать документы постепенно и не загружать все в память сразу
                                relevant_doc_ids = set()
                                
                                # Размер батча для проверки документов по названиям
                                # ОПТИМИЗАЦИЯ: Уменьшен размер батча для более быстрой обработки первых результатов
                                name_check_batch_size = 50
                                prefiltered_doc_ids_list = list(prefiltered_doc_ids)
                                
                                # ОПТИМИЗАЦИЯ: Раннее прерывание при достаточном количестве результатов
                                # Для процедурных запросов достаточно найти limit * 2 документов для сортировки
                                max_relevant_docs = limit * 2 if limit else None
                                
                                for i in range(0, len(prefiltered_doc_ids_list), name_check_batch_size):
                                    # ОПТИМИЗАЦИЯ: Прерываем цикл, если уже нашли достаточно релевантных документов
                                    if max_relevant_docs and len(relevant_doc_ids) >= max_relevant_docs:
                                        logger.debug(f"Early exit: found {len(relevant_doc_ids)} relevant documents (target: {max_relevant_docs})")
                                        break
                                    
                                    batch_doc_ids = set(prefiltered_doc_ids_list[i:i + name_check_batch_size])
                                    # ОПТИМИЗАЦИЯ: Для процедурных запросов используем get_many_metadata_only
                                    # Это быстрее, так как не нужно получать свойства документов на этапе проверки по названиям
                                    if hasattr(self._documents, 'get_many_metadata_only'):
                                        docs_to_check = await self._documents.get_many_metadata_only(vault_name, batch_doc_ids)
                                    else:
                                        docs_to_check = await self._documents.get_many(vault_name, batch_doc_ids)
                                    
                                    for doc in docs_to_check:
                                        # ОПТИМИЗАЦИЯ: FTS уже выполнил предварительную фильтрацию
                                        # Упрощенная проверка в Python - FTS нашел релевантные документы
                                        # Проверяем только наличие ключевых слов для уточнения
                                        
                                        title_lower = (doc.title or "").lower()
                                        file_path_lower = (doc.file_path or "").lower()
                                        file_name = file_path_lower.split('/')[-1] if '/' in file_path_lower else file_path_lower
                                        file_name_without_ext = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
                                        
                                        # Нормализуем названия для проверки
                                        file_name_normalized = file_name_without_ext.replace("-", " ").replace("_", " ").lower()
                                        
                                        # ОПТИМИЗАЦИЯ: Упрощенная проверка - FTS уже нашел релевантные документы
                                        # Проверяем только наличие ключевых слов для подтверждения
                                        is_relevant = False
                                        
                                        # Проверяем наличие procedural keywords
                                        has_procedural = False
                                        if procedural_keywords:
                                            has_procedural = (
                                                any(kw in title_lower for kw in procedural_keywords) or
                                                any(kw in file_name_normalized for kw in procedural_keywords) or
                                                any(kw in file_path_lower for kw in procedural_keywords)
                                            )
                                        
                                        # Проверяем наличие content keywords
                                        has_content = False
                                        if content_keywords:
                                            has_content = (
                                                any(kw in title_lower for kw in content_keywords) or
                                                any(kw in file_name_normalized for kw in content_keywords) or
                                                any(kw in file_path_lower for kw in content_keywords)
                                            )
                                        
                                        # Документ релевантен если:
                                        # 1. Есть procedural keywords в названии ИЛИ
                                        # 2. Есть content keywords в названии (FTS уже проверил, но подтверждаем)
                                        is_relevant = has_procedural or has_content
                                        
                                        if is_relevant:
                                            relevant_doc_ids.add(doc.document_id)
                                            logger.debug(f"Found relevant PROCEDURAL document by name (FTS filtered): {doc.file_path}")
                                            
                                            # ОПТИМИЗАЦИЯ: Раннее прерывание внутреннего цикла при достаточном количестве результатов
                                            if max_relevant_docs and len(relevant_doc_ids) >= max_relevant_docs:
                                                break
                                
                                # Добавляем релевантные документы в результаты
                                if relevant_doc_ids:
                                    # Объединяем с результатами FTS (если есть)
                                    document_ids = document_ids | relevant_doc_ids
                                    # Сохраняем информацию о релевантных документах для сортировки
                                    if not hasattr(self, '_temp_procedural_relevant_doc_ids'):
                                        self._temp_procedural_relevant_doc_ids = set()
                                    self._temp_procedural_relevant_doc_ids.update(relevant_doc_ids)
                                    logger.debug(f"Added {len(relevant_doc_ids)} relevant PROCEDURAL documents by name (total: {len(document_ids)})")
                                elif not document_ids:
                                    # Если нет ни FTS результатов, ни релевантных по названиям, document_ids остается пустым
                                    logger.debug(f"No FTS results and no relevant documents by name for PROCEDURAL query: {query}")
                else:
                    if not document_ids:
                        # Есть текстовый запрос, но нет chunk_repo и нет результатов от фильтров
                        logger.warning("Text query provided but no chunk_repo available for FTS search")
                        return []
            
            if not document_ids:
                return []
            
            # 3. Получаем документы
            documents = await self._documents.get_many(vault_name, document_ids)
            
            # 4. Сортируем документы по релевантности:
            # - Профили людей (type:person) - самый высокий приоритет
            # - Документы с релевантными названиями (для PROCEDURAL запросов) - высокий приоритет
            # - Документы, найденные через метаданные (title, properties) - выше
            # - Затем документы, найденные через FTS
            metadata_matches = getattr(self, '_temp_metadata_matches', set())
            person_doc_ids = getattr(self, '_temp_person_doc_ids', set())
            procedural_relevant_doc_ids = getattr(self, '_temp_procedural_relevant_doc_ids', set())
            
            # Для PROCEDURAL запросов определяем релевантные ключевые слова
            query_lower = query.lower().strip() if query else ""
            query_words = set(query_lower.split()) if query_lower else set()
            # Ключевые слова для PROCEDURAL запросов (guide, template, шаблон, гайд, инструкция)
            procedural_keywords = {"guide", "template", "шаблон", "гайд", "инструкция", "how", "как"}
            has_procedural_keywords = bool(query_words & procedural_keywords)
            
            # Извлекаем ключевые слова запроса (исключая procedural keywords для лучшего совпадения)
            content_keywords = query_words - procedural_keywords
            
            def sort_key(doc):
                title_lower = (doc.title or "").lower()
                file_path_lower = (doc.file_path or "").lower()
                file_name = file_path_lower.split('/')[-1] if '/' in file_path_lower else file_path_lower
                file_name_without_ext = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
                
                # Для PROCEDURAL запросов приоритизируем документы с релевантными названиями
                if has_procedural_keywords and query_words:
                    title_words = set(title_lower.split())
                    file_path_words = set(file_path_lower.replace("/", " ").replace("-", " ").replace("_", " ").split())
                    file_name_words = set(file_name_without_ext.replace("-", " ").replace("_", " ").split())
                    file_name_normalized_lower = file_name_without_ext.replace("-", " ").replace("_", " ").lower()
                    file_path_normalized = file_path_lower.replace("-", " ").replace("_", " ")
                    
                    # Документы, найденные по релевантным названиям для PROCEDURAL, получают наивысший приоритет
                    # (даже выше профилей людей для PROCEDURAL запросов)
                    if doc.document_id in procedural_relevant_doc_ids:
                        # Чем больше совпадений ключевых слов, тем выше приоритет
                        matched_keywords_count = 0
                        matched_title_keywords_count = 0
                        all_keywords_matched = True
                        if content_keywords:
                            matched_keywords_count = len(content_keywords & file_name_words)
                            matched_title_keywords_count = len(content_keywords & title_words)
                            # Также проверяем частичное совпадение
                            for keyword in content_keywords:
                                keyword_normalized = keyword.replace("-", " ")
                                keyword_underscore = keyword.replace("-", "_")
                                keyword_matched = (
                                    keyword in file_name_normalized_lower or 
                                    keyword_normalized in file_name_normalized_lower or
                                    keyword in file_path_normalized or
                                    keyword in title_lower or
                                    keyword in file_name_without_ext.lower() or
                                    keyword.replace("-", "_") in file_name_without_ext.lower() or
                                    keyword_underscore in file_name_without_ext.lower()
                                )
                                if keyword_matched:
                                    if keyword not in file_name_words and keyword not in title_words:
                                        matched_keywords_count += 0.5  # Частичное совпадение
                                else:
                                    all_keywords_matched = False
                        
                        # Если все ключевые слова совпадают, это максимальный приоритет
                        if all_keywords_matched and content_keywords:
                            match_score = matched_keywords_count + matched_title_keywords_count + len(content_keywords) * 10
                            return (-1, -match_score, doc.title or "")  # Максимальный приоритет (даже выше профилей людей для PROCEDURAL)
                        
                        match_score = matched_keywords_count + matched_title_keywords_count + len(content_keywords) * 5
                        return (-1, -match_score, doc.title or "")  # Максимальный приоритет для всех документов в procedural_relevant_doc_ids
                    
                    # Проверяем точное совпадение ключевых слов запроса в названии файла (высший приоритет)
                    # Например, для "как создать ADR" ищем "adr" в названии файла
                    if content_keywords:
                        # Проверяем совпадение всех ключевых слов запроса в названии файла
                        matched_keywords = content_keywords & file_name_words
                        matched_title_keywords = content_keywords & title_words
                        
                        # Также проверяем частичное совпадение (для случаев типа "1-1")
                        partial_match = False
                        partial_match_count = 0
                        all_keywords_partial_match = True
                        for keyword in content_keywords:
                            keyword_normalized = keyword.replace("-", " ")
                            keyword_underscore = keyword.replace("-", "_")
                            # Проверяем разные варианты совпадения
                            keyword_matched = (
                                keyword in file_name_normalized_lower or 
                                keyword_normalized in file_name_normalized_lower or
                                keyword in file_path_normalized or
                                keyword in title_lower or
                                keyword in file_name_without_ext.lower() or
                                keyword.replace("-", "_") in file_name_without_ext.lower() or
                                keyword_underscore in file_name_without_ext.lower()
                            )
                            if keyword_matched:
                                partial_match = True
                                partial_match_count += 1
                            else:
                                all_keywords_partial_match = False
                        
                        # Проверяем наличие procedural keywords в названии
                        has_procedural_in_name = (
                            procedural_keywords & file_name_words or 
                            procedural_keywords & title_words or
                            any(kw in file_name_normalized_lower for kw in procedural_keywords) or
                            any(kw in title_lower for kw in procedural_keywords) or
                            any(kw in file_name_without_ext.lower() for kw in procedural_keywords)
                        )
                        
                        # Если все ключевые слова совпадают (хотя бы частично), это очень высокий приоритет
                        if all_keywords_partial_match and partial_match_count == len(content_keywords):
                            if has_procedural_in_name:
                                # Максимальный приоритет для документов с procedural keywords и совпадением всех ключевых слов
                                match_score = len(matched_keywords) + len(matched_title_keywords) + partial_match_count * 10
                                return (-1, -match_score, doc.title or "")  # Максимальный приоритет (даже выше профилей людей для PROCEDURAL)
                            else:
                                # Высокий приоритет для документов с совпадением всех ключевых слов
                                match_score = len(matched_keywords) + len(matched_title_keywords) + partial_match_count * 5
                                return (-1, -match_score, doc.title or "")  # Максимальный приоритет
                        
                        if matched_keywords or matched_title_keywords or partial_match:
                            if has_procedural_in_name:
                                # Чем больше совпадений, тем выше приоритет
                                match_score = len(matched_keywords) + len(matched_title_keywords)
                                if partial_match:
                                    match_score += partial_match_count * 0.5  # Бонус за частичные совпадения
                                return (1, -match_score, doc.title or "")  # Высокий приоритет для PROCEDURAL
                            # Средний приоритет для совпадений ключевых слов
                            match_score = len(matched_keywords) + len(matched_title_keywords)
                            if partial_match:
                                match_score += partial_match_count * 0.5
                            return (2, -match_score, doc.title or "")
                    
                    # Проверяем наличие procedural keywords в названии (даже без совпадения ключевых слов)
                    if (procedural_keywords & file_name_words or 
                        procedural_keywords & title_words or
                        any(kw in file_name_normalized_lower for kw in procedural_keywords) or
                        any(kw in title_lower for kw in procedural_keywords) or
                        any(kw in file_name_without_ext.lower() for kw in procedural_keywords)):
                        return (4, doc.title or "")  # Высокий приоритет для procedural документов
                    
                    # Проверяем частичное совпадение ключевых слов в названии файла
                    if content_keywords:
                        for keyword in content_keywords:
                            if (keyword in file_name_without_ext.lower() or 
                                keyword in title_lower or
                                keyword.replace("-", "_") in file_name_without_ext.lower()):
                                return (5, doc.title or "")  # Средний приоритет для частичных совпадений
                
                # Профили людей получают приоритет (но ниже PROCEDURAL документов)
                if doc.document_id in person_doc_ids:
                    return (1, doc.title or "")
                
                # Документы из метаданных получают приоритет
                if doc.document_id in metadata_matches:
                    return (2, doc.title or "")
                
                # Остальные документы идут после
                return (3, doc.title or "")
            
            documents.sort(key=sort_key)
            
            # Очищаем временные переменные
            if hasattr(self, '_temp_metadata_matches'):
                delattr(self, '_temp_metadata_matches')
            if hasattr(self, '_temp_person_doc_ids'):
                delattr(self, '_temp_person_doc_ids')
            if hasattr(self, '_temp_procedural_relevant_doc_ids'):
                delattr(self, '_temp_procedural_relevant_doc_ids')
            
            # 5. Обогащаем контентом если нужно
            # ОПТИМИЗАЦИЯ: Отложенное получение контента - только для финальных результатов после сортировки
            # Определяем, является ли запрос процедурным
            query_lower_final = query.lower().strip() if query else ""
            query_words_final = set(query_lower_final.split()) if query_lower_final else set()
            procedural_keywords_final = {"guide", "template", "шаблон", "гайд", "инструкция", "how", "как"}
            is_procedural_query = bool(query_words_final & procedural_keywords_final)
            
            # ОПТИМИЗАЦИЯ: Получаем контент только для финальных результатов после сортировки
            # Это значительно ускоряет запросы, так как не нужно получать контент для всех документов
            documents_to_process = documents[:limit]  # Только финальные результаты после сортировки
            logger.debug(f"Processing {len(documents_to_process)} final documents (after sorting) for content and properties")
            
            properties_map: dict[str, dict[str, Any]] = {}
            
            # Получаем свойства батчами только для финальных результатов
            batch_size = 20  # Размер батча для параллельных запросов
            doc_ids_to_process = [doc.document_id for doc in documents_to_process]
            
            for i in range(0, len(doc_ids_to_process), batch_size):
                batch_ids = doc_ids_to_process[i:i + batch_size]
                
                # Параллельно получаем properties для батча
                tasks = [
                    self._documents.get_properties(vault_name, doc_id)
                    for doc_id in batch_ids
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Распределяем результаты
                for idx, doc_id in enumerate(batch_ids):
                    props_result = batch_results[idx]
                    
                    if isinstance(props_result, Exception):
                        logger.warning(f"Error getting properties for {doc_id}: {props_result}")
                        properties_map[doc_id] = {}
                    else:
                        properties_map[doc_id] = props_result if isinstance(props_result, dict) else {}
            
            # ОПТИМИЗАЦИЯ: Отложенное получение контента - только для финальных результатов
            # Контент получается только после сортировки, для финальных результатов
            # Это значительно ускоряет запросы, так как не нужно получать контент для всех документов
            content_map: dict[str, str] = {}
            if include_content:
                # Получаем контент только для финальных результатов (уже отсортированных)
                content_doc_ids = doc_ids_to_process
                logger.debug(f"Getting content for {len(content_doc_ids)} final documents (deferred content loading)")
                
                content_batch_size = 20
                for i in range(0, len(content_doc_ids), content_batch_size):
                    batch_ids_content = content_doc_ids[i:i + content_batch_size]
                    
                    # Параллельно получаем контент для батча
                    content_tasks = [
                        self._documents.get_content(vault_name, doc_id)
                        for doc_id in batch_ids_content
                    ]
                    
                    batch_content_results = await asyncio.gather(*content_tasks, return_exceptions=True)
                    
                    # Распределяем результаты
                    for idx, doc_id in enumerate(batch_ids_content):
                        content_result = batch_content_results[idx]
                        
                        if isinstance(content_result, Exception):
                            logger.warning(f"Error getting content for {doc_id}: {content_result}")
                            content_map[doc_id] = ""
                        else:
                            content_map[doc_id] = content_result if isinstance(content_result, str) else ""
            
            results = []
            for doc in documents_to_process:
                try:
                    if include_content:
                        content = content_map.get(doc.document_id, "")
                        if len(content) > max_content_length:
                            doc.content = content[:max_content_length] + "\n\n[... обрезано ...]"
                            doc.summary = content[:500] if len(content) > 500 else content
                        else:
                            doc.content = content
                        doc.content_length = len(content)
                    
                    # Используем свойства из батча
                    properties = properties_map.get(doc.document_id, {})
                    doc.properties = properties
                    
                    # Извлекаем теги из свойств или metadata
                    if "tags" in properties:
                        tags_value = properties["tags"]
                        if isinstance(tags_value, list):
                            doc.tags = tags_value
                        elif isinstance(tags_value, str):
                            # Если теги в виде строки, парсим
                            doc.tags = [t.strip() for t in tags_value.split(",")]
                    
                    # Создаём результат с exact match score
                    results.append(DocumentSearchResult(
                        document=doc,
                        score=RelevanceScore.exact_match(),
                        matched_chunks=[],
                        matched_sections=[],
                    ))
                except Exception as e:
                    logger.warning(f"Error processing document {doc.document_id}: {e}")
                    continue
            
            total_time = (time.time() - start_time) * 1000
            
            # Логируем детальное время выполнения
            query_preview = query[:50] if query else "metadata_only"
            logger.debug(
                f"[PERF] DocumentLevelStrategy.search('{query_preview}...'): "
                f"total={total_time:.1f}ms, "
                f"filter={filter_time:.1f}ms, "
                f"results={len(results)}"
            )
            
            return results
        except Exception as e:
            logger.error(f"Error in DocumentLevelStrategy.search for vault '{vault_name}': {e}")
            return []

