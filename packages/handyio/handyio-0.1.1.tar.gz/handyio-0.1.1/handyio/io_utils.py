from pathlib import Path
from typing import List, Dict, Any
import json
from charset_normalizer import from_bytes


# ---------- PATH ----------

def _ensure_path(path) -> Path:
    if isinstance(path, Path):
        return path
    return Path(path)


# ---------- ENCODING ----------

def _read_text_with_fallback(path, encoding="utf-8") -> str:
    path = _ensure_path(path)

    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        raw = path.read_bytes()
        result = from_bytes(raw).best()

        if result is None:
            raise

        return raw.decode(result.encoding)


# ---------- LIST <-> TXT ----------

def save_list_to_txt(
    data: List[Any],
    path,
    encoding: str = "utf-8",
):

    path = _ensure_path(path)

    with path.open("w", encoding=encoding) as f:
        for item in data:
            f.write(f"{item}\n")


def load_list_from_txt(
    path,
    encoding: str = "utf-8",
    strip: bool = True,
) -> List[str]:
    text = _read_text_with_fallback(path, encoding)
    lines = text.splitlines()

    if strip:
        return [line.rstrip("\n") for line in lines]

    return lines


# ---------- DICT <-> TXT (JSON) ----------

def save_dict_to_txt(
    data: Dict[str, Any],
    path,
    encoding: str = "utf-8",
    indent: int = 2,
):

    path = _ensure_path(path)

    with path.open("w", encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_dict_from_txt(
    path,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    text = _read_text_with_fallback(path, encoding)
    return json.loads(text)
