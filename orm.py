import os
import json
import datetime
from peewee import Model, CharField, IntegerField, FloatField, DateTimeField, TextField
from playhouse.pool import PooledSqliteDatabase, PooledCSqliteExtDatabase
from config import Config
from threading import Lock
from model import VoteRecordDB
from typing import List, Tuple
from collections import OrderedDict
from flask import current_app
operators_id_dict = Config.DICT_NAME
operators_id_dict_length = len(operators_id_dict)

# 创建SQLite存储目录
dirname = os.path.dirname(Config.ARCHIVE_DB_URL)
if not os.path.exists(dirname):
    os.makedirs(dirname)
dirname = os.path.dirname(Config.OPERATORS_VOTE_RECORDS_DB_URL)
if not os.path.exists(dirname):
    os.makedirs(dirname)

archive_db = PooledSqliteDatabase(Config.ARCHIVE_DB_URL, max_connections=Config.ARCHIVE_DB_MAX_CONNECTION, stale_timeout=Config.ARCHIVE_DB_TIMEOUT)
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

# TODO: 初始化为1的操作是错的，以前的代码为了不让'/view_final_order'接口报错
class OperatorsVoteRecords(Model):
    operator_id = IntegerField(null=False, primary_key=True)
    score_win = FloatField(null=False, default=1)
    score_lose = FloatField(null=False, default=1)

    class Meta:
        database = operators_vote_records_db
        db_table = "operators_vote_records"


def DB_Init():
    # archive_db
    archive_db.connect()
    archive_db.create_tables([Archive])

    # operators_vote_records_db
    operators_vote_records_db.connect()
    operators_vote_records_db.create_tables([OperatorsVoteRecords], safe=True)

    # TODO: replace to redis, sqlite(memory mode) or any other memory db...
    # 全局投票数据（内存），反正就几百个浮点数
    mem_db = VoteRecordDB(
        score_win = OrderedDict((id, 1) for id in range(operators_id_dict_length)),
        score_lose = OrderedDict((id, 1) for id in range(operators_id_dict_length)),
        lock_score_win = [Lock() for _ in range(operators_id_dict_length)],
        lock_score_lose = [Lock() for _ in range(operators_id_dict_length)],
        operators_vote_matrix = [[0 for _ in range(operators_id_dict_length)] for _ in range(operators_id_dict_length)] # 才存储106*106个数据，查询/赋值速度还真不一定比numpy慢
    )

    # 加载SQLite的投票数据到内存
    with operators_vote_records_db.atomic():
        # 获取所有已存在的记录
        existing_records = {record.operator_id: record for record in OperatorsVoteRecords.select()}
        # 准备要插入的新记录
        new_records = [OperatorsVoteRecords(operator_id=i) for i in range(len(Config.DICT_NAME)) if i not in existing_records]
        # 批量插入新记录
        if new_records:
            OperatorsVoteRecords.bulk_create(new_records)
        # 更新 mem_db
        all_records = {**existing_records, **{record.operator_id: record for record in new_records}}
        for i in range(len(Config.DICT_NAME)):
            mem_db.score_win[i] = all_records[i].score_win
            mem_db.score_lose[i] = all_records[i].score_lose
    
    # 加载干员对位击杀矩阵
    # TODO: 数据持久化到sqlite，而不是存储到文件
    #   比如：'''CREATE TABLE IF NOT EXISTS matrix_table (operator_id INTEGER PRIMARY KEY, key TEXT, matrix_data TEXT)'''
    if os.path.exists(Config.OPERATORS_VOTE_MATRIX_PATH):
        with open(Config.OPERATORS_VOTE_MATRIX_PATH, 'r') as f:
            mem_db.operators_vote_matrix = json.load(f)
    else:
        if not os.path.exists(os.path.dirname(Config.OPERATORS_VOTE_MATRIX_PATH)):
            os.makedirs(os.path.dirname(Config.OPERATORS_VOTE_MATRIX_PATH))
        with open(Config.OPERATORS_VOTE_MATRIX_PATH, 'w') as f:
            json.dump(mem_db.operators_vote_matrix, f)
    return mem_db

def dump_vote_records(win_update_list: List[Tuple[float, int]], lose_update_list: List[Tuple[float, int]], operator_1v1_matrix: List[List]):
    try:
        # 存储分数记录
        win_update_instances = [OperatorsVoteRecords(operator_id=id, score_win=score) for score, id in win_update_list]
        lose_update_instances = [OperatorsVoteRecords(operator_id=id, score_lose=score) for score, id in lose_update_list]
        with operators_vote_records_db.atomic():
            OperatorsVoteRecords.bulk_update(win_update_instances, fields=["score_win"])
            OperatorsVoteRecords.bulk_update(lose_update_instances, fields=["score_lose"])
        # 存储干员对位记录
        with open(Config.OPERATORS_VOTE_MATRIX_PATH, 'w') as f:
            json.dump(operator_1v1_matrix, f)
    except Exception as e:
        current_app.logger.error(f"An error occurred when dump_vote_records: {e}")
        # TODO: 其他处理