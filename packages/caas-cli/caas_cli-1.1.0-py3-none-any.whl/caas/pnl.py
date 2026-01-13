# src/caas/pnl.py
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import requests

from .memory import (
    insert_pending_trade,
    update_trade,
    get_pending_trades,
    get_position,
    upsert_position,
)

LAMPORTS_PER_SOL = 1_000_000_000

@dataclass(frozen=True)
class EnrichedTrade:
    slot: int
    block_time: int
    fee_lamports: int
    sol_delta: float      # signed SOL change for wallet
    token_delta: float    # signed token change (UI units)
    usd_value: float      # buy: cost (positive), sell: proceeds (positive)

def _rpc_get_transaction(rpc_url: str, signature: str, timeout: float = 15.0) -> Optional[dict]:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "encoding": "jsonParsed",
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0,
            },
        ],
    }
    r = requests.post(rpc_url, json=payload, timeout=timeout)
    r.raise_for_status()
    j = r.json()
    return j.get("result")

def _nearest_sol_price_usd(block_time: int, timeout: float = 15.0) -> float:
    """
    Best-effort SOL/USD near the tx timestamp.
    Uses CoinGecko market_chart/range (no key) and picks nearest point.
    If it fails, returns 0.0 (PnL will still work in SOL terms via sol_delta, but USD will be blank-ish).
    """
    try:
        # query +/- 10 minutes
        start = block_time - 600
        end = block_time + 600
        url = "https://api.coingecko.com/api/v3/coins/solana/market_chart/range"
        params = {"vs_currency": "usd", "from": str(start), "to": str(end)}
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        prices = data.get("prices") or []
        if not prices:
            return 0.0

        # prices: [[ms, price], ...]
        target_ms = block_time * 1000
        best = min(prices, key=lambda p: abs(int(p[0]) - target_ms))
        return float(best[1])
    except Exception:
        return 0.0

def _extract_wallet_sol_delta(tx: dict, wallet_pubkey: str) -> Tuple[float, int]:
    """
    Returns (sol_delta, fee_lamports) where sol_delta is post-pre for wallet in SOL.
    Includes fee naturally (since balance change includes fee).
    """
    meta = tx.get("meta") or {}
    fee = int(meta.get("fee") or 0)

    message = (tx.get("transaction") or {}).get("message") or {}
    keys = message.get("accountKeys") or []

    fee_payer_index = None
    for i, k in enumerate(keys):
        # jsonParsed accountKeys are objects sometimes
        if isinstance(k, dict):
            pub = k.get("pubkey")
        else:
            pub = k
        if str(pub) == wallet_pubkey:
            fee_payer_index = i
            break

    if fee_payer_index is None:
        # if we can't find it, bail to 0 deltas
        return (0.0, fee)

    pre = (meta.get("preBalances") or [])[fee_payer_index]
    post = (meta.get("postBalances") or [])[fee_payer_index]
    lamports_delta = int(post) - int(pre)
    return (lamports_delta / LAMPORTS_PER_SOL, fee)

def _extract_wallet_token_delta(tx: dict, wallet_pubkey: str, mint: str) -> float:
    meta = tx.get("meta") or {}
    pre = meta.get("preTokenBalances") or []
    post = meta.get("postTokenBalances") or []

    def _sum_for(arr: list) -> float:
        total = 0.0
        for it in arr:
            if str(it.get("mint")) != mint:
                continue
            # owner may be absent on some nodes; accountIndex is there but harder.
            owner = it.get("owner")
            if owner and str(owner) != wallet_pubkey:
                continue
            ui = (it.get("uiTokenAmount") or {}).get("uiAmount")
            if ui is None:
                # fallback from amount/decimals
                amt = float((it.get("uiTokenAmount") or {}).get("amount") or 0)
                dec = int((it.get("uiTokenAmount") or {}).get("decimals") or 0)
                ui = amt / (10 ** dec) if dec >= 0 else 0.0
            total += float(ui or 0.0)
        return total

    pre_amt = _sum_for(pre)
    post_amt = _sum_for(post)
    return float(post_amt - pre_amt)

