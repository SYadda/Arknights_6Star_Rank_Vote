import asyncio
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from litestar import Request, Response, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_423_LOCKED, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.stores.base import Store
from litestar.types import Scope
from msgspec import Struct, msgpack
from redis.asyncio import Redis, RedisError

MAX_IP_LIMIT = int(os.getenv("ARKVOTES_MAX_IP_LIMIT", "100"))
BASE_MULTIPLIER = 100
LOW_MULTIPLIER = 1
LOCK_TIMEOUT = 10
LOCK_RETRIES = 100
LOCK_RETRY_INTERVAL = 0.1


class RedisLock:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.lock_script = self.redis.register_script("""
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
        """)

    @asynccontextmanager
    async def acquire_lock(
        self,
        lock_key: str,
        timeout: int = LOCK_TIMEOUT,
        retries: int = LOCK_RETRIES,
        retry_interval: float = LOCK_RETRY_INTERVAL,
    ):
        token = str(uuid.uuid4())
        lock_acquired = False

        for _ in range(retries):
            if await self.redis.set(lock_key, token, nx=True, ex=timeout):
                lock_acquired = True
                break
            await asyncio.sleep(retry_interval)

        if not lock_acquired:
            raise HTTPException(detail=f"Could not acquire lock for {lock_key}", status_code=HTTP_423_LOCKED)

        try:
            yield
        finally:
            await self.lock_script(keys=[lock_key], args=[token])


class SaveScoreReq(Struct):
    win_id: int
    lose_id: int
    code: str
    timestamp: float = time.time()


class Ballot(Struct):
    code: str
    win: int
    lose: int


async def get_client_identifier(request: Request) -> str:
    host = request.client.host if request.client else "anonymous"
    return request.headers.get("X-Forwarded-For") or request.headers.get("X-Real-IP") or host


async def validate_ballot(code: str, ballot_store: Store) -> tuple[int, int]:
    ballot_info = None
    for _ in range(10):
        ballot_info = await ballot_store.get(code)
        if ballot_info:
            break
        await asyncio.sleep(0.1)

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


async def save_request_to_redis(ballot: Ballot, timestamp: float, redis: Redis):
    packed_data = msgpack.encode(ballot)

    async with redis.pipeline(transaction=True) as pipe:
        await pipe.hset(f"req:{ballot.code}", mapping={"timestamp": timestamp, "data": packed_data})  # pyright: ignore[reportGeneralTypeIssues]

        await pipe.zadd("req_index:by_time", {ballot.code: timestamp})
        await pipe.sadd(f"req_index:by_operator:win:{ballot.win}", ballot.code)  # pyright: ignore[reportGeneralTypeIssues]
        await pipe.sadd(f"req_index:by_operator:lose:{ballot.lose}", ballot.code)  # pyright: ignore[reportGeneralTypeIssues]

        await pipe.execute()


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

    if not {win_id, lose_id} <= {left_id, right_id}:
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

    if "redis_lock" not in app.state:
        app.state["redis_lock"] = RedisLock(redis)
    lock: RedisLock = app.state["redis_lock"]
    win_lock_key = f"lock:{win_id}:win"
    lose_lock_key = f"lock:{lose_id}:lose"
    sorted_locks = sorted([win_lock_key, lose_lock_key])

    ballot = Ballot(code=data.code, win=win_id, lose=lose_id)

    try:
        await save_request_to_redis(ballot, data.timestamp, redis)
        async with lock.acquire_lock(sorted_locks[0]), lock.acquire_lock(sorted_locks[1]):  # noqa: SIM117
            async with redis.pipeline(transaction=True) as pipe:
                pipe.multi()
                pipe.incr(f"{win_id}:win", multiplier)
                pipe.incr(f"{lose_id}:lose", multiplier)
                pipe.incr(f"op_matrix:{win_id}:{lose_id}", multiplier)
                pipe.decr(f"op_matrix:{lose_id}:{win_id}", multiplier)
                await pipe.execute()

        return Response(status_code=200, content="success")

    except RedisError as e:
        raise HTTPException(detail=f"Redis operation failed: {e!s}", status_code=HTTP_500_INTERNAL_SERVER_ERROR) from e
