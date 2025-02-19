from itertools import product

import structlog
from saq.types import Context
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.config import conf
from app.data import operator_ids
from app.db.model import OperatorsVoteRecords, sqlalchemy_config

logger = structlog.get_logger()
task_redis = conf.redis.get_client()


async def database_save_task(_: Context):
    logger.info("Database update task started")

    try:
        win_keys = [f"{oid}:win" for oid in operator_ids]
        lose_keys = [f"{oid}:lose" for oid in operator_ids]
        all_keys = win_keys + lose_keys

        values = await task_redis.mget(*all_keys)
        logger.info("Redis data collected", keys_fetched=len(all_keys))

        win_values = values[: len(operator_ids)]
        lose_values = values[len(operator_ids) :]

        updates = {}
        for oid, w_val, l_val in zip(operator_ids, win_values, lose_values, strict=True):
            updates[oid] = (int(w_val) if w_val is not None else 0, int(l_val) if l_val is not None else 0)

        async with sqlalchemy_config.get_session() as session:
            try:
                result = await session.execute(
                    select(OperatorsVoteRecords).where(OperatorsVoteRecords.operator_id.in_(operator_ids))
                )
                records = {r.operator_id: r for r in result.scalars()}

                updated = 0
                for oid, (win, lose) in updates.items():
                    if record := records.get(oid):
                        record.score_win = win / 100
                        record.score_lose = lose / 100
                        updated += 1

                await session.commit()
                logger.info("Database update succeeded", updated_records=updated, total_records=len(operator_ids))
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error("Database update failed", error=str(e))

    except Exception as e:  # noqa: BLE001
        logger.error("Database update task failed", error=str(e))

    finally:
        logger.info("Database update task completed")


async def redis_op_matrix_update_task(_: Context):
    try:
        logger.info("redis_op_matrix_update_task started.")
        redis_keys = [f"op_matrix:{i}:{j}" for i, j in product(operator_ids, repeat=2)]
        values = await task_redis.mget(*redis_keys)
        op_length = len(operator_ids)
        values = [[int(values[i * op_length + j]) for j in range(op_length)] for i in range(op_length)]
        async with task_redis.lock("lock:op_matrix", timeout=5, blocking_timeout=3):
            await task_redis.set("op_matrix", str(values))

    except Exception as e:  # noqa: BLE001
        logger.error("redis_op_matrix_update_task fail.", error=str(e))
    finally:
        logger.info("redis_op_matrix_update_task completed")
