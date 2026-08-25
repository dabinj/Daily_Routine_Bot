from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    root: Path = ROOT
    telegram_key_path: Path = ROOT / ".telegram.key"
    telegram_chat_path: Path = ROOT / ".telegram.chat"
    state_path: Path = ROOT / "var" / "state.json"
    db_path: Path = ROOT / "var" / "routine.sqlite3"
    schedule_path: Path = ROOT / "config" / "routine_schedule.json"


def read_secret(path: Path) -> str:
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"Secret file is empty: {path}")
    return value


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_settings() -> Settings:
    return Settings()

