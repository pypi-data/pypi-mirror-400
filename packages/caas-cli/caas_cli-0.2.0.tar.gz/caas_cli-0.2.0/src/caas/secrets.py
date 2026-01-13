from __future__ import annotations

import keyring
from typing import Optional

SERVICE = "caas"


def set_secret(name: str, value: str) -> None:
    keyring.set_password(SERVICE, name, value)


def get_secret(name: str) -> Optional[str]:
    return keyring.get_password(SERVICE, name)


def delete_secret(name: str) -> None:
    try:
        keyring.delete_password(SERVICE, name)
    except Exception:
        pass


def has_secret(name: str) -> bool:
    return get_secret(name) is not None


def clear_all_secrets() -> None:
    for k in ("anthropic_api_key", "solana_private_key"):
        delete_secret(k)
