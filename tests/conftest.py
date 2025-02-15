from collections.abc import AsyncIterator

from app.asgi import app

from litestar.app import Litestar
from litestar.testing import AsyncTestClient
import pytest


@pytest.fixture(scope="function")
async def test_client() -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app=app) as client:
        yield client
