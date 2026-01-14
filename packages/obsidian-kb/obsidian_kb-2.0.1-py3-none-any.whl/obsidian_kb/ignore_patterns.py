"""Модуль для работы с паттернами игнорирования файлов (в стиле .gitignore)."""

import fnmatch
import logging
import re
from pathlib import Path
from typing import Pattern

logger = logging.getLogger(__name__)

# Имя файла с паттернами игнорирования
IGNORE_FILE_NAME = ".obsidian-kb-ignore"


class IgnorePattern:
    """Паттерн для игнорирования файлов/папок."""

    def __init__(self, pattern: str, is_negation: bool = False) -> None:
        """Инициализация паттерна.

        Args:
            pattern: Паттерн (может содержать *, ?, **)
            is_negation: Если True, паттерн отменяет игнорирование (начинается с !)
        """
        self.pattern = pattern
        self.is_negation = is_negation
        self.regex = self._compile_pattern(pattern)

    def _compile_pattern(self, pattern: str) -> Pattern[str]:
        """Компиляция паттерна в регулярное выражение.

        Args:
            pattern: Паттерн в стиле .gitignore

        Returns:
            Скомпилированное регулярное выражение
        """
        # Нормализуем паттерн
        original_pattern = pattern.strip()
        pattern = original_pattern
        
        # Убираем ведущий / если есть (означает корень)
        anchor_to_root = pattern.startswith("/")
        if anchor_to_root:
            pattern = pattern[1:]
        
        # Обрабатываем ** (любые директории)
        has_double_star = "**" in pattern
        
        # Разбиваем паттерн на части
        parts = pattern.split("/")
        regex_parts = []
        
        # Обрабатываем ** специально
        if pattern == "**":
            # Просто ** означает всё
            regex_str = ".*"
        else:
            # Проверяем, начинается ли паттерн с **/
            starts_with_double_star = pattern.startswith("**/")
            
            # Упрощаем обработку **: заменяем **/ на .*/ и /** на /.*
            simplified = pattern.replace("**/", ".*/").replace("/**", "/.*")
            
            # Разбиваем упрощённый паттерн
            parts = simplified.split("/")
            regex_parts = []
            
            for part in parts:
                if part == "":
                    continue
                elif part == ".*":
                    regex_parts.append(".*")
                else:
                    # Экранируем специальные символы
                    escaped = re.escape(part)
                    # Заменяем \* на паттерн для любых символов кроме /
                    escaped = escaped.replace(r"\*", r"[^/]*")
                    # Заменяем \? на паттерн для одного символа кроме /
                    escaped = escaped.replace(r"\?", r"[^/]")
                    regex_parts.append(escaped)
            
            regex_str = "/".join(regex_parts) if regex_parts else ""
            
            # Если паттерн начинался с **/, делаем начальный .* опциональным
            if starts_with_double_star and regex_str.startswith(".*/"):
                regex_str = regex_str[3:]  # Убираем .*/
                # Добавляем опциональный префикс
                regex_str = f"(.*/)?{regex_str}"
        
        # Если паттерн заканчивается на /, это директория
        is_directory = original_pattern.endswith("/")
        
        # Формируем финальный паттерн
        if pattern == "**":
            # Просто ** означает всё
            regex_str = ".*"
        elif len(parts) == 1 and not anchor_to_root and not has_double_star:
            # Паттерн только для имени файла (например, *.tmp)
            # Должен соответствовать имени файла в конце любого пути
            regex_str = f"{regex_str}$"
        else:
            # Паттерн с путём
            if anchor_to_root:
                # Паттерн должен начинаться с корня
                regex_str = f"^{regex_str}"
            else:
                # Паттерн может быть в любом месте пути
                # Если начинается с **, не требуем начало строки
                if original_pattern.startswith("**"):
                    regex_str = f".*{regex_str}"
                else:
                    regex_str = f"(^|/){regex_str}"
            
            if is_directory:
                # Для директории: должно совпадать с началом пути к файлу внутри
                regex_str = f"{regex_str}(/.*)?$"
            else:
                # Для файла с путём: должно совпадать с полным путём
                regex_str = f"{regex_str}$"
        
        try:
            return re.compile(regex_str)
        except re.error as e:
            logger.warning(f"Invalid pattern '{original_pattern}': {e}, using fnmatch")
            # Fallback: используем fnmatch
            return re.compile(fnmatch.translate(original_pattern))

    def matches(self, path: str) -> bool:
        """Проверка, соответствует ли путь паттерну.

        Args:
            path: Относительный путь к файлу/директории

        Returns:
            True если путь соответствует паттерну
        """
        # Нормализуем путь (используем / как разделитель)
        normalized_path = path.replace("\\", "/")
        
        # Проверяем соответствие паттерну
        if self.regex.match(normalized_path):
            return True
        
        # Для паттернов типа *.ext проверяем также имя файла
        if "*" in self.pattern and "/" not in self.pattern:
            # Это паттерн только для имени файла
            filename = normalized_path.split("/")[-1]
            if self.regex.match(filename):
                return True
        
        return False


