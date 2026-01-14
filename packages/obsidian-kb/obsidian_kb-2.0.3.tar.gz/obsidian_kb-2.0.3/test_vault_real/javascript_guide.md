---
title: JavaScript Guide
tags: [javascript, web, programming]
created: 2024-01-20
---

# JavaScript Guide

Руководство по JavaScript для веб-разработки.

## Основы JavaScript

JavaScript - это язык программирования для веб-разработки.

### Переменные

```javascript
const name = "Иван";
let age = 25;
var city = "Москва";
```

### Функции

```javascript
function greet(name) {
    return `Привет, ${name}!`;
}

// Стрелочная функция
const greetArrow = (name) => `Привет, ${name}!`;
```

### Асинхронный код

```javascript
async function fetchData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Ошибка:", error);
    }
}
```

### Работа с DOM

```javascript
document.addEventListener("DOMContentLoaded", () => {
    const button = document.querySelector("#myButton");
    button.addEventListener("click", () => {
        alert("Кнопка нажата!");
    });
});
```

## Заключение

JavaScript - мощный язык для создания интерактивных веб-приложений.

