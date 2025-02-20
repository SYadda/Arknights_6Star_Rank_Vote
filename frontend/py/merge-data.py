import json
from pathlib import Path


def merge_data(avatars, ids):
    merged_data = {}
    for name, avatar_url in avatars.items():
        if name in ids:
            merged_data[name] = {
                "avatar": avatar_url,
                "id": ids[name]
            }

    return merged_data


def save(data, filepath="data.json"):
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    Path(filepath).write_text(json_data, encoding="utf-8")


def main():
    print('success')


if __name__ == "__main__":
    main()
