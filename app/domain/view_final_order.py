from litestar import get
from msgspec import Struct
from redis.asyncio import Redis

from app.data import operator_ids, reverse_operators_id_dict


class ViewFinalOrderResponse(Struct):
    name: list[str]
    score: list[str]
    rate: list[str]
    count: str


@get("/view_final_order", status_code=200, cache=10)
async def view_final_order(
    redis: Redis,
) -> ViewFinalOrderResponse:
    num_operators = len(operator_ids)

    win_keys = [f"{oid}:win" for oid in operator_ids]
    lose_keys = [f"{oid}:lose" for oid in operator_ids]
    all_keys = win_keys + lose_keys

    values = await redis.mget(*all_keys)
    win_counts = [int(v) if v is not None else 0 for v in values[:num_operators]]
    lose_counts = [int(v) if v is not None else 0 for v in values[num_operators:]]

    operators_data = {
        oid: {"win": win_counts[i], "lose": lose_counts[i], "name": reverse_operators_id_dict[oid]}
        for i, oid in enumerate(operator_ids)
    }

    total_data = await redis.zcard("req_index:by_time")

    results = []
    for oid, data in operators_data.items():
        win: int = data["win"]
        lose: int = data["lose"]

        total_games = win + lose
        rate = (win / total_games * 100) if total_games else 0.0

        results.append({"name": data["name"], "score": (win - lose) / 100, "rate": rate, "oid": oid})

    sorted_results = sorted(results, key=lambda x: x["rate"], reverse=True)

    return ViewFinalOrderResponse(
        name=[item["name"] for item in sorted_results],
        score=[f"{item['score']:.2f}" for item in sorted_results],
        rate=[f"{item['rate']:.1f}%" for item in sorted_results],
        count=f"已收集数据 {total_data} 条",
    )
