from peewee import *
from playhouse.pool import PooledSqliteDatabase, PooledCSqliteExtDatabase
import datetime

# db = SqliteDatabase('archive.db')
db = PooledSqliteDatabase("archive.db", max_connections=32, stale_timeout=300)
class BaseModel(Model):
    class Meta:
        database = db

class Archive(BaseModel):
    key = CharField(primary_key=True)
    data = TextField(null = True)
    vote_times = IntegerField(null = True)
    created_at = DateTimeField(formats='%Y-%m-%d %H:%M:%S', default=datetime.datetime.now)
    updated_at = DateTimeField(formats='%Y-%m-%d %H:%M:%S', default=datetime.datetime.now)
    shared_link = CharField(null = True)
    ip = CharField()

db.connect()
db.create_tables([Archive])