# Contact API

## `POST /api/contact`

Создает обращение с формы обратной связи, запускает AI-анализ, сохраняет запись в PostgreSQL и отправляет email владельцу сайта и пользователю.

### Назначение

- проверить входные данные;
- защититься от спама через rate limiting;
- получить AI-анализ комментария;
- сохранить обращение;
- отправить уведомления;
- вернуть итоговый статус операции.

### Request

`Content-Type: application/json`

```json
{
  "name": "Sergey",
  "phone": "+7 (999) 123-45-67",
  "email": "sergey@example.com",
  "comment": "Please review my portfolio landing page and suggest improvements."
}
```

### Validation rules

- `name` - от 2 до 100 символов
- `phone` - от 7 до 32 символов, только цифры, пробелы, `+`, `(`, `)`, `-`
- `email` - валидный email
- `comment` - от 5 до 2000 символов

### Success response

`201 Created`

```json
{
  "request_id": "72e228db-32f1-41ee-9886-bfd6fe42b165",
  "contact_id": "3e1d2f6d-9f6a-4dcb-8c1b-7a8c2d4b7c90",
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

### Partial email failure

Если SMTP недоступен, обращение сохраняется, а статус уведомлений возвращается как частично успешный.

```json
{
  "notification_status": "partial_failed",
  "warnings": [
    {
      "code": "owner_email_failed",
      "message": "Failed to send owner email"
    }
  ]
}
```

### Error responses

- `422 Unprocessable Entity` - невалидный payload
- `429 Too Many Requests` - превышен rate limit
- `500 Internal Server Error` - неожиданный сбой

### curl example

```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sergey",
    "phone": "+7 (999) 123-45-67",
    "email": "sergey@example.com",
    "comment": "Please review my portfolio landing page and suggest improvements."
  }'
```

### Notes

- AI fallback не останавливает обработку запроса.
- Email-ошибка не отменяет сохранение обращения.
- Все запросы пишутся в файл логов.

