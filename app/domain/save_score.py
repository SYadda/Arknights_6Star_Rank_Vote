import time
from typing import Any

from app.cache import record_cache, save_batch
from app.data import operators_id_dict, reverse_operators_id_dict

from litestar import Request, Response, post
from litestar.types import Scope
from msgspec import Struct
from sqlalchemy.ext.asyncio import AsyncSession


class SaveScoreReq(Struct):
    win_name: str
    lose_name: str
    code: str


@post("/save_score")
async def save_score(
    scope: Scope,
    request: Request[Any, Any, Any],
    data: SaveScoreReq,
    db_session: AsyncSession,
) -> Response[Any]:
    win_name = data.win_name
    lose_name = data.lose_name
    code = data.code
    app = scope["app"]

    ballot_store = app.stores.get("ballot")
    ballot_info = await ballot_store.get(code)
    if ballot_info is None:
        return Response(status_code=429, content="")
    await ballot_store.delete(code)

    left, right = ballot_info.decode().split(",")
    left_name = reverse_operators_id_dict[int(left)]
    right_name = reverse_operators_id_dict[int(right)]

    if win_name not in (left_name, right_name):
        return Response(status_code=429, content="")

    if lose_name not in (left_name, right_name):
        return Response(status_code=429, content="")

    host = request.client.host if request.client else "anonymous"
    identifier = (
        request.headers.get("X-Forwarded-For")
        or request.headers.get("X-Real-IP")
        or host
    )

    ip_limit_store = app.stores.get("ip_mul_limiter")
    ip_limit = await ip_limit_store.get(identifier)

    multiplier = 0
    if ip_limit is None:
        await ip_limit_store.set(identifier, b"1")
        multiplier = 100
    else:
        ip_limit = ip_limit.decode()
        if int(ip_limit) > 50:
            multiplier = 1
        else:
            await ip_limit_store.set(identifier, str(int(ip_limit) + 1))
            multiplier = 100

    await record_cache.update_score(
        operators_id_dict[win_name],
        operators_id_dict[lose_name],
        multiplier,
    )

    if int(time.time()) - record_cache.last_save > 10:
        batch = await record_cache.swap_batches()
        await save_batch(db_session, batch)
        record_cache.last_save = int(time.time())

    return Response(status_code=200, content="success")
