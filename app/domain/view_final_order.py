from litestar import Response, get
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data import reverse_operators_id_dict
from app.db.model import OperatorsVoteRecords


@get("/view_final_order")
async def view_final_order(db_session: AsyncSession) -> Response:
    result = (await db_session.stream(select(OperatorsVoteRecords))).scalars()
    records = {r.operator_id: r async for r in result}

    win_score = {oid: record.score_win for oid, record in records.items()}
    lose_score = {oid: record.score_lose for oid, record in records.items()}

    rate = {
        oid: win_score[oid] / (win_score[oid] + lose_score[oid]) * 100
        for oid in win_score
    }
    score = {oid: win_score[oid] - lose_score[oid] for oid in win_score}

    final_order = sorted(score.items(), key=lambda x: x[1], reverse=True)
    final_order = [
        (reverse_operators_id_dict[oid], score, f"{rate:.1f} %")
        for oid, score in final_order
    ]

    return Response(
        status_code=200,
        content={
            "name": [name for name, _, _ in final_order],
            "score": [f"{score:.2f}" for _, score, _ in final_order],
            "rate": [rate for _, _, rate in final_order],
            "count": f"已收集数据 {sum(win_score.values())} 条",
        },
    )
