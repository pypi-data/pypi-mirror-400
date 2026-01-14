---
title: Configuration Management
tags: [config, settings, environment]
created: 2024-02-20
---

# Configuration Management

Управление конфигурацией в приложениях.

## Переменные окружения

Используйте переменные окружения для конфигурации.

### Python пример

```python
import os
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
```

### Node.js пример

```javascript
require('dotenv').config();

const config = {
    databaseUrl: process.env.DATABASE_URL,
    port: process.env.PORT || 3000,
    nodeEnv: process.env.NODE_ENV || 'development',
};
```

## Файлы конфигурации

### YAML конфигурация

```yaml
database:
  host: localhost
  port: 5432
  name: mydb
  user: admin

server:
  host: 0.0.0.0
  port: 8000
  debug: false
```

### JSON конфигурация

```json
{
  "database": {
    "host": "localhost",
    "port": 5432
  },
  "features": {
    "enable_cache": true,
    "cache_ttl": 3600
  }
}
```

## Заключение

Правильное управление конфигурацией критично для безопасности и гибкости приложения.

