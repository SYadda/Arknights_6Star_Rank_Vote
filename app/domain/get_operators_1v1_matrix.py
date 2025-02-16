from typing import Any
from litestar import post
from litestar.types import Scope
from msgspec import Struct
from app.data import operator_ids
from app.snowflake import snowflake_instance
from litestar import Request, post
from redis.asyncio import Redis, RedisError

CACHE_INTERVAL_SECOND = 300 

async def vaildRequestOperatorsId(id_need_check: list[int]):
    if id_need_check is None or len(id_need_check) == 0:
        return None
    for oid in id_need_check:
        if oid not in operator_ids:
            return None
    return id_need_check


@post("/get_operators_1v1_matrix", status_code=200, cache=CACHE_INTERVAL_SECOND)
async def get_operators_1v1_matrix(
    scope: Scope,
    request: Request[Any, Any, Any], 
    data: list[int],
    redis: Redis) -> list[list]:
    op_list = await vaildRequestOperatorsId(data)
    if op_list is None:
        return [[]]
    all_keys = [f"op_matrix:{i}:{j}" for i in op_list for j in op_list]
    values = await redis.mget(*all_keys)
    matrix = [[ int(value) / 100 if (value := values[i * len(op_list) + j]) is not None else 0 
        for j in range(len(op_list))]
        for i in range((len(values) + len(op_list) - 1) // len(op_list))
    ]
    return matrix