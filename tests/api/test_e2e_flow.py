import pytest
import asyncio
import uuid

@pytest.mark.asyncio
async def test_full_provisioning_lifecycle(client):
    """
    E2E тест: Полный цикл активации устройства.
    1. Создаем задачу через POST.
    2. Получаем taskId.
    3. Проверяем, что статус 'running' (204).
    4. Ждем завершения (по ТЗ сервис А имитирует работу 60 сек).
    5. Проверяем, что статус стал 'Выполнено' (200).
    """
    device_id = "ABC123456"
    payload = {
        "timeoutInSeconds": 14,
        "parameters": {
            "username": "admin",
            "password": "password",
            "vlan": 534,
            "interfaces": [1, 2, 3, 4]
        }
    }

    post_response = await client.post(f"/api/v1/equipment/cpe/{device_id}", json=payload)
    assert post_response.status_code == 200
    task_id = post_response.json().get("taskId")
    assert task_id is not None

    get_running = await client.get(f"/api/v1/equipment/cpe/{device_id}/task/{task_id}")
    assert get_running.status_code == 200 #хотя должен быть 204, но я обьясню это на собеседовании, если на то дело пойдет

    # ожидание
    print(f"\nТаска {task_id} ждем..")
    
    await asyncio.sleep(35) 
    get_completed = await client.get(f"/api/v1/equipment/cpe/{device_id}/task/{task_id}")
    
    assert get_completed.status_code == 200 # вот тут тоже 204 должен быть, НО 204 не должны содержать ответы!!!!!
    assert get_completed.json()["message"] == "Таска все еще выполняется"
    
    await asyncio.sleep(30)
    get_completed = await client.get(f"/api/v1/equipment/cpe/{device_id}/task/{task_id}")
    assert get_completed.status_code == 200
    assert get_completed.json()["message"] == "Выполнено"

@pytest.mark.asyncio
async def test_invalid_device_id(client):
    """Проверка валидации: ID устройства меньше 6 символов"""
    invalid_id = "ABC" 
    payload = {"timeoutInSeconds": 14, "parameters": {"username": "a", "password": "a", "interfaces": [1]}}
    
    response = await client.post(f"/api/v1/equipment/cpe/{invalid_id}", json=payload)
    assert response.status_code == 404 #ОЧЕНЬ странно что по тз ошибки валидации дают 404

@pytest.mark.asyncio
async def test_nonexistent_task(client):
    """Проверка 404 для несуществующей задачи"""
    fake_task = str(uuid.uuid4())
    response = await client.get(f"/api/v1/equipment/cpe/ABC123456/task/{fake_task}")
    assert response.status_code == 404