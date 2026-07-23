# Metrics API

## `GET /api/metrics`

Возвращает агрегированную статистику обращений из PostgreSQL.

### Response

`200 OK`

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

### Что входит в метрики

- общее количество обращений;
- успешные AI-ответы;
- обращения, ушедшие в fallback;
- email-failures;
- распределение по категориям.

### curl example

```bash
curl http://localhost:8000/api/metrics
```

