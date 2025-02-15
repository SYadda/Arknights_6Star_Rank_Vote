import random

from litestar import post
from litestar.types import Scope
from msgspec import Struct

from app.data import operator_ids
from app.snowflake import snowflake_instance


class NewCompareResponse(Struct):
    left: int
    right: int
    code: str


@post("/new_compare", status_code=200)
async def new_compare(scope: Scope) -> NewCompareResponse:
    a, b = random.sample(operator_ids, 2)

    code = str(snowflake_instance.next_value())
    ballot_store = scope["app"].stores.get("ballot")
    await ballot_store.set(code, f"{a},{b}", expires_in=3600)

    return NewCompareResponse(
        left=a,
        right=b,
        code=code,
    )
