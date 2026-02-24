# QA Final Project — Tandoor Smoke Testing (Meal Plan)

## Описание
Проект дипломной работы по автотестированию: smoke-тестирование веб-приложения **Tandoor** (раздел **Meal Plan**) с использованием:
- UI автотестов (Selenium WebDriver)
- API тестов (requests)
- отчётов Allure

## Стек
- Python 3.13
- pytest
- selenium
- requests
- python-dotenv
- allure-pytest

## Структура проекта
- `api/` — API-клиент для работы с Tandoor
- `pages/` — Page Object Model (страницы UI)
- `tests/` — UI и API тесты
- `conftest.py` — фикстуры pytest
- `pytest.ini` — маркеры и настройки pytest

## Переменные окружения
Создай файл `.env` в корне проекта:

```env
BASE_URL=https://app.tandoor.dev
TANDOOR_TOKEN=your_token_here
TANDOOR_USERNAME=your_email_here
TANDOOR_PASSWORD=your_password_here