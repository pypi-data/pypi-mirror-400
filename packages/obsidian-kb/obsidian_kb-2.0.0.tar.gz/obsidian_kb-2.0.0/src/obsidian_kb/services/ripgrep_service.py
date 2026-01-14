"""RipgrepService для прямого текстового поиска по файлам.

Предоставляет прямой текстовый поиск по файлам vault'а без использования индекса.
Использует ripgrep если установлен, иначе fallback на grep или python.
"""

import asyncio
import json
import logging
import re
import shutil
import time
from pathlib import Path

from obsidian_kb.interfaces import IRipgrepService, RipgrepMatch, RipgrepResult

logger = logging.getLogger(__name__)


class RipgrepService(IRipgrepService):
    """Прямой текстовый поиск по файлам vault'а."""
    
    def __init__(self) -> None:
        """Инициализация RipgrepService."""
        self._ripgrep_path = shutil.which("rg")
        self._grep_path = shutil.which("grep")
    
    def is_ripgrep_available(self) -> bool:
        """Проверка доступности ripgrep."""
        return self._ripgrep_path is not None
    
    async def search_text(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
        context_lines: int = 2,
        file_pattern: str = "*.md",
        max_results: int = 100
    ) -> RipgrepResult:
        """Поиск текста в файлах vault'а."""
        start_time = time.time()
        
        if self._ripgrep_path:
            result = await self._search_with_ripgrep(
                vault_path, query, case_sensitive, whole_word,
                context_lines, file_pattern, max_results, is_regex=False
            )
        elif self._grep_path:
            result = await self._search_with_grep(
                vault_path, query, case_sensitive, whole_word,
                context_lines, file_pattern, max_results
            )
        else:
            result = await self._search_with_python(
                vault_path, query, case_sensitive, whole_word,
                context_lines, file_pattern, max_results
            )
        
        result.search_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def search_regex(
        self,
        vault_path: str,
        pattern: str,
        context_lines: int = 2,
        file_pattern: str = "*.md",
        max_results: int = 100
    ) -> RipgrepResult:
        """Поиск по regex паттерну."""
        start_time = time.time()
        
        if self._ripgrep_path:
            result = await self._search_with_ripgrep(
                vault_path, pattern, case_sensitive=True, whole_word=False,
                context_lines=context_lines, file_pattern=file_pattern,
                max_results=max_results, is_regex=True
            )
        else:
            result = await self._search_regex_python(
                vault_path, pattern, context_lines, file_pattern, max_results
            )
        
        result.search_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def find_files(
        self,
        vault_path: str,
        name_pattern: str,
        content_contains: str | None = None
    ) -> list[str]:
        """Поиск файлов по имени и/или содержимому."""
        vault = Path(vault_path)
        
        # Находим файлы по паттерну имени
        matching_files = list(vault.glob(f"**/{name_pattern}"))
        
        # Фильтруем по содержимому если нужно
        if content_contains:
            filtered = []
            for file_path in matching_files:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if content_contains.lower() in content.lower():
                        filtered.append(str(file_path.relative_to(vault)))
                except Exception:
                    continue
            return filtered
        
        return [str(f.relative_to(vault)) for f in matching_files]
    
    async def _search_with_ripgrep(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool,
        whole_word: bool,
        context_lines: int,
        file_pattern: str,
        max_results: int,
        is_regex: bool
    ) -> RipgrepResult:
        """Поиск с использованием ripgrep."""
        args = [
            self._ripgrep_path,
            "--json",  # JSON output
            f"--context={context_lines}",
            f"--glob={file_pattern}",
            f"--max-count={max_results}",
        ]
        
        if not case_sensitive:
            args.append("--ignore-case")
        
        if whole_word:
            args.append("--word-regexp")
        
        if not is_regex:
            args.append("--fixed-strings")
        
        args.extend([query, vault_path])
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if stderr:
                logger.warning(f"ripgrep stderr: {stderr.decode()}")
            
            # Парсим JSON output
            matches = []
            files_searched = set()
            context_before_buffer: dict[str, list[str]] = {}
            context_after_buffer: dict[str, list[str]] = {}
            current_match: RipgrepMatch | None = None
            
            for line in stdout.decode("utf-8", errors="ignore").strip().split("\n"):
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    msg_type = data.get("type")
                    
                    if msg_type == "match":
                        match_data = data["data"]
                        file_path = match_data["path"]["text"]
                        files_searched.add(file_path)
                        
                        line_number = match_data["line_number"]
                        line_content = match_data["lines"]["text"].rstrip("\n")
                        
                        # Получаем контекст из буферов
                        file_key = f"{file_path}:{line_number}"
                        context_before = context_before_buffer.get(file_key, [])
                        context_after = context_after_buffer.get(file_key, [])
                        
                        for submatch in match_data.get("submatches", []):
                            matches.append(RipgrepMatch(
                                file_path=Path(file_path).relative_to(Path(vault_path)).as_posix(),
                                line_number=line_number,
                                line_content=line_content,
                                match_text=submatch["match"]["text"],
                                match_start=submatch["start"],
                                match_end=submatch["end"],
                                context_before=context_before,
                                context_after=context_after
                            ))
                    
                    elif msg_type == "context":
                        # Контекстные строки (до/после совпадения)
                        context_data = data["data"]
                        file_path = context_data["path"]["text"]
                        line_number = context_data["line_number"]
                        line_content = context_data["lines"]["text"].rstrip("\n")
                        
                        # Определяем, это контекст до или после
                        # (ripgrep выводит контекст перед совпадением, затем совпадение)
                        file_key = f"{file_path}:{line_number}"
                        # Просто сохраняем в буфер, будет использовано при следующем match
                        if file_key not in context_before_buffer:
                            context_before_buffer[file_key] = []
                        context_before_buffer[file_key].append(line_content)
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.debug(f"Error parsing ripgrep output: {e}")
                    continue
            
            return RipgrepResult(
                matches=matches[:max_results],
                total_matches=len(matches),
                files_searched=len(files_searched),
                search_time_ms=0  # Будет заполнено в вызывающем методе
            )
        
        except Exception as e:
            logger.error(f"Error running ripgrep: {e}")
            return RipgrepResult(
                matches=[],
                total_matches=0,
                files_searched=0,
                search_time_ms=0
            )
    
    async def _search_with_grep(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool,
        whole_word: bool,
        context_lines: int,
        file_pattern: str,
        max_results: int
    ) -> RipgrepResult:
        """Fallback поиск с grep."""
        args = [
            self._grep_path,
            "-r",  # Recursive
            f"--include={file_pattern}",
            "-n",  # Line numbers
            f"-C{context_lines}",  # Context
        ]
        
        if not case_sensitive:
            args.append("-i")
        
        if whole_word:
            args.append("-w")
        
        args.extend([query, vault_path])
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if stderr:
                logger.debug(f"grep stderr: {stderr.decode()}")
            
            # Парсим grep output
            matches = []
            files_searched = set()
            
            for line in stdout.decode("utf-8", errors="ignore").strip().split("\n"):
                if not line:
                    continue
                
                # Формат: file:line_number:content
                # Или для контекста: file-line_number-content
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    file_path = parts[0]
                    try:
                        line_number = int(parts[1])
                        content = parts[2]
                        
                        # Проверяем, это строка с совпадением или контекст
                        # Контекстные строки обычно не содержат совпадение
                        search_content = content.lower() if not case_sensitive else content
                        search_query = query.lower() if not case_sensitive else query
                        
                        if search_query in search_content:
                            match_start = search_content.find(search_query)
                            matches.append(RipgrepMatch(
                                file_path=Path(file_path).relative_to(Path(vault_path)).as_posix(),
                                line_number=line_number,
                                line_content=content.strip(),
                                match_text=query,
                                match_start=match_start,
                                match_end=match_start + len(query),
                                context_before=[],  # grep не предоставляет структурированный контекст
                                context_after=[]
                            ))
                            files_searched.add(file_path)
                    except ValueError:
                        continue
            
            return RipgrepResult(
                matches=matches[:max_results],
                total_matches=len(matches),
                files_searched=len(files_searched),
                search_time_ms=0
            )
        
        except Exception as e:
            logger.error(f"Error running grep: {e}")
            return RipgrepResult(
                matches=[],
                total_matches=0,
                files_searched=0,
                search_time_ms=0
            )
    
    async def _search_with_python(
        self,
        vault_path: str,
        query: str,
        case_sensitive: bool,
        whole_word: bool,
        context_lines: int,
        file_pattern: str,
        max_results: int
    ) -> RipgrepResult:
        """Pure Python fallback поиск."""
        vault = Path(vault_path)
        matches = []
        files_searched = set()
        
        search_query = query if case_sensitive else query.lower()
        
        try:
            for file_path in vault.glob(f"**/{file_pattern}"):
                if len(matches) >= max_results:
                    break
                
                try:
                    lines = file_path.read_text(encoding="utf-8").splitlines()
                except Exception:
                    continue
                
                files_searched.add(str(file_path))
                
                for i, line in enumerate(lines):
                    if len(matches) >= max_results:
                        break
                    
                    search_line = line if case_sensitive else line.lower()
                    
                    if search_query in search_line:
                        # Проверка whole_word
                        if whole_word:
                            pattern = rf'\b{re.escape(search_query)}\b'
                            if not re.search(pattern, search_line, re.IGNORECASE if not case_sensitive else 0):
                                continue
                        
                        # Контекст
                        context_before = lines[max(0, i - context_lines):i]
                        context_after = lines[i + 1:i + 1 + context_lines]
                        
                        match_start = search_line.find(search_query)
                        
                        matches.append(RipgrepMatch(
                            file_path=file_path.relative_to(vault).as_posix(),
                            line_number=i + 1,
                            line_content=line.strip(),
                            match_text=query,
                            match_start=match_start,
                            match_end=match_start + len(query),
                            context_before=context_before,
                            context_after=context_after
                        ))
            
            return RipgrepResult(
                matches=matches,
                total_matches=len(matches),
                files_searched=len(files_searched),
                search_time_ms=0
            )
        
        except Exception as e:
            logger.error(f"Error in Python search: {e}")
            return RipgrepResult(
                matches=[],
                total_matches=0,
                files_searched=0,
                search_time_ms=0
            )
    
    async def _search_regex_python(
        self,
        vault_path: str,
        pattern: str,
        context_lines: int,
        file_pattern: str,
        max_results: int
    ) -> RipgrepResult:
        """Pure Python regex поиск."""
        vault = Path(vault_path)
        matches = []
        files_searched = set()
        
        try:
            regex = re.compile(pattern)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {e}")
            return RipgrepResult(
                matches=[],
                total_matches=0,
                files_searched=0,
                search_time_ms=0
            )
        
        try:
            for file_path in vault.glob(f"**/{file_pattern}"):
                if len(matches) >= max_results:
                    break
                
                try:
                    lines = file_path.read_text(encoding="utf-8").splitlines()
                except Exception:
                    continue
                
                files_searched.add(str(file_path))
                
                for i, line in enumerate(lines):
                    if len(matches) >= max_results:
                        break
                    
                    match = regex.search(line)
                    if match:
                        context_before = lines[max(0, i - context_lines):i]
                        context_after = lines[i + 1:i + 1 + context_lines]
                        
                        matches.append(RipgrepMatch(
                            file_path=file_path.relative_to(vault).as_posix(),
                            line_number=i + 1,
                            line_content=line.strip(),
                            match_text=match.group(),
                            match_start=match.start(),
                            match_end=match.end(),
                            context_before=context_before,
                            context_after=context_after
                        ))
            
            return RipgrepResult(
                matches=matches,
                total_matches=len(matches),
                files_searched=len(files_searched),
                search_time_ms=0
            )
        
        except Exception as e:
            logger.error(f"Error in Python regex search: {e}")
            return RipgrepResult(
                matches=[],
                total_matches=0,
                files_searched=0,
                search_time_ms=0
            )

