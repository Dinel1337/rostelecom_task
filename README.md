> **Комент разраба**
> 
> * Не ругайтесь на русские `message` - это тестовое задание, не production решение.
> * Для HTTPS используется самоподписной сертификат. Браузер может показывать предупреждение - это нормально для локального тестирования.
> * Так же немного странно, 204 статусы с телами ответа???Или пайтон 2.7??Тела ответа в формате списков:)).
> * А так интересное тестовое, скорее всего это регистрация какого-либо устройства, с минимальной микросервисной архитектурой.

## Компоненты

| Сервис | Порт | Описание |
|--------|------|----------|
| Service A | 8001 | Заглушка, имитирует активацию оборудования (ждёт 60 секунд) |
| Service B | 8000 | Основной API для создания и проверки задач |
| Consumer | - | Фоновый воркер, обрабатывает задачи из очереди |
| PostgreSQL | 5432 | Хранилище задач |
| RabbitMQ | 5672 | Брокер сообщений между сервисами |

## Запуск

```bash
cp .env.example .env
cp service_b/.env.example service_b/.env
cp consumer/.env.example consumer/.env
```

### Требования
- Docker & Docker Compose

### Быстрый старт (Docker)

```bash
git clone https://github.com/Dinel1337/rostelecom_task.git
cd rostelecom_task
docker-compose up --build
```

## Автоматический деплой (Ansible)

В проекте настроена автоматизация развертывания с помощью Ansible. Плейбук полностью автономен: если на целевом сервере не установлен Docker, Ansible установит и настроит его автоматически.

### Инструкция по запуску:
Установите Ansible на управляющую машину (если еще не установлен):
```bash
sudo apt update && sudo apt install ansible -y
```

Откройте файл ansible/inventory.ini и укажите IP-адрес вашего целевого сервера (или оставьте localhost).

Запустите сценарий деплоя:

```Bash
ansible-playbook -i ansible/inventory.ini ansible/deploy.ansible.yml
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

### Архитектурная схема компонентов (System Topology)

```mermaid
graph TD
    %% Стиль для внешних и внутренних элементов
    classDef clientStyle fill:#f9f,stroke:#333,stroke-width:2px;
    classDef serviceStyle fill:#bbf,stroke:#333,stroke-width:1px;
    classDef infraStyle fill:#f96,stroke:#333,stroke-width:1px;

    Client[Пользователь / Скрипт]:::clientStyle
    
    subgraph "Инфраструктура Docker Compose"
        Nginx[Nginx Reverse Proxy]:::serviceStyle
        SB[Service B <br> FastAPI Frontend]:::serviceStyle
        DB[(PostgreSQL <br> Хранилище задач)]:::infraStyle
        RMQ{RabbitMQ <br> Брокер сообщений}:::infraStyle
        CNS[Consumer <br> Фоновый воркер]:::serviceStyle
        SA[Service A <br> Синхронная заглушка]:::serviceStyle
    end

    %% Потоки данных и протоколы
    Client -- "HTTPS (внешний порт 443/80)" --> Nginx
    Nginx -- "HTTP (проксирование порт 8000)" --> SB
    
    SB -- "SQL (psycopg2)" --> DB
    SB -- "AMQP (Публикация задач)" --> RMQ
    RMQ -- "AMQP (Получение результатов)" --> SB

    RMQ -- "AMQP (Извлечение задач)" --> CNS
    CNS -- "AMQP (Отправка результатов)" --> RMQ
    
    CNS -- "HTTP (Синхронный вызов 60 сек)" --> SA

    %% Дополнительная связь для healthcheck (которую мы чинили)
    SB -- "curl проверка готовности" --> SA