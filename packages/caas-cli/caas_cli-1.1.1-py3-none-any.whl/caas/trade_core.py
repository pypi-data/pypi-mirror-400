from __future__ import annotations

from .config import load_config
from .gate import is_unlocked
from .pumpportal_trader import PumpPortalTrader
from .secrets import get_secret
from .session import SessionState


class TradeError(RuntimeError):
    pass


def execute_trade(
    *,
    state: SessionState,
    action: str,
    mint: str,
    amount,
    denominated_in_sol: bool,
):
    cfg = load_config()

    if not cfg.rpc_url:
        raise TradeError("RPC not set")

    if not is_unlocked():
        raise TradeError("Wallet locked")

    secret = get_secret("solana_private_key")
    if not secret:
        raise TradeError("Wallet not set")

    # Ensure wallet loaded into session
    if not state.wallet_unlocked:
        state.unlock_with_secret(secret)

    trader = PumpPortalTrader(cfg.rpc_url)

    trader.trade(
        state.wallet(),
        action=action,
        mint=mint,
        amount=amount,
        denominated_in_sol=denominated_in_sol,
        slippage=cfg.slippage,
        priority_fee=cfg.priority_fee,
        pool=cfg.pool,
    )
