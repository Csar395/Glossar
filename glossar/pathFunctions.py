from pathlib import Path

from glossar.config import CURRENT_META_FILE


def get_active_filepath() -> Path:
    if CURRENT_META_FILE.exists():
        path_str = CURRENT_META_FILE.read_text(encoding="utf-8").strip()
        if path_str:
            return Path(path_str)

    return Path("glossary.json")


def set_active_filepath(path: Path) -> None:
    CURRENT_META_FILE.write_text(str(path), encoding="utf-8")
