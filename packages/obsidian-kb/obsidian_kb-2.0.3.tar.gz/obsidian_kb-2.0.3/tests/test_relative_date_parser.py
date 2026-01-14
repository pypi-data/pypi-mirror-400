"""Тесты для парсера относительных дат."""

from datetime import datetime, timedelta

import pytest

from obsidian_kb.relative_date_parser import RelativeDateParser


class TestRelativeDateParser:
    """Тесты для RelativeDateParser."""
    
    def test_today(self):
        """Тест парсинга 'today'."""
        result = RelativeDateParser.parse_relative_date("today")
        assert result is not None
        assert result.date() == datetime.now().date()
        assert result.hour == 0
        assert result.minute == 0
    
    def test_yesterday(self):
        """Тест парсинга 'yesterday'."""
        result = RelativeDateParser.parse_relative_date("yesterday")
        assert result is not None
        expected = datetime.now() - timedelta(days=1)
        assert result.date() == expected.date()
        assert result.hour == 0
    
    def test_last_week(self):
        """Тест парсинга 'last_week'."""
        result = RelativeDateParser.parse_relative_date("last_week")
        assert result is not None
        # Должно быть начало недели неделю назад (понедельник)
        assert result.weekday() == 0  # Понедельник
        assert result.hour == 0
    
    def test_last_month(self):
        """Тест парсинга 'last_month'."""
        result = RelativeDateParser.parse_relative_date("last_month")
        assert result is not None
        # Должно быть первое число прошлого месяца
        assert result.day == 1
        assert result.hour == 0
    
    def test_last_year(self):
        """Тест парсинга 'last_year'."""
        result = RelativeDateParser.parse_relative_date("last_year")
        assert result is not None
        # Должно быть 1 января прошлого года
        assert result.year == datetime.now().year - 1
        assert result.month == 1
        assert result.day == 1
    
    def test_this_week(self):
        """Тест парсинга 'this_week'."""
        result = RelativeDateParser.parse_relative_date("this_week")
        assert result is not None
        # Должно быть начало текущей недели (понедельник)
        days_since_monday = datetime.now().weekday()
        expected = datetime.now() - timedelta(days=days_since_monday)
        assert result.date() == expected.date()
        assert result.weekday() == 0  # Понедельник
    
    def test_this_month(self):
        """Тест парсинга 'this_month'."""
        result = RelativeDateParser.parse_relative_date("this_month")
        assert result is not None
        # Должно быть первое число текущего месяца
        assert result.day == 1
        assert result.month == datetime.now().month
        assert result.year == datetime.now().year
    
    def test_this_year(self):
        """Тест парсинга 'this_year'."""
        result = RelativeDateParser.parse_relative_date("this_year")
        assert result is not None
        # Должно быть 1 января текущего года
        assert result.year == datetime.now().year
        assert result.month == 1
        assert result.day == 1
    
    def test_n_days_ago(self):
        """Тест парсинга 'n_days_ago'."""
        result = RelativeDateParser.parse_relative_date("7_days_ago")
        assert result is not None
        expected = datetime.now() - timedelta(days=7)
        assert result.date() == expected.date()
        assert result.hour == 0
    
    def test_n_weeks_ago(self):
        """Тест парсинга 'n_weeks_ago'."""
        result = RelativeDateParser.parse_relative_date("2_weeks_ago")
        assert result is not None
        expected = datetime.now() - timedelta(weeks=2)
        assert result.date() == expected.date()
    
    def test_n_months_ago(self):
        """Тест парсинга 'n_months_ago'."""
        result = RelativeDateParser.parse_relative_date("3_months_ago")
        assert result is not None
        # Должно быть первое число месяца 3 месяца назад
        assert result.day == 1
    
    def test_is_relative_date(self):
        """Тест проверки относительной даты."""
        assert RelativeDateParser.is_relative_date("today") is True
        assert RelativeDateParser.is_relative_date("yesterday") is True
        assert RelativeDateParser.is_relative_date("last_week") is True
        assert RelativeDateParser.is_relative_date("7_days_ago") is True
        assert RelativeDateParser.is_relative_date("2024-01-15") is False
        assert RelativeDateParser.is_relative_date("invalid") is False
        assert RelativeDateParser.is_relative_date("") is False
    
    def test_case_insensitive(self):
        """Тест регистронезависимости."""
        result1 = RelativeDateParser.parse_relative_date("TODAY")
        result2 = RelativeDateParser.parse_relative_date("today")
        assert result1 is not None
        assert result2 is not None
        assert result1.date() == result2.date()
    
    def test_custom_reference_date(self):
        """Тест с кастомной опорной датой."""
        reference = datetime(2024, 1, 15)
        result = RelativeDateParser.parse_relative_date("yesterday", reference_date=reference)
        assert result is not None
        assert result.date() == datetime(2024, 1, 14).date()
    
    def test_invalid_date(self):
        """Тест обработки невалидной даты."""
        result = RelativeDateParser.parse_relative_date("invalid_date")
        assert result is None

