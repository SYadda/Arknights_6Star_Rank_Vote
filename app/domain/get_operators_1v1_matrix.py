from itertools import product

from litestar import post
from redis.asyncio import Redis

from app.data import operator_ids

CACHE_INTERVAL_SECONDS = 10


async def validate_operator_ids(ids_to_check: list[int]) -> list[int] | None:
    if not ids_to_check:
        return None
    if any(oid not in operator_ids for oid in ids_to_check):
        return None
    return ids_to_check


@post("/get_operators_1v1_matrix", status_code=200, cache=CACHE_INTERVAL_SECONDS)
async def get_operators_1v1_matrix(data: list[int], redis: Redis) -> list[list[float]]:
    valid_ids = await validate_operator_ids(data)
    if valid_ids is None:
        return [[]]

    redis_keys = [f"op_matrix:{i}:{j}" for i, j in product(valid_ids, repeat=2)]
    values = await redis.mget(*redis_keys)

    matrix_size = len(valid_ids)
    return [
        [
            int(value) / 100 if (value := values[row * matrix_size + col]) is not None else 0
            for col in range(matrix_size)
        ]
        for row in range(matrix_size)
    ]
