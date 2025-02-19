from litestar import post
from redis.asyncio import Redis

CACHE_INTERVAL_SECONDS = 10


@post("/get_operators_1v1_matrix", status_code=200, cache=CACHE_INTERVAL_SECONDS)
async def get_operators_1v1_matrix(redis: Redis) -> str | None:
    return await redis.get("op_matrix")

