"""Парсер WHERE условий для Dataview запросов.

Поддерживает SQL-подобный синтаксис условий с операторами сравнения,
проверки вхождения и относительными датами.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class WhereCondition:
    """Условие WHERE."""
    field: str
    operator: str
    value: Any
    connector: str = "AND"  # "AND" | "OR"


class WhereParser:
    """Парсер WHERE условий."""
    
    # Поддерживаемые операторы
    OPERATORS = {
        "=": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        "CONTAINS": lambda a, b: b in a if isinstance(a, (list, str)) else False,
        "NOT CONTAINS": lambda a, b: b not in a if isinstance(a, (list, str)) else True,
        "STARTS WITH": lambda a, b: str(a).startswith(str(b)),
        "ENDS WITH": lambda a, b: str(a).endswith(str(b)),
        "IS NULL": lambda a, b: a is None or a == "",
        "IS NOT NULL": lambda a, b: a is not None and a != "",
    }
    
    # Паттерн для парсинга условий
    CONDITION_PATTERN = re.compile(
        r'(\w+)\s*'  # Имя поля
        r'(=|!=|>=|<=|>|<|CONTAINS|NOT CONTAINS|STARTS WITH|ENDS WITH|IS NULL|IS NOT NULL)\s*'  # Оператор
        r'(?:"([^"]+)"|\'([^\']+)\'|(\S+))?',  # Значение (в кавычках или без)
        re.IGNORECASE
    )
    
    # Относительные даты
    RELATIVE_DATES = {
        "today": lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        "yesterday": lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1),
        "last_week": lambda: datetime.now() - timedelta(weeks=1),
        "last_month": lambda: datetime.now() - timedelta(days=30),
        "last_year": lambda: datetime.now() - timedelta(days=365),
    }
    
    @classmethod
    def parse(cls, where_string: str) -> list[WhereCondition]:
        """
        Парсинг WHERE строки.
        
        Args:
            where_string: Строка условий, например:
                "status != done AND priority > 2"
                "role = manager OR role = director"
                "created > last_week"
        
        Returns:
            Список WhereCondition
        """
        conditions = []
        
        # Разбиваем по AND/OR
        parts = re.split(r'\s+(AND|OR)\s+', where_string, flags=re.IGNORECASE)
        
        connector = "AND"
        for part in parts:
            part = part.strip()
            
            if part.upper() in ("AND", "OR"):
                connector = part.upper()
                continue
            
            match = cls.CONDITION_PATTERN.match(part)
            if match:
                field = match.group(1)
                operator = match.group(2).upper()
                # Значение может быть в разных группах
                value = match.group(3) or match.group(4) or match.group(5)
                
                # Обработка относительных дат
                if value and value.lower() in cls.RELATIVE_DATES:
                    value = cls.RELATIVE_DATES[value.lower()]()
                
                conditions.append(WhereCondition(
                    field=field,
                    operator=operator,
                    value=value,
                    connector=connector
                ))
                
                connector = "AND"  # Reset
        
        return conditions
    
    @classmethod
    def evaluate(cls, conditions: list[WhereCondition], document: dict) -> bool:
        """
        Проверка документа на соответствие условиям.
        
        Args:
            conditions: Список условий
            document: Документ для проверки
        
        Returns:
            True если документ соответствует всем условиям
        """
        if not conditions:
            return True
        
        result = True
        prev_connector = "AND"
        
        for condition in conditions:
            doc_value = document.get(condition.field)
            
            # Получаем функцию оператора
            op_func = cls.OPERATORS.get(condition.operator)
            if not op_func:
                continue
            
            # Вычисляем результат условия
            try:
                condition_result = op_func(doc_value, condition.value)
            except (TypeError, ValueError):
                condition_result = False
            
            # Комбинируем с предыдущим результатом
            if prev_connector == "AND":
                result = result and condition_result
            else:  # OR
                result = result or condition_result
            
            prev_connector = condition.connector
        
        return result

