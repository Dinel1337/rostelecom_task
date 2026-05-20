import sys
from pathlib import Path

# Добавляем корень проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Фикстура для асинхронных тестов (если понадобятся)
import pytest

@pytest.fixture
def anyio_backend():
    return "asyncio"
