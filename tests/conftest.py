from collections.abc import AsyncIterator

import pytest
from litestar.app import Litestar
from litestar.testing import AsyncTestClient

from app.asgi import create_app


@pytest.fixture(scope="function")
async def test_client() -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app=create_app()) as client:
        yield client