def enrich_trade_from_signature(
    *,
    rpc_url: str,
    wallet_pubkey: str,
    mint: str,
    side: str,            # "buy" | "sell"
    signature: str,
    max_wait_seconds: int = 25,
) -> Optional[EnrichedTrade]:
    """
    Poll getTransaction until it exists (confirmed), then compute exact deltas and USD value.
    USD value uses SOL/USD near blockTime.
    """
    deadline = time.time() + max_wait_seconds
    last_err: Optional[str] = None

    while time.time() < deadline:
        try:
            tx = _rpc_get_transaction(rpc_url, signature)
            if not tx:
                time.sleep(0.6)
                continue

            meta = tx.get("meta") or {}
            if meta.get("err") is not None:
                update_trade(signature, status="failed", error=str(meta.get("err")))
                return None

            slot = int(tx.get("slot") or 0)
            block_time = int(tx.get("blockTime") or tx.get("block_time") or 0)

            sol_delta, fee_lamports = _extract_wallet_sol_delta(tx, wallet_pubkey)
            token_delta = _extract_wallet_token_delta(tx, wallet_pubkey, mint)

            sol_price = _nearest_sol_price_usd(block_time) if block_time else 0.0

            # For buys: wallet SOL delta should be negative (spent). For sells: usually positive (received).
            if side == "buy":
                sol_spent = max(0.0, -sol_delta)
                usd_value = sol_spent * sol_price if sol_price > 0 else 0.0
            else:
                sol_received = max(0.0, sol_delta)
                usd_value = sol_received * sol_price if sol_price > 0 else 0.0

            return EnrichedTrade(
                slot=slot,
                block_time=block_time,
                fee_lamports=fee_lamports,
                sol_delta=sol_delta,
                token_delta=token_delta,
                usd_value=usd_value,
            )
        except Exception as e:
            last_err = str(e)
            time.sleep(0.6)

    if last_err:
        update_trade(signature, status="pending", error=last_err)
    return None

def _apply_position_avg_cost(wallet_pubkey: str, mint: str, side: str, token_delta: float, usd_value: float) -> None:
    """
    Avg-cost method:
    - buy: token_delta > 0, usd_value is cost (positive)
    - sell: token_delta < 0, usd_value is proceeds (positive)
    """
    pos = get_position(wallet_pubkey, mint) or {"qty": 0.0, "cost_usd": 0.0, "realized_pnl_usd": 0.0}
    qty = float(pos["qty"])
    cost_usd = float(pos["cost_usd"])
    realized = float(pos["realized_pnl_usd"])

    if side == "buy":
        q_add = max(0.0, token_delta)
        if q_add <= 0:
            return
        cost_usd += float(usd_value or 0.0)
        qty += q_add
        upsert_position(wallet_pubkey, mint, qty=qty, cost_usd=cost_usd, realized_pnl_usd=realized)
        return

    # sell
    q_sold = max(0.0, -token_delta)
    if q_sold <= 0:
        return

    avg = (cost_usd / qty) if qty > 0 else 0.0
    cost_removed = avg * q_sold
    proceeds = float(usd_value or 0.0)
    realized += (proceeds - cost_removed)

    qty = max(0.0, qty - q_sold)
    cost_usd = max(0.0, cost_usd - cost_removed)

    upsert_position(wallet_pubkey, mint, qty=qty, cost_usd=cost_usd, realized_pnl_usd=realized)

def record_trade_async(
    *,
    rpc_url: str,
    wallet_pubkey: str,
    mint: str,
    side: str,
    signature: str,
) -> None:
    """
    Insert pending row immediately, then enrich in background to keep trading fast.
    """
    insert_pending_trade(wallet_pubkey, mint, side, signature)

    def _worker() -> None:
        try:
            enriched = enrich_trade_from_signature(
                rpc_url=rpc_url,
                wallet_pubkey=wallet_pubkey,
                mint=mint,
                side=side,
                signature=signature,
            )
            if not enriched:
                return

            update_trade(
                signature,
                status="confirmed",
                slot=enriched.slot,
                block_time=enriched.block_time,
                sol_delta=enriched.sol_delta,
                fee_lamports=enriched.fee_lamports,
                token_delta=enriched.token_delta,
                usd_value=enriched.usd_value,
                error=None,
            )

            _apply_position_avg_cost(
                wallet_pubkey=wallet_pubkey,
                mint=mint,
                side=side,
                token_delta=enriched.token_delta,
                usd_value=enriched.usd_value,
            )
        except Exception as e:
            update_trade(signature, status="pending", error=str(e))

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

def enrich_pending_trades_now(*, rpc_url: str, wallet_pubkey: str, limit: int = 5) -> None:
    """
    Called from `show port` to catch up quickly if user runs it right after trading.
    """
    pend = get_pending_trades(wallet_pubkey, max_age_seconds=6 * 3600, limit=limit)
    for it in pend:
        sig = it["signature"]
        mint = it["mint"]
        side = it["side"]
        try:
            enriched = enrich_trade_from_signature(
                rpc_url=rpc_url,
                wallet_pubkey=wallet_pubkey,
                mint=mint,
                side=side,
                signature=sig,
                max_wait_seconds=3,  # short wait during "show"
            )
            if not enriched:
                continue

            update_trade(
                sig,
                status="confirmed",
                slot=enriched.slot,
                block_time=enriched.block_time,
                sol_delta=enriched.sol_delta,
                fee_lamports=enriched.fee_lamports,
                token_delta=enriched.token_delta,
                usd_value=enriched.usd_value,
                error=None,
            )
            _apply_position_avg_cost(wallet_pubkey, mint, side, enriched.token_delta, enriched.usd_value)
        except Exception as e:
            update_trade(sig, error=str(e))
