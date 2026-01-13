# src/caas/wallet_value.py
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests

DEFAULT_PROXY_URL = "https://us-central1-caas-cli.cloudfunctions.net/birdeyeWalletTokenList"

SOL_MINTS = {
    "So11111111111111111111111111111111111111111",
    "So11111111111111111111111111111111111111112",
}

@dataclass(frozen=True)
class WalletValue:
    sol: float
    usd: float
    total_usd: float

@dataclass(frozen=True)
class PortfolioItem:
    address: str
    name: str
    symbol: str
    ui_amount: float
    value_usd: float

@dataclass(frozen=True)
class WalletPortfolio:
    wallet: str
    total_usd: float
    items: List[PortfolioItem]

class WalletValueError(RuntimeError):
    pass

class WalletPortfolioError(RuntimeError):
    pass

_value_cache: Dict[str, Tuple[float, WalletValue]] = {}
_port_cache: Dict[str, Tuple[float, WalletPortfolio]] = {}

def invalidate_wallet_cache(wallet_pubkey: str) -> None:
    _value_cache.pop(wallet_pubkey, None)
    _port_cache.pop(wallet_pubkey, None)

def _proxy_wallet_token_list(wallet: str, timeout: float = 15) -> dict:
    base = (os.getenv("CAAS_BIRDEYE_PROXY_URL") or "").strip() or DEFAULT_PROXY_URL

    # Cache-bust so upstream/proxy/CDN doesn't hand you stale JSON.
    # If your Cloud Function/Birdeye ignores it, harmless. If it caches by full URL, this fixes it.
    cb = str(int(time.time() * 1000))

    r = requests.get(
        base,
        params={"wallet": wallet, "ui_amount_mode": "scaled", "cb": cb},
        timeout=timeout,
        headers={
            "cache-control": "no-cache",
            "pragma": "no-cache",
        },
    )
    r.raise_for_status()
    return r.json()

def get_wallet_value(wallet_pubkey: str, *, cache_seconds: float = 10.0) -> WalletValue:
    now = time.time()
    cached = _value_cache.get(wallet_pubkey)
    if cached and cached[0] > now:
        return cached[1]

    try:
        j = _proxy_wallet_token_list(wallet_pubkey)
    except Exception as e:
        raise WalletValueError(str(e))

    data = j.get("data") or {}
    items = data.get("items") or []
    total_usd = float(data.get("totalUsd") or 0.0)

    sol_item = next((it for it in items if str(it.get("symbol", "")).upper() == "SOL"), None)

    sol = float(sol_item.get("uiAmount", 0.0)) if sol_item else 0.0
    usd = float(sol_item.get("valueUsd", 0.0)) if sol_item else 0.0

    v = WalletValue(sol=sol, usd=usd, total_usd=total_usd)
    _value_cache[wallet_pubkey] = (now + cache_seconds, v)
    return v

def get_wallet_portfolio(wallet_pubkey: str, *, cache_seconds: float = 10.0) -> WalletPortfolio:
    now = time.time()
    cached = _port_cache.get(wallet_pubkey)
    if cached and cached[0] > now:
        return cached[1]

    try:
        j = _proxy_wallet_token_list(wallet_pubkey)
    except Exception as e:
        raise WalletPortfolioError(str(e))

    data = j.get("data") or {}
    items = data.get("items") or []

    out = [
        PortfolioItem(
            address=str(it.get("address")),
            name=str(it.get("name") or it.get("symbol")),
            symbol=str(it.get("symbol")),
            ui_amount=float(it.get("uiAmount") or 0),
            value_usd=float(it.get("valueUsd") or 0),
        )
        for it in items
    ]

    port = WalletPortfolio(
        wallet=wallet_pubkey,
        total_usd=float(data.get("totalUsd") or 0),
        items=out,
    )
    _port_cache[wallet_pubkey] = (now + cache_seconds, port)
    return port