class IgnoreMatcher:
    """Матчер для проверки игнорирования файлов по паттернам."""

    def __init__(self, patterns: list[IgnorePattern]) -> None:
        """Инициализация матчера.

        Args:
            patterns: Список паттернов игнорирования
        """
        self.patterns = patterns

    def should_ignore(self, path: str) -> bool:
        """Проверка, должен ли файл быть проигнорирован.

        Args:
            path: Относительный путь к файлу/директории

        Returns:
            True если файл должен быть проигнорирован
        """
        # Нормализуем путь
        normalized_path = path.replace("\\", "/")
        
        # Проверяем сам путь и все родительские директории
        path_parts = normalized_path.split("/")
        paths_to_check = []
        for i in range(len(path_parts)):
            # Проверяем путь от корня до текущего уровня
            check_path = "/".join(path_parts[:i+1])
            paths_to_check.append(check_path)
            # Также проверяем с завершающим / для директорий
            if i < len(path_parts) - 1:  # Не последний элемент (файл)
                paths_to_check.append(check_path + "/")
        
        # Сначала проверяем паттерны отрицания (они имеют приоритет)
        negations = [p for p in self.patterns if p.is_negation]
        for check_path in paths_to_check:
            for neg_pattern in negations:
                if neg_pattern.matches(check_path):
                    return False  # Паттерн отрицания отменяет игнорирование
        
        # Затем проверяем обычные паттерны
        for check_path in paths_to_check:
            for pattern in self.patterns:
                if not pattern.is_negation and pattern.matches(check_path):
                    return True
        
        return False


def parse_ignore_file(ignore_file_path: Path) -> list[IgnorePattern]:
    """Парсинг файла с паттернами игнорирования.

    Args:
        ignore_file_path: Путь к файлу .obsidian-kb-ignore

    Returns:
        Список паттернов игнорирования
    """
    if not ignore_file_path.exists():
        return []
    
    patterns: list[IgnorePattern] = []
    
    try:
        content = ignore_file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Failed to read ignore file {ignore_file_path}: {e}")
        return []
    
    for line_num, line in enumerate(content.splitlines(), 1):
        # Убираем пробелы в начале и конце
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith("#"):
            continue
        
        # Проверяем на отрицание (начинается с !)
        is_negation = line.startswith("!")
        if is_negation:
            pattern_str = line[1:].strip()
        else:
            pattern_str = line
        
        if not pattern_str:
            continue
        
        try:
            pattern = IgnorePattern(pattern_str, is_negation=is_negation)
            patterns.append(pattern)
        except Exception as e:
            logger.warning(f"Invalid pattern on line {line_num} in {ignore_file_path}: {line} ({e})")
            continue
    
    return patterns


def load_ignore_patterns(vault_path: Path) -> IgnoreMatcher:
    """Загрузка паттернов игнорирования для vault'а.

    Args:
        vault_path: Путь к корню vault'а

    Returns:
        IgnoreMatcher с загруженными паттернами
    """
    ignore_file = vault_path / IGNORE_FILE_NAME
    patterns = parse_ignore_file(ignore_file)
    
    # Добавляем паттерны по умолчанию (только если пользователь не создал свой файл)
    if not ignore_file.exists():
        default_patterns = [
            # Временные файлы
            "*.tmp",
            "*.temp",
            "*.swp",
            "*.bak",
            "*.~",
            # Системные файлы
            ".DS_Store",
            "Thumbs.db",
            # Node modules и другие зависимости
            "node_modules/",
            ".git/",
            ".svn/",
            # Python виртуальные окружения
            ".venv/",
            "venv/",
            "env/",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
        ]
        
        for default_pattern in default_patterns:
            patterns.append(IgnorePattern(default_pattern))
    
    return IgnoreMatcher(patterns)

