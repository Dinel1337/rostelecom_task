import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pytest

@pytest.fixture
def anyio_backend():
    return "asyncio"
