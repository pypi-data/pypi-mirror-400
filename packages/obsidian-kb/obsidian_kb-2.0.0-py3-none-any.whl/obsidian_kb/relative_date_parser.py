"""Модуль для парсинга относительных дат.

Поддерживает форматы:
- today, yesterday
- last_week, last_month, last_year
- this_week, this_month, this_year
- n_days_ago, n_weeks_ago, n_months_ago
"""

import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RelativeDateParser:
    """Парсер относительных дат для фильтров поиска."""
    
    # Паттерны для парсинга относительных дат
    TODAY_PATTERN = re.compile(r'^today$', re.IGNORECASE)
    YESTERDAY_PATTERN = re.compile(r'^yesterday$', re.IGNORECASE)
    LAST_WEEK_PATTERN = re.compile(r'^last_week$', re.IGNORECASE)
    LAST_MONTH_PATTERN = re.compile(r'^last_month$', re.IGNORECASE)
    LAST_YEAR_PATTERN = re.compile(r'^last_year$', re.IGNORECASE)
    THIS_WEEK_PATTERN = re.compile(r'^this_week$', re.IGNORECASE)
    THIS_MONTH_PATTERN = re.compile(r'^this_month$', re.IGNORECASE)
    THIS_YEAR_PATTERN = re.compile(r'^this_year$', re.IGNORECASE)
    N_DAYS_AGO_PATTERN = re.compile(r'^(\d+)_days_ago$', re.IGNORECASE)
    N_WEEKS_AGO_PATTERN = re.compile(r'^(\d+)_weeks_ago$', re.IGNORECASE)
    N_MONTHS_AGO_PATTERN = re.compile(r'^(\d+)_months_ago$', re.IGNORECASE)
    
    @classmethod
    def parse_relative_date(cls, date_str: str, reference_date: datetime | None = None) -> datetime | None:
        """Парсинг относительной даты в абсолютную дату.
        
        Args:
            date_str: Относительная дата (например, "last_week", "7_days_ago")
            reference_date: Опорная дата (по умолчанию текущая дата)
            
        Returns:
            Абсолютная дата или None если не удалось распарсить
            
        Examples:
            >>> parser = RelativeDateParser()
            >>> parser.parse_relative_date("today")
            datetime(2024, 1, 15, 0, 0, 0)  # текущая дата
            >>> parser.parse_relative_date("last_week")
            datetime(2024, 1, 8, 0, 0, 0)  # неделя назад
            >>> parser.parse_relative_date("7_days_ago")
            datetime(2024, 1, 8, 0, 0, 0)  # 7 дней назад
        """
        if not date_str:
            return None
        
        if reference_date is None:
            reference_date = datetime.now()
        
        date_str = date_str.strip().lower()
        
        # today
        if cls.TODAY_PATTERN.match(date_str):
            return reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # yesterday
        if cls.YESTERDAY_PATTERN.match(date_str):
            yesterday = reference_date - timedelta(days=1)
            return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # last_week (начало недели неделю назад)
        if cls.LAST_WEEK_PATTERN.match(date_str):
            # Находим начало текущей недели (понедельник)
            days_since_monday = reference_date.weekday()
            start_of_this_week = reference_date - timedelta(days=days_since_monday)
            start_of_last_week = start_of_this_week - timedelta(weeks=1)
            return start_of_last_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # last_month (начало месяца месяц назад)
        if cls.LAST_MONTH_PATTERN.match(date_str):
            # Первый день текущего месяца
            first_day_this_month = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Первый день прошлого месяца
            if first_day_this_month.month == 1:
                first_day_last_month = first_day_this_month.replace(year=first_day_this_month.year - 1, month=12)
            else:
                first_day_last_month = first_day_this_month.replace(month=first_day_this_month.month - 1)
            return first_day_last_month
        
        # last_year (начало года год назад)
        if cls.LAST_YEAR_PATTERN.match(date_str):
            first_day_last_year = reference_date.replace(year=reference_date.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return first_day_last_year
        
        # this_week (начало текущей недели)
        if cls.THIS_WEEK_PATTERN.match(date_str):
            days_since_monday = reference_date.weekday()
            start_of_this_week = reference_date - timedelta(days=days_since_monday)
            return start_of_this_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # this_month (начало текущего месяца)
        if cls.THIS_MONTH_PATTERN.match(date_str):
            first_day_this_month = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return first_day_this_month
        
        # this_year (начало текущего года)
        if cls.THIS_YEAR_PATTERN.match(date_str):
            first_day_this_year = reference_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return first_day_this_year
        
        # n_days_ago
        match = cls.N_DAYS_AGO_PATTERN.match(date_str)
        if match:
            days = int(match.group(1))
            result_date = reference_date - timedelta(days=days)
            return result_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # n_weeks_ago
        match = cls.N_WEEKS_AGO_PATTERN.match(date_str)
        if match:
            weeks = int(match.group(1))
            result_date = reference_date - timedelta(weeks=weeks)
            return result_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # n_months_ago
        match = cls.N_MONTHS_AGO_PATTERN.match(date_str)
        if match:
            months = int(match.group(1))
            result_date = reference_date
            for _ in range(months):
                # Вычитаем месяц
                if result_date.month == 1:
                    result_date = result_date.replace(year=result_date.year - 1, month=12)
                else:
                    result_date = result_date.replace(month=result_date.month - 1)
            return result_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Не удалось распарсить
        logger.debug(f"Could not parse relative date: {date_str}")
        return None
    
    @classmethod
    def is_relative_date(cls, date_str: str) -> bool:
        """Проверка, является ли строка относительной датой.
        
        Args:
            date_str: Строка для проверки
            
        Returns:
            True если строка является относительной датой
        """
        if not date_str:
            return False
        
        date_str = date_str.strip().lower()
        
        patterns = [
            cls.TODAY_PATTERN,
            cls.YESTERDAY_PATTERN,
            cls.LAST_WEEK_PATTERN,
            cls.LAST_MONTH_PATTERN,
            cls.LAST_YEAR_PATTERN,
            cls.THIS_WEEK_PATTERN,
            cls.THIS_MONTH_PATTERN,
            cls.THIS_YEAR_PATTERN,
            cls.N_DAYS_AGO_PATTERN,
            cls.N_WEEKS_AGO_PATTERN,
            cls.N_MONTHS_AGO_PATTERN,
        ]
        
        return any(pattern.match(date_str) for pattern in patterns)

