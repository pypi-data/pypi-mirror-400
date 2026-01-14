---
title: Docker Setup Guide
tags: [docker, devops, containers]
created: 2024-02-15
---

# Docker Setup Guide

Руководство по настройке Docker для разработки.

## Dockerfile примеры

### Python приложение

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### Node.js приложение

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
```

## Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Полезные команды

```bash
# Сборка образа
docker build -t myapp .

# Запуск контейнера
docker run -p 8000:8000 myapp

# Просмотр логов
docker logs -f container_name

# Остановка всех контейнеров
docker stop $(docker ps -q)
```

