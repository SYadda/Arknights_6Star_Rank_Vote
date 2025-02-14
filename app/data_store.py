from pathlib import Path

root_path = Path(__file__).parent.parent


def get_res_path(_path: str | list | None = None) -> Path:
    path = (root_path / _path if isinstance(_path, str) else root_path.joinpath(*_path)) if _path else root_path

    if not path.exists():
        path.mkdir(parents=True)

    return path
