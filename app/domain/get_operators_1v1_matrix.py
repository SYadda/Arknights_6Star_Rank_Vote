from litestar import post
from redis.asyncio import Redis
from msgspec import Struct
from app.data import operator_ids

CACHE_INTERVAL_SECONDS = 10

@post("/get_operators_1v1_matrix", status_code=200, cache=CACHE_INTERVAL_SECONDS)
async def get_operators_1v1_matrix(redis: Redis) -> str | None:
    values = await redis.get("op_matrix")
    return values