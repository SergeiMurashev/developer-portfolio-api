# Health API

## `GET /api/health`

Проверяет статус сервиса и доступность PostgreSQL.

### Response

`200 OK`

```json
{
  "status": "ok",
  "service": "developer-portfolio-api",
  "env": "development",
  "database": "ok"
}
```

### Behavior

- `status = ok` - сервис работает и база доступна
- `status = degraded` - сервис жив, но PostgreSQL недоступен

### curl example

```bash
curl http://localhost:8000/api/health
```

