import json

with open("./operators_6star_id.json", "r", encoding="utf8") as f:
    operators_6star_id = json.load(f)
    
with open("./operators_6star_pic.json", "r", encoding="utf8") as f:
    operators_6star_pic = json.load(f)

class Config(object):
    # Operators parameters
    DICT_NAME: dict = operators_6star_id
    DICT_PIC_URL: dict = operators_6star_pic

class ProductionConfig(Config):
    SERVER_ADDRESS = "https://vote.ltsc.vip"


class DevelopmentConfig(Config):
    SERVER_ADDRESS = "http://localhost:9876"
