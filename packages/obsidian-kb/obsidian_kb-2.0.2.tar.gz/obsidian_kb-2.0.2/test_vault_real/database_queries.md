---
title: Database Queries
tags: [database, sql, queries]
created: 2024-02-01
---

# Database Queries

Коллекция полезных SQL запросов.

## Основные запросы

### SELECT

```sql
SELECT * FROM users WHERE age > 18;
SELECT name, email FROM users ORDER BY name;
```

### JOIN

```sql
SELECT u.name, p.title
FROM users u
INNER JOIN posts p ON u.id = p.user_id;
```

### Агрегация

```sql
SELECT 
    category,
    COUNT(*) as total,
    AVG(price) as avg_price
FROM products
GROUP BY category;
```

## PostgreSQL специфичные запросы

```sql
-- Использование JSONB
SELECT data->>'name' as name
FROM documents
WHERE data @> '{"status": "active"}';

-- Оконные функции
SELECT 
    name,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employees;
```

## Оптимизация

```sql
-- Создание индекса
CREATE INDEX idx_users_email ON users(email);

-- EXPLAIN для анализа
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

