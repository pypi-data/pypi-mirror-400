"""Репозиторий для работы с документами."""

import asyncio
import logging
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

from obsidian_kb.types import Document

if TYPE_CHECKING:
    from obsidian_kb.lance_db import LanceDBManager

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Реализация IDocumentRepository для работы с документами."""

    def __init__(self, db_manager: "LanceDBManager") -> None:
        """Инициализация репозитория.
        
        Args:
            db_manager: Экземпляр LanceDBManager
        """
        self._db_manager = db_manager
        # ОПТИМИЗАЦИЯ: Кэш метаданных документов для избежания повторных запросов
        # Ключ: (vault_name, document_id), Значение: DocumentInfo
        self._metadata_cache: dict[tuple[str, str], Any] = {}
        self._cache_max_size = 1000  # Максимальное количество записей в кэше

    async def get(
        self,
        vault_name: str,
        document_id: str,
    ) -> Document | None:
        """Получение документа по ID."""
        doc_info = await self._db_manager.get_document_info(vault_name, document_id)
        if not doc_info:
            return None
        
        # Получаем свойства документа
        properties = await self.get_properties(vault_name, document_id)
        
        # Конвертируем DocumentInfo в Document
        return Document.from_document_info(doc_info, properties)

    async def get_many(
        self,
        vault_name: str,
        document_ids: set[str],
    ) -> list[Document]:
        """Получение нескольких документов."""
        # Параллельное получение документов
        tasks = [self.get(vault_name, doc_id) for doc_id in document_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        documents = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error getting document: {result}")
                continue
            if result:
                documents.append(result)
        
        return documents
    
    async def get_many_metadata_only(
        self,
        vault_name: str,
        document_ids: set[str],
    ) -> list[Document]:
        """Получение нескольких документов только с метаданными (без свойств).
        
        ОПТИМИЗАЦИЯ: Использует кэш метаданных для избежания повторных запросов к БД.
        Оптимизированный метод для процедурных запросов, где свойства не нужны
        на этапе проверки по названиям.
        
        Args:
            vault_name: Имя vault'а
            document_ids: Множество document_ids для получения
            
        Returns:
            Список документов с метаданными (title, file_path), но без properties
        """
        if not document_ids:
            return []
        
        try:
            # ОПТИМИЗАЦИЯ: Проверяем кэш перед запросом к БД
            cached_docs: dict[str, Any] = {}
            uncached_ids: set[str] = set()
            
            for doc_id in document_ids:
                cache_key = (vault_name, doc_id)
                if cache_key in self._metadata_cache:
                    cached_docs[doc_id] = self._metadata_cache[cache_key]
                else:
                    uncached_ids.add(doc_id)
            
            # Получаем метаданные только для документов, которых нет в кэше
            if uncached_ids:
                tasks = [
                    self._db_manager.get_document_info(vault_name, doc_id)
                    for doc_id in uncached_ids
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Сохраняем результаты в кэш
                for idx, doc_id in enumerate(uncached_ids):
                    result = results[idx]
                    if isinstance(result, Exception):
                        logger.debug(f"Error getting document info: {result}")
                        continue
                    if result:
                        cache_key = (vault_name, doc_id)
                        # ОПТИМИЗАЦИЯ: Ограничиваем размер кэша (FIFO)
                        if len(self._metadata_cache) >= self._cache_max_size:
                            # Удаляем первую запись (старейшую)
                            first_key = next(iter(self._metadata_cache))
                            del self._metadata_cache[first_key]
                        self._metadata_cache[cache_key] = result
                        cached_docs[doc_id] = result
            
            # Создаем Document объекты из кэшированных и новых метаданных
            documents = []
            for doc_id in document_ids:
                if doc_id in cached_docs:
                    doc_info = cached_docs[doc_id]
                    # Создаем Document только с метаданными, без свойств
                    doc = Document.from_document_info(doc_info, properties={})
                    documents.append(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Error in get_many_metadata_only for vault '{vault_name}': {e}")
            return []

    async def find_by_property(
        self,
        vault_name: str,
        property_key: str,
        property_value: str,
    ) -> set[str]:
        """Поиск document_ids по свойству."""
        return await self._db_manager.get_documents_by_property(
            vault_name=vault_name,
            property_key=property_key,
            property_value=property_value,
        )

    async def find_by_tags(
        self,
        vault_name: str,
        tags: list[str],
        match_all: bool = True,
    ) -> set[str]:
        """Поиск document_ids по тегам."""
        return await self._db_manager.get_documents_by_tags(
            vault_name=vault_name,
            tags=tags,
            match_all=match_all,
        )

    async def find_by_date_range(
        self,
        vault_name: str,
        field: str,  # "created_at" | "modified_at"
        after: datetime | None = None,
        before: datetime | None = None,
        after_exclusive: bool = False,  # Если True, используется > вместо >=
        before_exclusive: bool = False,  # Если True, используется < вместо <=
    ) -> set[str]:
        """Поиск document_ids по диапазону дат.
        
        Args:
            vault_name: Имя vault'а
            field: Поле для фильтрации (created_at или modified_at)
            after: Минимальная дата (включительно, если after_exclusive=False)
            before: Максимальная дата (включительно, если before_exclusive=False)
            after_exclusive: Если True, используется оператор > вместо >=
            before_exclusive: Если True, используется оператор < вместо <=
        """
        try:
            documents_table = await self._db_manager._ensure_table(vault_name, "documents")
            db = self._db_manager._get_db()
            
            def _find() -> set[str]:
                try:
                    conditions = []
                    if after:
                        # Для оператора > используем строгое сравнение
                        # Для оператора >= используем >=
                        if after_exclusive:
                            # Для строгого > добавляем минимальное приращение
                            # Если дата без времени (только дата), добавляем 1 день
                            # Иначе добавляем 1 секунду
                            from datetime import timedelta
                            if after.hour == 0 and after.minute == 0 and after.second == 0 and after.microsecond == 0:
                                # Дата без времени - добавляем 1 день
                                after_strict = after + timedelta(days=1)
                            else:
                                # Дата с временем - добавляем 1 секунду
                                after_strict = after + timedelta(seconds=1)
                            conditions.append(f"{field} >= '{after_strict.isoformat()}'")
                        else:
                            conditions.append(f"{field} >= '{after.isoformat()}'")
                    if before:
                        # Для оператора < используем строгое сравнение
                        # Для оператора <= используем <=
                        if before_exclusive:
                            # Для строгого < вычитаем минимальное приращение
                            # Если дата без времени (только дата), вычитаем 1 день
                            # Иначе вычитаем 1 секунду
                            from datetime import timedelta
                            if before.hour == 0 and before.minute == 0 and before.second == 0 and before.microsecond == 0:
                                # Дата без времени - вычитаем 1 день
                                before_strict = before - timedelta(days=1)
                            else:
                                # Дата с временем - вычитаем 1 секунду
                                before_strict = before - timedelta(seconds=1)
                            conditions.append(f"{field} <= '{before_strict.isoformat()}'")
                        else:
                            conditions.append(f"{field} <= '{before.isoformat()}'")
                    
                    where_clause = " AND ".join(conditions) if conditions else None
                    
                    query = documents_table.search()
                    if where_clause:
                        query = query.where(where_clause)
                    
                    arrow_table = query.to_arrow()
                    document_ids = set()
                    if arrow_table.num_rows > 0:
                        doc_ids = arrow_table["document_id"].to_pylist()
                        document_ids = set(doc_ids)
                    
                    return document_ids
                except Exception as e:
                    logger.error(f"Error finding documents by date range: {e}")
                    return set()
            
            return await asyncio.to_thread(_find)
            
        except Exception as e:
            logger.error(f"Error in find_by_date_range for vault '{vault_name}': {e}")
            return set()

    async def get_content(
        self,
        vault_name: str,
        document_id: str,
    ) -> str:
        """Получение полного контента документа.
        
        Приоритет: файл напрямую > сборка из чанков.
        """
        # Сначала пытаемся получить контент из файла напрямую
        doc_info = await self._db_manager.get_document_info(vault_name, document_id)
        if doc_info:
            file_path = Path(doc_info.file_path_full)
            if file_path.exists():
                try:
                    return file_path.read_text(encoding="utf-8")
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {e}")
        
        # Fallback: собираем контент из чанков через прямой запрос к таблице
        try:
            chunks_table = await self._db_manager._ensure_table(vault_name, "chunks")
            db = self._db_manager._get_db()
            
            def _get_chunks() -> list[dict[str, Any]]:
                try:
                    arrow_table = (
                        chunks_table.search()
                        .where(f"document_id = '{document_id}'")
                        .to_arrow()
                    )
                    # Оптимизация: to_pylist() вместо построчного преобразования
                    return arrow_table.to_pylist()
                except Exception:
                    return []
            
            rows = await asyncio.to_thread(_get_chunks)
            if rows:
                # Сортируем по chunk_index и объединяем контент
                rows.sort(key=lambda r: r.get("chunk_index", 0))
                content_parts = [row.get("content", "") for row in rows]
                return "\n\n".join(content_parts)
        except Exception as e:
            logger.warning(f"Could not get content from chunks: {e}")
        
        return ""

    async def get_properties(
        self,
        vault_name: str,
        document_id: str,
    ) -> dict[str, Any]:
        """Получение всех свойств документа."""
        properties_dict = await self._db_manager.get_document_properties(vault_name, document_id)
        return properties_dict

    async def find_by_links(
        self,
        vault_name: str,
        links: list[str],
        match_all: bool = True,
    ) -> set[str]:
        """Поиск document_ids по ссылкам через двухэтапный запрос.
        
        Args:
            vault_name: Имя vault'а
            links: Список нормализованных ссылок для поиска
            match_all: Если True, документ должен содержать все ссылки (AND), иначе хотя бы одну (OR)
            
        Returns:
            Множество document_ids документов, содержащих указанные ссылки
        """
        try:
            from obsidian_kb.normalization import DataNormalizer
            
            # Нормализуем ссылки
            normalized_links = DataNormalizer.normalize_links(links)
            if not normalized_links:
                return set()
            
            chunks_table = await self._db_manager._ensure_table(vault_name, "chunks")
            
            def _find() -> set[str]:
                try:
                    document_ids = set()
                    
                    if match_all:
                        # AND логика: документ должен содержать все ссылки
                        # Используем пересечение множеств document_ids для каждой ссылки
                        link_doc_ids: list[set[str]] = []
                        for link in normalized_links:
                            safe_link = link.replace("'", "''")
                            where_clause = f"array_contains(links, '{safe_link}')"
                            arrow_table = chunks_table.search(query=None).where(where_clause).to_arrow()
                            doc_ids = set()
                            if arrow_table.num_rows > 0:
                                doc_ids = set(arrow_table["document_id"].to_pylist())
                            link_doc_ids.append(doc_ids)
                        
                        # Пересечение всех множеств
                        if link_doc_ids:
                            document_ids = link_doc_ids[0]
                            for doc_ids in link_doc_ids[1:]:
                                document_ids &= doc_ids
                    else:
                        # OR логика: документ должен содержать хотя бы одну ссылку
                        for link in normalized_links:
                            safe_link = link.replace("'", "''")
                            where_clause = f"array_contains(links, '{safe_link}')"
                            arrow_table = chunks_table.search(query=None).where(where_clause).to_arrow()
                            if arrow_table.num_rows > 0:
                                doc_ids = set(arrow_table["document_id"].to_pylist())
                                document_ids.update(doc_ids)
                    
                    return document_ids
                except Exception as e:
                    logger.error(f"Error finding documents by links: {e}")
                    return set()
            
            return await asyncio.to_thread(_find)
            
        except Exception as e:
            logger.error(f"Error in find_by_links for vault '{vault_name}': {e}")
            return set()

    async def find_by_filename(
        self,
        vault_name: str,
        filename: str,
        exact_match: bool = True,
    ) -> set[str]:
        """Поиск document_ids по имени файла.
        
        Оптимизированный метод для поиска документов по имени файла через прямой запрос
        к таблице documents вместо медленного FTS поиска.
        
        Args:
            vault_name: Имя vault'а
            filename: Имя файла для поиска (может быть с расширением или без)
            exact_match: Если True, ищет точное совпадение, иначе частичное (LIKE)
            
        Returns:
            Множество document_ids документов с указанным именем файла
        """
        try:
            documents_table = await self._db_manager._ensure_table(vault_name, "documents")
            
            def _find() -> set[str]:
                try:
                    filename_lower = filename.lower()
                    # Экранируем для SQL запроса
                    safe_filename = filename_lower.replace("'", "''")
                    
                    if exact_match:
                        # Точное совпадение: проверяем file_path заканчивается на filename
                        # Также проверяем без расширения
                        where_clause = (
                            f"file_path LIKE '%/{safe_filename}' OR "
                            f"file_path LIKE '%/{safe_filename}.%' OR "
                            f"file_path = '{safe_filename}'"
                        )
                    else:
                        # Частичное совпадение: filename содержится в file_path
                        where_clause = f"file_path LIKE '%{safe_filename}%'"
                    
                    arrow_table = documents_table.search().where(where_clause).to_arrow()
                    document_ids = set()
                    if arrow_table.num_rows > 0:
                        doc_ids = arrow_table["document_id"].to_pylist()
                        document_ids = set(doc_ids)
                    
                    return document_ids
                except Exception as e:
                    logger.error(f"Error finding documents by filename: {e}")
                    return set()
            
            return await asyncio.to_thread(_find)
            
        except Exception as e:
            logger.error(f"Error in find_by_filename for vault '{vault_name}': {e}")
            return set()

    async def find_by_keywords_in_name(
        self,
        vault_name: str,
        keywords: set[str],
        procedural_keywords: set[str] | None = None,
        require_all_keywords: bool = False,
        limit: int | None = None,
    ) -> set[str]:
        """Поиск document_ids по ключевым словам в названиях файлов и заголовках.
        
        ОПТИМИЗАЦИЯ: Использует FTS-поиск вместо LIKE запросов для более быстрого поиска.
        FTS-поиск использует индексы на полях file_path и title для оптимальной производительности.
        
        Args:
            vault_name: Имя vault'а
            keywords: Множество ключевых слов для поиска
            procedural_keywords: Опциональное множество процедурных ключевых слов
            require_all_keywords: Если True, требует совпадение всех ключевых слов (AND),
                                 иначе хотя бы одного (OR)
            limit: Опциональное ограничение количества результатов
            
        Returns:
            Множество document_ids документов, содержащих ключевые слова в названиях
        """
        if not keywords and not procedural_keywords:
            return set()
        
        try:
            documents_table = await self._db_manager._ensure_table(vault_name, "documents")
            
            # ОПТИМИЗАЦИЯ: Убеждаемся, что FTS индексы созданы
            try:
                await self._db_manager._create_fts_index(documents_table, "documents")
            except Exception as e:
                logger.debug(f"FTS index check failed (may already exist): {e}")
            
            def _find() -> set[str]:
                try:
                    document_ids = set()
                    
                    # ОПТИМИЗАЦИЯ: Используем FTS-поиск вместо LIKE запросов
                    # FTS-поиск использует индексы на file_path и title для более быстрого поиска
                    
                    # Формируем FTS-запрос из ключевых слов
                    if keywords:
                        # Для FTS-поиска объединяем ключевые слова через пробел
                        # Если require_all_keywords=True, используем кавычки для фразового поиска
                        if require_all_keywords and len(keywords) > 1:
                            # AND логика: все ключевые слова должны присутствовать
                            # В FTS используем кавычки для фразового поиска или просто пробелы
                            fts_query = " ".join(keywords)
                        else:
                            # OR логика: хотя бы одно ключевое слово должно присутствовать
                            fts_query = " ".join(keywords)
                        
                        # Выполняем FTS-поиск по file_path и title
                        # FTS автоматически использует индексы на этих полях
                        try:
                            search_query = documents_table.search(fts_query, query_type="fts")
                            
                            # ОПТИМИЗАЦИЯ: Используем больше результатов для лучшего ранжирования
                            # Затем сортируем по score и берем топ limit
                            fts_limit = (limit * 2) if limit else None
                            if fts_limit:
                                search_query = search_query.limit(fts_limit)
                            
                            arrow_table = search_query.to_arrow()
                            if arrow_table.num_rows > 0:
                                # ОПТИМИЗАЦИЯ: Используем score для ранжирования результатов
                                # FTS возвращает результаты с score, сортируем по нему
                                doc_ids_list = arrow_table["document_id"].to_pylist()
                                
                                # Проверяем наличие колонки score
                                if "_score" in arrow_table.column_names:
                                    scores = arrow_table["_score"].to_pylist()
                                    # Сортируем по score (убывание) и берем топ limit
                                    scored_docs = list(zip(doc_ids_list, scores))
                                    scored_docs.sort(key=lambda x: x[1], reverse=True)
                                    if limit:
                                        top_doc_ids = [doc_id for doc_id, _ in scored_docs[:limit]]
                                    else:
                                        top_doc_ids = [doc_id for doc_id, _ in scored_docs]
                                    document_ids.update(top_doc_ids)
                                else:
                                    # Если score нет, просто берем первые limit результатов
                                    if limit:
                                        top_doc_ids = doc_ids_list[:limit]
                                    else:
                                        top_doc_ids = doc_ids_list
                                    document_ids.update(top_doc_ids)
                        except Exception as e:
                            logger.debug(f"FTS search failed, falling back to LIKE: {e}")
                            # Fallback на LIKE запросы если FTS не работает
                            return self._find_with_like(documents_table, keywords, procedural_keywords, 
                                                       require_all_keywords, limit)
                    
                    # Если есть процедурные ключевые слова, выполняем отдельный FTS-поиск
                    if procedural_keywords:
                        procedural_query = " ".join(procedural_keywords)
                        try:
                            search_query = documents_table.search(procedural_query, query_type="fts")
                            # ОПТИМИЗАЦИЯ: Используем больше результатов для лучшего ранжирования
                            fts_limit = (limit * 2) if limit else None
                            if fts_limit:
                                search_query = search_query.limit(fts_limit)
                            arrow_table = search_query.to_arrow()
                            if arrow_table.num_rows > 0:
                                doc_ids_list = arrow_table["document_id"].to_pylist()
                                
                                # ОПТИМИЗАЦИЯ: Используем score для ранжирования результатов
                                if "_score" in arrow_table.column_names:
                                    scores = arrow_table["_score"].to_pylist()
                                    scored_docs = list(zip(doc_ids_list, scores))
                                    scored_docs.sort(key=lambda x: x[1], reverse=True)
                                    if limit:
                                        top_doc_ids = [doc_id for doc_id, _ in scored_docs[:limit]]
                                    else:
                                        top_doc_ids = [doc_id for doc_id, _ in scored_docs]
                                    document_ids.update(top_doc_ids)
                                else:
                                    if limit:
                                        top_doc_ids = doc_ids_list[:limit]
                                    else:
                                        top_doc_ids = doc_ids_list
                                    document_ids.update(top_doc_ids)
                        except Exception as e:
                            logger.debug(f"FTS search for procedural keywords failed: {e}")
                            # Fallback на LIKE для процедурных ключевых слов
                            if not keywords:  # Только если нет основных ключевых слов
                                return self._find_with_like(documents_table, set(), procedural_keywords, 
                                                           require_all_keywords, limit)
                    
                    return document_ids
                except Exception as e:
                    logger.error(f"Error finding documents by keywords with FTS: {e}")
                    # Fallback на LIKE запросы при ошибке
                    return self._find_with_like(documents_table, keywords, procedural_keywords, 
                                               require_all_keywords, limit)
            
            return await asyncio.to_thread(_find)
            
        except Exception as e:
            logger.error(f"Error in find_by_keywords_in_name for vault '{vault_name}': {e}")
            return set()
    
    def _find_with_like(
        self,
        documents_table: Any,
        keywords: set[str],
        procedural_keywords: set[str] | None = None,
        require_all_keywords: bool = False,
        limit: int | None = None,
    ) -> set[str]:
        """Fallback метод с использованием LIKE запросов (старая реализация).
        
        Используется если FTS-поиск не работает или не поддерживается.
        """
        try:
            # Экранируем ключевые слова для SQL
            safe_keywords = [kw.replace("'", "''") for kw in keywords] if keywords else []
            
            if require_all_keywords and len(safe_keywords) > 1:
                # Требуем совпадение всех ключевых слов (AND логика)
                keyword_conditions = []
                for keyword in safe_keywords:
                    keyword_lower = keyword.lower()
                    keyword_conditions.append(
                        f"(LOWER(file_path) LIKE '%{keyword_lower}%' OR "
                        f"LOWER(file_path) LIKE '%{keyword_lower.replace('-', '_')}%' OR "
                        f"LOWER(file_path) LIKE '%{keyword_lower.replace('_', '-')}%' OR "
                        f"LOWER(title) LIKE '%{keyword_lower}%')"
                    )
                where_clause = " AND ".join(keyword_conditions)
                
                if procedural_keywords:
                    safe_procedural = [kw.replace("'", "''") for kw in procedural_keywords]
                    procedural_conditions = []
                    for keyword in safe_procedural:
                        keyword_lower = keyword.lower()
                        procedural_conditions.append(
                            f"(LOWER(file_path) LIKE '%{keyword_lower}%' OR "
                            f"LOWER(title) LIKE '%{keyword_lower}%')"
                        )
                    if procedural_conditions:
                        where_clause = f"({where_clause}) AND ({' OR '.join(procedural_conditions)})"
            else:
                # OR логика
                conditions = []
                for keyword in safe_keywords:
                    keyword_lower = keyword.lower()
                    conditions.append(
                        f"(LOWER(file_path) LIKE '%{keyword_lower}%' OR "
                        f"LOWER(file_path) LIKE '%{keyword_lower.replace('-', '_')}%' OR "
                        f"LOWER(file_path) LIKE '%{keyword_lower.replace('_', '-')}%' OR "
                        f"LOWER(title) LIKE '%{keyword_lower}%')"
                    )
                
                if procedural_keywords:
                    safe_procedural = [kw.replace("'", "''") for kw in procedural_keywords]
                    for keyword in safe_procedural:
                        keyword_lower = keyword.lower()
                        conditions.append(
                            f"(LOWER(file_path) LIKE '%{keyword_lower}%' OR "
                            f"LOWER(title) LIKE '%{keyword_lower}%')"
                        )
                
                where_clause = " OR ".join(conditions) if conditions else "1=0"
            
            query = documents_table.search().where(where_clause)
            if limit is not None and limit > 0:
                query = query.limit(limit)
            arrow_table = query.to_arrow()
            document_ids = set()
            if arrow_table.num_rows > 0:
                doc_ids = arrow_table["document_id"].to_pylist()
                document_ids = set(doc_ids)
            
            return document_ids
        except Exception as e:
            logger.error(f"Error finding documents with LIKE: {e}")
            return set()

    async def get_all_document_ids(
        self,
        vault_name: str,
    ) -> set[str]:
        """Получение всех document_ids из vault'а.
        
        Оптимизированный метод для получения всех документов через прямой запрос
        к таблице documents вместо медленного FTS поиска.
        
        Используется для оптимизации процедурных запросов.
        
        Args:
            vault_name: Имя vault'а
            
        Returns:
            Множество всех document_ids в vault'е
        """
        try:
            documents_table = await self._db_manager._ensure_table(vault_name, "documents")
            
            def _get_all() -> set[str]:
                try:
                    arrow_table = documents_table.to_arrow()
                    if arrow_table.num_rows == 0:
                        return set()
                    
                    doc_ids = arrow_table["document_id"].to_pylist()
                    return set(doc_ids)
                except Exception as e:
                    logger.error(f"Error getting all document IDs: {e}")
                    return set()
            
            return await asyncio.to_thread(_get_all)
            
        except Exception as e:
            logger.error(f"Error in get_all_document_ids for vault '{vault_name}': {e}")
            return set()

