# API Documentation

Документация API вынесена в отдельные страницы по аналогии с Go-проектом.

## Разделы

- [Contact](./endpoints/contact.md)
- [Health](./endpoints/health.md)
- [Metrics](./endpoints/metrics.md)

## Общие принципы

- REST-стиль с JSON body.
- Все ответы возвращаются в JSON.
- Валидация делается на уровне схем FastAPI/Pydantic.
- Ошибки отдаются с понятным HTTP-status и телом `error`.
- AI-часть не ломает основной сценарий: при сбое провайдера включается fallback.
- Email-ошибка не теряет обращение: запись уже сохранена в базе.

## Базовый workflow

```text
POST /api/contact
  -> validation
  -> rate limit check
  -> AI analysis or fallback
  -> save contact
  -> send owner email
  -> send user email
  -> update metrics
  -> response
```

