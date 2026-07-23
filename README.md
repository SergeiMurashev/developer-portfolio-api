# developer-portfolio-api

Backend-сервис для лендинг-презентации разработчика на `FastAPI` + `PostgreSQL` с AI-интеграцией, email-уведомлениями, rate limiting, логированием в файл и Swagger/OpenAPI.

## Что уже закрыто по ТЗ

- `POST /api/contact`
- валидация `name`, `phone`, `email`, `comment`
- отправка письма владельцу сайта
- отправка копии письма пользователю
- AI-анализ обращения с graceful fallback
- rate limiting
- логирование запросов в файл
- `GET /api/health`
- `GET /api/metrics`
- Swagger/OpenAPI документация
- `.env`-конфигурация
- глобальная обработка ошибок
- CORS
- слоистая архитектура

## Что важно знать заранее

- Это production-shaped MVP, а не “игрушечный” пример.
- Если AI-провайдер недоступен или ключ не задан, сервис не падает, а продолжает работу через fallback.
- Email-отправка сделана синхронно. Если SMTP недоступен, обращение сохраняется, а статус уведомлений возвращается как частично неуспешный.

## Стек

- Python 3.9+
- FastAPI
- PostgreSQL 16
- `psycopg2-binary`
- `httpx`
- SMTP
- Groq API через OpenAI-compatible endpoint
- Docker / Docker Compose

## Архитектура

Структура повторяет Go-подход и разделяет ответственность по слоям:

- `app/api/handlers` - HTTP-ручки
- `app/usecases` - бизнес-сценарии
- `app/services` - AI и email
- `app/repositories` - работа с PostgreSQL
- `app/infrastructure` - БД, SMTP, AI client, file storage, logging
- `app/core` - конфиг, исключения, обработчики ошибок

Основной поток:

1. Handler принимает JSON.
2. FastAPI валидирует payload.
3. Use case проверяет rate limit.
4. AI-service анализирует комментарий.
5. Контакт сохраняется в PostgreSQL.
6. Email-service отправляет письма владельцу и пользователю.
7. Метрики обновляются.
8. API возвращает ответ.

## Локальный запуск

### 1. Установить зависимости

```bash
pip install -r requirements.txt
```

### 2. Создать `.env`

Скопируй `.env.example` в `.env` и заполни значения.

### 3. Поднять базу и MailHog

```bash
docker compose up -d db mailhog
```

### 4. Запустить API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Открыть документацию

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Запуск через Docker

```bash
docker compose up --build
```

После старта:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5441`
- MailHog UI: `http://localhost:8025`

## Переменные окружения

Пример базовой конфигурации:

```env
APP_NAME=developer-portfolio-api
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_DIR=logs
DATA_DIR=data
CORS_ORIGINS=*
DATABASE_URL=postgresql://zephy_db:1234@localhost:5441/zephy_db
DATABASE_CONNECT_TIMEOUT_SECONDS=5
POSTGRES_HOST_PORT=5441

OWNER_EMAIL=owner@example.com
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=portfolio@example.com
SMTP_USE_TLS=false
SMTP_TIMEOUT_SECONDS=10

OPENAI_API_KEY=your_groq_or_openai_api_key
OPENAI_MODEL=llama-3.1-8b-instant
OPENAI_BASE_URL=https://api.groq.com/openai/v1
AI_TIMEOUT_SECONDS=12

RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_HASH_SECRET=change-me
```

### Как тестировать AI

Для проверки AI вживую достаточно указать любой рабочий ключ Groq или совместимого OpenAI-провайдера:

- `OPENAI_API_KEY` - ваш ключ
- `OPENAI_BASE_URL=https://api.groq.com/openai/v1`
- `OPENAI_MODEL=llama-3.1-8b-instant`

Если ключ не задан, сервис продолжит работать через fallback и вернёт ответ без AI-обогащения.

## База данных

Схема создаётся автоматически при старте PostgreSQL.

Тестовые обращения не захардкожены и не заливаются автоматически. Данные появляются только через реальные запросы к `POST /api/contact`.

Файл схемы:

- [migrations/schema.sql](/C:/Dev/GolandProjects/developer-portfolio-api/migrations/schema.sql)

Ручная проверка:

```bash
psql -h localhost -p 5441 -U zephy_db -d zephy_db -f migrations/schema.sql
```

## API

Подробная документация по ручкам вынесена отдельно:

- [docs/index.md](/C:/Dev/GolandProjects/developer-portfolio-api/docs/index.md)
- [docs/endpoints/contact.md](/C:/Dev/GolandProjects/developer-portfolio-api/docs/endpoints/contact.md)
- [docs/endpoints/health.md](/C:/Dev/GolandProjects/developer-portfolio-api/docs/endpoints/health.md)
- [docs/endpoints/metrics.md](/C:/Dev/GolandProjects/developer-portfolio-api/docs/endpoints/metrics.md)

### `POST /api/contact`

Создаёт обращение, запускает AI-анализ, сохраняет контакт, отправляет письма и возвращает итоговый статус.

Request body:

```json
{
  "name": "Sergey",
  "phone": "+7 (999) 123-45-67",
  "email": "sergey@example.com",
  "comment": "Please review my portfolio landing page and suggest improvements."
}
```

Success response `201 Created`:

```json
{
  "request_id": "uuid",
  "contact_id": "uuid",
  "ai": {
    "provider": "groq",
    "status": "success",
    "category": "general",
    "sentiment": "neutral",
    "priority": "low",
    "summary": "Request for review of portfolio landing page",
    "suggested_reply": "Thank you for reaching out...",
    "fallback_reason": null
  },
  "owner_email": {
    "status": "sent",
    "error": null
  },
  "user_email": {
    "status": "sent",
    "error": null
  },
  "notification_status": "sent",
  "warnings": []
}
```

Типовые ошибки:

- `422` - некорректные входные данные
- `429` - превышен rate limit
- `500` - внутренняя ошибка

### `GET /api/health`

Возвращает статус приложения и PostgreSQL.

Response:

```json
{
  "status": "ok",
  "service": "developer-portfolio-api",
  "env": "development",
  "database": "ok"
}
```

### `GET /api/metrics`

Возвращает агрегированную статистику обращений из PostgreSQL.

Response:

```json
{
  "total_contacts": 13,
  "ai_success": 9,
  "ai_fallback": 4,
  "email_failures": 1,
  "categories": {
    "general": 8,
    "job_offer": 3,
    "project_request": 2
  }
}
```

## Логирование и хранение данных

- `logs/app.log` - файл приложения
- `data/request_logs.jsonl` - поток запросов
- `contacts` - источник истины по обращениям
- `rate_limits` - защита от спама

## Что проверено локально

Проверялось прямыми JSON-запросами к живому контейнеру, не только тестами:

- `GET /api/health` - `200`
- `GET /api/metrics` - `200`
- корректный `POST /api/contact` - `201`
- невалидный `POST /api/contact` - `422`
- превышение rate limit - `429`
- падение SMTP - `201` с `notification_status: partial_failed`
