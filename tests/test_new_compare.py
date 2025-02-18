from litestar import Litestar
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient
import pytest

pytestmark = pytest.mark.anyio

async def test_new_compare(test_client: AsyncTestClient[Litestar]):
    response = await test_client.post("/new_compare")
    assert response.status_code == HTTP_200_OK

    data = response.json()
    left_name = data["left"]
    right_name = data["right"]
    code = data["code"]

    response = await test_client.post(
        "/save_score",
        json={"win_name": left_name, "lose_name": right_name, "code": code},
    )

    assert response.status_code == HTTP_200_OK
