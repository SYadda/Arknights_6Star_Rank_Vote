import os
import time
from typing import Any

from litestar import Request, Response, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.stores.base import Store
from litestar.types import Scope
from msgspec import Struct, msgpack
from redis.asyncio import Redis, RedisError

from app.server.core import _redis_script

MAX_IP_LIMIT = int(os.getenv("ARKVOTES_MAX_IP_LIMIT", "100"))
BASE_MULTIPLIER = 100
LOW_MULTIPLIER = 1


class SaveScoreReq(Struct):
    win_id: int
    lose_id: int
    code: str
    timestamp: float = time.time()


class Ballot(Struct):
    code: str
    win: int
    lose: int
    ip: str
    user_agent: str
    multiplier: int


async def get_client_identifier(request: Request) -> str:
    host = request.client.host if request.client else "anonymous"
    return request.headers.get("X-Forwarded-For") or request.headers.get("X-Real-IP") or host


async def validate_ballot(code: str, ballot_store: Store) -> tuple[int, int]:
    ballot_info = await ballot_store.get(code)

    if not ballot_info:
        raise HTTPException(detail="Invalid ballot code", status_code=HTTP_400_BAD_REQUEST)

    await ballot_store.delete(code)

    try:
        decoded = ballot_info.decode()
        left, right = decoded.split(",")
        return int(left), int(right)
    except (ValueError, KeyError) as e:
        raise HTTPException(detail="Invalid ballot format", status_code=HTTP_400_BAD_REQUEST) from e


async def calculate_multiplier(identifier: str, redis: Redis) -> int:
    counter_key = f"ip_counter:{identifier}"
    current = await redis.incr(counter_key)
    return BASE_MULTIPLIER if current <= MAX_IP_LIMIT or MAX_IP_LIMIT < 0 else LOW_MULTIPLIER


@post("/save_score")
async def save_score(
    scope: Scope,
    request: Request[Any, Any, Any],
    data: SaveScoreReq,
    redis: Redis,
) -> Response[Any]:
    win_id = data.win_id
    lose_id = data.lose_id

    app = scope["app"]

    ballot_store = app.stores.get("ballot")
    try:
        left_id, right_id = await validate_ballot(data.code, ballot_store)
    except HTTPException as e:
        return Response(status_code=e.status_code, content=e.detail)

    if win_id not in {left_id, right_id} or lose_id not in {left_id, right_id}:
        return Response(status_code=HTTP_400_BAD_REQUEST, content="Invalid match participants")

    if win_id == lose_id:
        return Response(status_code=HTTP_400_BAD_REQUEST, content="Winner cannot be loser")

    identifier = await get_client_identifier(request)
    try:
        multiplier = await calculate_multiplier(identifier, redis)
    except RedisError as e:
        raise HTTPException(
            detail=f"Counter operation failed: {e!s}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e

    ballot = Ballot(
        code=data.code,
        win=win_id,
        lose=lose_id,
        ip=identifier,
        user_agent=request.headers.get("User-Agent", "unknown"),
        multiplier=multiplier,
    )

    try:
        packed_data = msgpack.encode(ballot)
        global _redis_script  # noqa: PLW0603
        if _redis_script is None:
            from app.server.core import lua_script

            _redis_script = redis.register_script(lua_script)

        await _redis_script(
            keys=None,
            args=[ballot.code, data.timestamp, packed_data, ballot.win, ballot.lose, ballot.multiplier],
        )

        return Response(status_code=200, content="success")
    except RedisError as e:
        raise HTTPException(detail=f"Redis operation failed: {e!s}", status_code=HTTP_500_INTERNAL_SERVER_ERROR) from e
