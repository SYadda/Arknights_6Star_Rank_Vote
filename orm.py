from peewee import *
from playhouse.pool import PooledSqliteDatabase, PooledCSqliteExtDatabase
import sqlite3
import datetime
from config import Config
from contextlib import closing
from collections import OrderedDict
from threading import Lock

operators_id_dict = Config.DICT_NAME
operators_id_dict_length = len(operators_id_dict)

archive_db = PooledSqliteDatabase("archive.db", max_connections=32, stale_timeout=300)
operators_vote_records_db = PooledSqliteDatabase(
    Config.OPERATORS_VOTE_RECORDS_DB_URL,
    max_connections=Config.OPERATORS_VOTE_RECORDS_DB_MAX_CONNECTION,
    stale_timeout=Config.OPERATORS_VOTE_RECORDS_DB_STABLE_TIMEOUT,
    pragmas={"journal_mode": "wal", "synchronous": "NORMAL"},
)

class Archive(Model):
    key = CharField(primary_key=True)
    data = TextField(null=True)
    vote_times = IntegerField(null=True)
    created_at = DateTimeField(
        formats="%Y-%m-%d %H:%M:%S", default=datetime.datetime.now
    )
    updated_at = DateTimeField(
        formats="%Y-%m-%d %H:%M:%S", default=datetime.datetime.now
    )
    shared_link = CharField(null=True)
    ip = CharField()

    class Meta:
        database = archive_db
        db_table = "archive"

class OperatorsVoteRecords(Model):
    operator_id = IntegerField(null=False, primary_key=True)
    score_win = FloatField(null=False, default=1)
    score_lose = FloatField(null=False, default=1)

    class Meta:
        database = operators_vote_records_db
        db_table = "operators_vote_records"


# TODO: 可以用pydantic优化一下
class MemoryDB(object):
    def __init__(self, score_win, score_lose, lock_score_win, lock_score_lose):
        self.score_win: OrderedDict = score_win
        self.score_lose: OrderedDict = score_lose
        self.lock_score_win: list = lock_score_win
        self.lock_score_lose: list = lock_score_lose


def DB_Init():
    # archive_db
    archive_db.connect()
    archive_db.create_tables([Archive])

    # operators_vote_records_db
    operators_vote_records_db.connect()
    operators_vote_records_db.create_tables([OperatorsVoteRecords], safe=True)

    # TODO: replace to redis, sqlite(memory mode) or any other memory db...
    # 全局投票数据（内存），反正就几百个浮点数
    mem_db = MemoryDB(
        OrderedDict((id, 1) for id in range(operators_id_dict_length)),
        OrderedDict((id, 1) for id in range(operators_id_dict_length)),
        [Lock() for _ in range(operators_id_dict_length)],
        [Lock() for _ in range(operators_id_dict_length)],
    )

    with operators_vote_records_db.atomic():
        for i in range(len(Config.DICT_NAME)):
            OperatorsVoteRecords_i, _ = OperatorsVoteRecords.get_or_create(
                operator_id=i, defaults={"score_win": 1, "score_lose": 1}
            )
            mem_db.score_win[i] = OperatorsVoteRecords_i.score_win
            mem_db.score_lose[i] = OperatorsVoteRecords_i.score_lose
    return mem_db

# TODO: 用pydantic写个update_list的Model
def dump_vote_records(win_update_list, lose_update_list):
    try:
        with closing(sqlite3.connect("operators_vote_records.db")) as conn:
            with conn:
                with closing(conn.cursor()) as cur:
                    if win_update_list:
                        cur.executemany(
                            # "UPDATE operators_vote_records SET score_win = score_win + ? WHERE operator_id = ?", # 没必要设计两层缓存
                            "UPDATE operators_vote_records SET score_win = ? WHERE operator_id = ?",
                            win_update_list,
                        )
                    if lose_update_list:
                        cur.executemany(
                            "UPDATE operators_vote_records SET score_lose = ? WHERE operator_id = ?",
                            lose_update_list,
                        )
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        # TODO: 其他处理
