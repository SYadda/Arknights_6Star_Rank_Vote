import json
from pathlib import Path

from app.data_store import get_res_path


def get_resource_path(filename: str) -> Path:
    return get_res_path(f"./resources/{filename}")

with Path.open(get_resource_path("operators_6star_id.json"), encoding="utf8") as f:
    operators_id_dict: dict[str, int] = json.load(f)

with Path.open(get_resource_path("operators_6star_pic.json"), encoding="utf8") as f:
    operators_6star_pic = json.load(f)

reverse_operators_id_dict = {v: k for k, v in operators_id_dict.items()}
operators_id_list = list(operators_id_dict.values())
