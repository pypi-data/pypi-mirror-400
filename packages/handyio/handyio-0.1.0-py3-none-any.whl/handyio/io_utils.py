from pathlib import Path
from typing import List, Dict, Any


def _ensure_path(path) -> Path:
    if isinstance(path, Path):
        return path
    return Path(path)


# ---------- LIST <-> TXT ----------

def save_list_to_txt(
    data: List[Any],
    path,
    encoding: str = "utf-8",
):
    if not isinstance(data, list):
        raise TypeError("data must be a list")

    path = _ensure_path(path)

    with path.open("w", encoding=encoding) as f:
        for item in data:
            f.write(f"{item}\n")


def load_list_from_txt(
    path,
    encoding: str = "utf-8",
    strip: bool = True,
) -> List[str]:
    path = _ensure_path(path)

    with path.open("r", encoding=encoding) as f:
        lines = f.readlines()

    if strip:
        lines = [line.rstrip("\n") for line in lines]

    return lines


# ---------- DICT <-> TXT ----------

def save_dict_to_txt(
    data: Dict[Any, Any],
    path,
    sep: str = "=",
    encoding: str = "utf-8",
):
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    path = _ensure_path(path)

    with path.open("w", encoding=encoding) as f:
        for k, v in data.items():
            f.write(f"{k}{sep}{v}\n")


def load_dict_from_txt(
    path,
    sep: str = "=",
    encoding: str = "utf-8",
) -> Dict[str, str]:
    path = _ensure_path(path)
    result = {}

    with path.open("r", encoding=encoding) as f:
        for line in f:
            line = line.rstrip("\n")
            if sep not in line:
                continue
            k, v = line.split(sep, 1)
            result[k] = v

    return result
