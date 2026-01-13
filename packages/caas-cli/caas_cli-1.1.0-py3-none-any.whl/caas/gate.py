from __future__ import annotations
import json
import time
from pathlib import Path
from platformdirs import user_runtime_dir

APP_NAME = "caas"

def _gate_path() -> Path:
    d = Path(user_runtime_dir(APP_NAME))
    d.mkdir(parents=True, exist_ok=True)
    return d / "gate.json"

def set_unlocked(ttl_seconds: int = 1800) -> None:
    _gate_path().write_text(
        json.dumps({"unlocked_until": time.time() + ttl_seconds}, indent=2),
        "utf-8"
    )

def is_unlocked() -> bool:
    p = _gate_path()
    if not p.exists():
        return False
    try:
        data = json.loads(p.read_text("utf-8"))
        return float(data.get("unlocked_until", 0)) > time.time()
    except Exception:
        return False

def clear() -> None:
    p = _gate_path()
    if p.exists():
        p.unlink()
