---
title: API Design Best Practices
tags: [api, design, rest, backend]
created: 2024-02-10
---

# API Design Best Practices

Руководство по проектированию REST API.

## Принципы REST API

### Использование HTTP методов

- GET для получения данных
- POST для создания ресурсов
- PUT для полного обновления
- PATCH для частичного обновления
- DELETE для удаления

### Примеры эндпоинтов

```python
# Flask пример
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    users = db.get_all_users()
    return jsonify(users)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.get_user(user_id)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(user)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    user = db.create_user(data)
    return jsonify(user), 201
```

### Обработка ошибок

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400
```

## Версионирование API

Используйте версии в URL: `/api/v1/users`, `/api/v2/users`

## Аутентификация

```python
from functools import wraps
from flask import request

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not validate_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

