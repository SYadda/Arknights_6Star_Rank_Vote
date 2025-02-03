import json

with open("./operators_6star_id.json", "r", encoding="utf8") as f:
    operators_6star_id = json.load(f)
    
with open("./operators_6star_pic.json", "r", encoding="utf8") as f:
    operators_6star_pic = json.load(f)

class Config(object):
    # Operators parameters
    DICT_NAME: dict = operators_6star_id
    DICT_PIC_URL: dict = operators_6star_pic
    # OPERATORS SQLite
    OPERATORS_VOTE_RECORDS_DB_URL = "./operators_vote_records.db"
    OPERATORS_VOTE_RECORDS_DB_MAX_CONNECTION = 32
    OPERATORS_VOTE_RECORDS_DB_STABLE_TIMEOUT = 300  # second
    OPERATORS_VOTE_RECORDS_DB_DUMP_INTERVAL = 10  # min
    

class ProductionConfig(Config):
    SERVER_ADDRESS = "https://vote.ltsc.vip"


class DevelopmentConfig(Config):
    SERVER_ADDRESS = "http://localhost:9876"
    # class Config:
    #     DB_URL = "./archive.db"
