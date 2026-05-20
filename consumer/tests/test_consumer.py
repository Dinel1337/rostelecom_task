from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.consumer_service import ConsumerService


@pytest.mark.asyncio
async def test_process_task_success():
    rabbitmq = AsyncMock()

    consumer = ConsumerService(rabbitmq)

    task_data = {
        "task_id": "task-1",
        "equipment_id": "ABC123",
        "parameters": {
            "username": "admin",
            "password": "admin"
        }
    }

    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        await consumer.process_task(task_data)

    rabbitmq.publish_result.assert_called_once_with(
        "task-1",
        "completed"
    )


@pytest.mark.asyncio
async def test_process_task_failed_status():
    rabbitmq = AsyncMock()

    consumer = ConsumerService(rabbitmq)

    task_data = {
        "task_id": "task-2",
        "equipment_id": "ABC123",
        "parameters": {
            "username": "admin",
            "password": "admin"
        }
    }

    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        await consumer.process_task(task_data)

    rabbitmq.publish_result.assert_called_once_with(
        "task-2",
        "failed"
    )


@pytest.mark.asyncio
async def test_process_task_exception():
    rabbitmq = AsyncMock()

    consumer = ConsumerService(rabbitmq)

    task_data = {
        "task_id": "task-3",
        "equipment_id": "ABC123",
        "parameters": {
            "username": "admin",
            "password": "admin"
        }
    }

    with (
        patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post,
        patch("asyncio.sleep", new_callable=AsyncMock)
    ):
        mock_post.side_effect = Exception("Connection error")

        await consumer.process_task(task_data)

    rabbitmq.publish_result.assert_called_once_with(
        "task-3",
        "failed"
    )