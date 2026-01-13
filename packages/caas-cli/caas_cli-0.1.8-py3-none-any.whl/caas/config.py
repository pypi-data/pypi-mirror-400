from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from platformdirs import user_config_dir
from pydantic import BaseModel, Field

APP_NAME = "caas"


class CaaSConfig(BaseModel):
    rpc_url: Optional[str] = None
    default_wallet_pubkey: Optional[str] = None
    last_session_id: Optional[str] = None

    slippage: float = Field(default=10.0, ge=0.1, le=99.0)
    priority_fee: float = Field(default=0.00005, ge=0.0, le=1.0)
    pool: str = Field(default="auto")

    seen_welcome: bool = False


def config_path() -> Path:
    d = Path(user_config_dir(APP_NAME))
    d.mkdir(parents=True, exist_ok=True)
    return d / "config.json"


def load_config() -> CaaSConfig:
    p = config_path()
    if not p.exists():
        return CaaSConfig()
    return CaaSConfig(**json.loads(p.read_text("utf-8")))


def save_config(cfg: CaaSConfig) -> None:
    config_path().write_text(cfg.model_dump_json(indent=2), "utf-8")
