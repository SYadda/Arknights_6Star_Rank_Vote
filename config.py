import json

with open("./resources/operators_6star_id.json", "r", encoding="utf8") as f:
    operators_6star_id = json.load(f)
    
with open("./resources/operators_6star_pic.json", "r", encoding="utf8") as f:
    operators_6star_pic = json.load(f)

class Config(object):
    # Operators parameters
    DICT_NAME: dict = operators_6star_id
    DICT_PIC_URL: dict = operators_6star_pic
    # ARCHIVE SQLite
    ARCHIVE_DB_URL = "./db/archive.db"
    ARCHIVE_DB_MAX_CONNECTION = 32
    ARCHIVE_DB_TIMEOUT = 300 # second
    
    # OPERATORS SQLite
    OPERATORS_VOTE_RECORDS_DB_URL = "./db/operators_vote_records.db"
    OPERATORS_VOTE_RECORDS_DB_MAX_CONNECTION = 32
    OPERATORS_VOTE_RECORDS_DB_STABLE_TIMEOUT = 300  # second
    OPERATORS_VOTE_RECORDS_DB_DUMP_INTERVAL = 10  # min
    

class ProductionConfig(Config):
    SERVER_ADDRESS = "https://vote.ltsc.vip"
    
    # IP limit
    IP_LIMITER_PER_DAY = 50000
    IP_LIMITER_PER_HOUR = 25000


class DevelopmentConfig(Config):
    SERVER_ADDRESS = "http://localhost:9876"