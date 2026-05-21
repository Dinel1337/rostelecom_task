

set -e

cleanup() {
    echo "Очистка ресурсов..."
    docker compose down
}
trap cleanup EXIT

echo "Запуск инфраструктуры..."
docker compose up -d

check_health() {
    local container_name=$1
    echo "Ждем готовности $container_name..."
    local timeout=60
    local count=0
    until [ "$(docker inspect -f '{{.State.Health.Status}}' $container_name)" == "healthy" ]; do
        if [ $count -ge $timeout ]; then
            echo "Ошибка: $container_name не поднялся за $timeout секунд!"
            exit 1
        fi
        sleep 2
        count=$((count + 2))
    done
}

check_health rostelecom_task-postgres-1
check_health rostelecom_task-rabbitmq-1

echo "Ожидание готовности API на http://localhost:8000..."
max_retries=30
retry_count=0

until curl -s -o /dev/null http://localhost:8000/; do
    if [ $retry_count -ge $max_retries ]; then
        echo "Ошибка: API не ответил за 60 секунд!"
        exit 1
    fi
    echo "API еще не готов, ждем 2 секунды..."
    sleep 2
    retry_count=$((retry_count + 1))
done

echo "API готов к приему запросов!"

echo "Запуск тестов..."
uv run pytest tests/api/test_e2e_flow.py --verbose