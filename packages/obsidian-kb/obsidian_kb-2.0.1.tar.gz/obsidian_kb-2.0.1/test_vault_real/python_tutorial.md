---
title: Python Tutorial
tags: [python, programming, tutorial]
created: 2024-01-15
---

# Python Tutorial

Это руководство по Python для начинающих.

## Основы Python

Python - это интерпретируемый язык программирования высокого уровня.

### Переменные и типы данных

В Python переменные создаются простым присваиванием:

```python
name = "Иван"
age = 25
height = 1.75
is_student = True
```

### Функции

Функции определяются с помощью ключевого слова `def`:

```python
def greet(name):
    """Приветствует пользователя по имени."""
    return f"Привет, {name}!"

result = greet("Мир")
print(result)
```

### Работа со списками

```python
fruits = ["яблоко", "банан", "апельсин"]
fruits.append("груша")
for fruit in fruits:
    print(fruit)
```

## Работа с файлами

```python
# Чтение файла
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Запись в файл
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Новые данные")
```

## Заключение

Python - отличный язык для начинающих программистов.

