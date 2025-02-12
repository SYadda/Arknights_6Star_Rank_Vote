from asyncio import Lock
import time

from app.data import operators_id_dict
from app.model import OperatorsVoteRecords

from msgspec import Struct
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class VoteRecordBatch(Struct):
    score_win: dict[int, int]
    score_lose: dict[int, int]
    operators_vote_matrix: dict[int, dict[int, int]]


class VoteRecordCache:
    swap_lock: Lock
    buffers: list[VoteRecordBatch]
    lock_score_win: dict[int, Lock]
    lock_score_lose: dict[int, Lock]
    last_save: int

    def __init__(self, operator_ids: list[int]):
        self._init_batch(operator_ids)

        self.swap_lock = Lock()
        self.buffers = [self._create_batch(), self._create_batch()]
        self.current_index = 0
        self.lock_score_win = {oid: Lock() for oid in operator_ids}
        self.lock_score_lose = {oid: Lock() for oid in operator_ids}
        self.last_save = int(time.time())

    def _init_batch(self, operator_ids: list[int]):
        self.operator_ids = operator_ids
        self.base_win = {(oid, 0) for oid in sorted(operator_ids)}
        self.base_lose = {(oid, 0) for oid in sorted(operator_ids)}
        self.base_matrix = {
            oid: {inner_oid: 0 for inner_oid in operator_ids} for oid in operator_ids
        }

    def _create_batch(self):
        return VoteRecordBatch(
            score_win=dict(self.base_win),
            score_lose=dict(self.base_lose),
            operators_vote_matrix=dict(self.base_matrix),
        )

    def current_batch(self):
        return self.buffers[self.current_index]

    async def update_score(self, win_id: int, lose_id: int, multiplier: int):
        batch = self.current_batch()

        async with self.lock_score_win[win_id]:
            batch.score_win[win_id] += multiplier
            batch.operators_vote_matrix[win_id][lose_id] += multiplier

        async with self.lock_score_lose[lose_id]:
            batch.score_lose[lose_id] += multiplier
            batch.operators_vote_matrix[lose_id][win_id] -= multiplier

    async def swap_batches(self):
        async with self.swap_lock:
            self.current_index = 1 - self.current_index
            return_batch = self.buffers[1 - self.current_index]
            self.buffers[1 - self.current_index] = self._create_batch()

            return return_batch


async def save_batch(session: AsyncSession, batch: VoteRecordBatch):
    win_updates = {oid: value for oid, value in batch.score_win.items() if value > 0}
    lose_updates = {oid: value for oid, value in batch.score_lose.items() if value > 0}

    if not win_updates and not lose_updates:
        return

    result = (
        await session.stream(
            select(OperatorsVoteRecords).where(
                OperatorsVoteRecords.operator_id.in_(
                    list(win_updates.keys()) + list(lose_updates.keys())
                )
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


record_cache = VoteRecordCache(operator_ids=list(operators_id_dict.values()))
