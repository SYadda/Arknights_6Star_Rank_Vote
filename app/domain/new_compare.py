import random

from litestar import post
from litestar.types import Scope
from msgspec import Struct

from app.data import operators_id_list, reverse_operators_id_dict
from app.snowflake import snowflake_instance


class NewCompareResponse(Struct):
    left: str
    right: str
    code: str


@post("/new_compare", status_code=200)
async def new_compare(scope: Scope) -> NewCompareResponse:
    a, b = random.sample(operators_id_list, 2)

    code_random = str(snowflake_instance.next_value())
    ballot_store = scope["app"].stores.get("ballot")
    await ballot_store.set(code_random, f"{a},{b}", expires_in=3600)

    return NewCompareResponse(
        left=reverse_operators_id_dict[a],
        right=reverse_operators_id_dict[b],
        code=code_random,
    )
