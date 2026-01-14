# Тестовые запросы для Intent Detection

**Цель:** Проверить точность определения intent для различных типов запросов  
**Целевая точность:** >90%  
**Дата создания:** 2025-01-21

---

## 1. METADATA_FILTER (20 запросов)

Запросы только с фильтрами, без текстового запроса.

1. `tags:python`
2. `tags:meeting tags:important`
3. `type:note`
4. `tags:project tags:active`
5. `type:meeting`
6. `tags:todo tags:urgent`
7. `type:document`
8. `tags:reference`
9. `tags:personal tags:private`
10. `type:guide`
11. `tags:work tags:priority`
12. `type:article`
13. `tags:archive`
14. `tags:project tags:completed`
15. `type:template`
16. `tags:learning`
17. `tags:health tags:exercise`
18. `type:recipe`
19. `tags:finance tags:budget`
20. `tags:travel tags:planning`

---

## 2. KNOWN_ITEM (20 запросов)

Запросы, ссылающиеся на конкретные файлы или известные документы.

1. `README.md`
2. `CHANGELOG`
3. `LICENSE`
4. `CONTRIBUTING.md`
5. `INSTALLATION`
6. `TODO.md`
7. `api_design.md`
8. `configuration.md`
9. `database_queries.md`
10. `docker_setup.md`
11. `javascript_guide.md`
12. `python_tutorial.md`
13. `ARCHITECTURE.md`
14. `DEVELOPER_GUIDE.md`
15. `API_DOCUMENTATION.md`
16. `QUICK_START.md`
17. `TROUBLESHOOTING.md`
18. `BEST_PRACTICES.md`
19. `FAQ.md`
20. `README`

---

## 3. PROCEDURAL (20 запросов)

How-to запросы, инструкции, руководства.

1. `how to install`
2. `как настроить`
3. `steps to configure`
4. `guide to setup`
5. `tutorial on using`
6. `инструкция по установке`
7. `how to use`
8. `как создать`
9. `setup guide`
10. `installation instructions`
11. `how to configure settings`
12. `настроить подключение`
13. `tutorial for beginners`
14. `how to deploy`
15. `инструкция по настройке`
16. `guide to getting started`
17. `how to build`
18. `как установить`
19. `setup tutorial`
20. `how to get started`

---

## 4. EXPLORATORY (20 запросов)

Вопросы, исследовательские запросы.

1. `что такое`
2. `what is`
3. `как работает`
4. `how does it work`
5. `почему используется`
6. `why use`
7. `когда применять`
8. `when to use`
9. `где найти`
10. `where to find`
11. `кто использует`
12. `who uses`
13. `какой выбрать`
14. `which one to choose`
15. `сколько стоит`
16. `how much does it cost`
17. `зачем нужен`
18. `what is the purpose`
19. `как выбрать`
20. `how to choose`

---

## 5. SEMANTIC (20 запросов)

Семантические запросы для поиска по содержанию.

1. `Python async programming`
2. `database optimization techniques`
3. `REST API design patterns`
4. `machine learning algorithms`
5. `web development best practices`
6. `контейнеризация приложений`
7. `distributed systems architecture`
8. `security best practices`
9. `performance optimization`
10. `code review guidelines`
11. `тестирование программного обеспечения`
12. `microservices architecture`
13. `data structures and algorithms`
14. `cloud computing strategies`
15. `agile development methodologies`
16. `continuous integration and deployment`
17. `системы управления версиями`
18. `monitoring and logging`
19. `scalability patterns`
20. `user interface design principles`

---

## Формат результатов тестирования

Для каждого запроса записывайте:

```
Запрос: [текст запроса]
Ожидаемый intent: [METADATA_FILTER | KNOWN_ITEM | PROCEDURAL | EXPLORATORY | SEMANTIC]
Определённый intent: [результат системы]
Confidence: [значение уверенности]
Правильно: [Да/Нет]
Комментарий: [если есть проблемы]
```

---

## Метрики успеха

- **Точность:** Количество правильных определений / 100 * 100%
- **Целевая точность:** >90%
- **Проблемные случаи:** Задокументировать запросы с неправильным определением intent

