import structlog
from saq.types import Context
from sqlalchemy import select

from app.db.model import OperatorsVoteRecords, sqlalchemy_config
from app.lib.cache import record_cache

logger = structlog.get_logger()

async def database_save_task(_: Context):
    logger.info("database_save_task start")
    batch = await record_cache.swap_batches()
    print(batch)
    win_updates = {oid: value for oid, value in batch.score_win.items() if value > 0}
    lose_updates = {oid: value for oid, value in batch.score_lose.items() if value > 0}

    if not win_updates and not lose_updates:
        logger.info("database_save_task done")
        return

    logger.info("database_save_task update")

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
                records[oid].score_win += value / 100
        for oid, value in lose_updates.items():
            if oid in records:
                records[oid].score_lose += value / 100

        await session.commit()
        await session.flush()

    logger.info("database_save_task done")
