> **Комент разраба**
> 
> * Не ругайтесь на русские `message` - это тестовое задание, не production решение.
> * Для HTTPS используется самоподписной сертификат. Браузер может показывать предупреждение - это нормально для локального тестирования.

## Компоненты

| Сервис | Порт | Описание |
|--------|------|----------|
| Service A | 8001 | Заглушка, имитирует активацию оборудования (ждёт 60 секунд) |
| Service B | 8000 | Основной API для создания и проверки задач |
| Consumer | - | Фоновый воркер, обрабатывает задачи из очереди |
| PostgreSQL | 5432 | Хранилище задач |
| RabbitMQ | 5672 | Брокер сообщений между сервисами |

## Запуск

### Требования
- Docker & Docker Compose

### Быстрый старт (Docker)

```bash
git clone https://github.com/Dinel1337/rostelecom_task.git
cd rostelecom_task
docker-compose up --build
```
## API Документация
После запуска сервиса B документация доступна по адресу:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Веб-интерфейс
Для удобства тестирования реализован простой веб-интерфейс:

- http://localhost:8000/api/v1/ — форма создания и проверки задач

## Примеры запросов
### Создать задачу
```bash
curl -X POST http://localhost:8000/api/v1/equipment/cpe/ABC123 \
  -H "Content-Type: application/json" \
  -d '{
    "timeoutInSeconds": 60,
    "parameters": {
      "username": "admin",
      "password": "admin",
      "vlan": 534,
      "interfaces": [1,2,3,4]
    }
  }'
```
### Ответ:
```json
{
  "code": 200,
  "taskId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Проверить статус
```bash
curl http://localhost:8000/api/v1/equipment/cpe/ABC123/task/550e8400-e29b-41d4-a716-446655440000
```

### Ответ (завершено):

```json
{
  "code": 200,
  "message": "Выполнено"
}
```

### Ответ (выполняется):

```json
{
  "code": 204,
  "message": "Таска все еще в обработке!"
}
```

## Мониторинг
- RabbitMQ Management: http://localhost:15672 (guest/guest)
- Healthcheck Service A: http://localhost:8001/api/v1/health
- Healthcheck Service B: http://localhost:8000/api/v1/health