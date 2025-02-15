import structlog
from saq.types import Context
from sqlalchemy import select

from app.config import conf
from app.data import operators_id_list
from app.db.model import OperatorsVoteRecords, sqlalchemy_config

logger = structlog.get_logger()


async def database_save_task(_: Context):
    redis = conf.redis.get_client()
    logger.info("Database update task started")

    # collect all updates from redis
    keys = [f"{operator_id}:win" for operator_id in operators_id_list] + [
        f"{operator_id}:lose" for operator_id in operators_id_list
    ]
    values = await redis.mget(*keys)

    win_updates = {operator_id: int(values[i]) for i, operator_id in enumerate(operators_id_list)}
    lose_updates = {
        operator_id: int(values[i + len(operators_id_list)]) for i, operator_id in enumerate(operators_id_list)
    }

    logger.info("Redis data collected")

    async with sqlalchemy_config.get_session() as session:
        result = (
            await session.stream(
                select(OperatorsVoteRecords).where(
                    OperatorsVoteRecords.operator_id.in_(list(win_updates.keys()) + list(lose_updates.keys()))
                )
            )
        ).scalars()
        records = {r.operator_id: r async for r in result}

        for oid, value in win_updates.items():
            if oid in records:
                records[oid].score_win = value / 100
        for oid, value in lose_updates.items():
            if oid in records:
                records[oid].score_lose = value / 100

        await session.commit()
        await session.flush()
    logger.info("Database updated")
