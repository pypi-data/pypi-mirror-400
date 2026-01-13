# src/caas/repl.py
from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Optional, Tuple, List

from platformdirs import user_data_dir
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.markdown import Markdown

from .anthropic_client import AnthropicAPIError, AnthropicAuthError, claude_chat
from .config import load_config, save_config
from .gate import is_unlocked
from .memory import add_message, get_recent, init_db
from .secrets import get_secret
from .session import SessionState
from .trade_core import TradeError, execute_trade
from .ui import bad, console, rule, show_banner, spinner, warn
from .wallet_value import WalletValueError, get_wallet_value, invalidate_wallet_cache

_BASE58_MINT_RE = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,80}\b")
_BUY_WORDS = {"buy", "purchase", "ape", "snipe", "swap", "get", "grab", "cop"}
_SELL_WORDS = {"sell", "dump", "exit", "close"}
_BAL_WORDS = {"balance", "wallet", "portfolio", "holdings", "value", "worth", "networth", "net worth"}


def _normalize_reply(text: str) -> str:
    t = (text or "").strip().replace("\r\n", "\n").replace("\r", "\n")
    t = "\n".join(line.rstrip() for line in t.splitlines())
    t = re.sub(r"\n[ \t]*\n+", "\n", t).strip()

    if "\n" not in t:
        parts = re.split(r"(?<=[.!?])\s+", t)
        t = "\n".join(p.strip() for p in parts if p.strip())

    return "\n".join(line.rstrip() for line in t.splitlines()).strip()


def _extract_mint(text: str) -> Optional[str]:
    m = _BASE58_MINT_RE.findall(text or "")
    return m[-1] if m else None


def _extract_number(text: str) -> Optional[float]:
    m = re.search(r"(?<![A-Za-z0-9])(\d+(\.\d+)?|\.\d+)", text or "")
    return float(m.group(1)) if m else None


def _looks_like_buy(text: str) -> bool:
    return any(w in text for w in _BUY_WORDS)


def _looks_like_sell(text: str) -> bool:
    return any(w in text for w in _SELL_WORDS)


def _looks_like_balance(text: str) -> bool:
    t = (text or "").lower()
    if any(w in t for w in _BAL_WORDS):
        return True
    if t.strip() in {"bal", "wallet?", "balance?", "portfolio?"}:
        return True
    return False


def _history_path() -> str:
    d = Path(user_data_dir("caas"))
    d.mkdir(parents=True, exist_ok=True)
    return str(d / "repl_history.txt")


def _base_runtime_context(cfg) -> str:
    parts = [
        "Runtime config (authoritative):",
        f"rpc_url={cfg.rpc_url or ''}",
        f"pool={cfg.pool}",
        f"slippage_percent={cfg.slippage}",
        f"priority_fee_sol={cfg.priority_fee}",
        f"wallet_gate_unlocked={is_unlocked()}",
        f"default_wallet_pubkey={cfg.default_wallet_pubkey or ''}",
    ]
    return "\n".join(parts).strip() + "\n"


def _print_assistant(reply: str) -> None:
    reply = (reply or "").replace("\r\n", "\n").replace("\r", "\n")
    reply = "\n".join(line.rstrip() for line in reply.splitlines()).strip()

    md = Markdown(reply, code_theme=None, hyperlinks=False)
    console.print("[accent]caas>[/accent] ", end="")
    console.print(md, soft_wrap=True, overflow="fold")


def _assistant_reply(api_key: str, session_id: str, runtime_context: str) -> None:
    recent = get_recent(session_id, limit=30)
    with spinner("Thinking..."):
        reply = claude_chat(api_key, recent, runtime_context=runtime_context)
    reply = _normalize_reply(reply)
    add_message(session_id, "assistant", reply)
    _print_assistant(reply)


def _trade_confirmation(
    api_key: str,
    session_id: str,
    cfg,
    *,
    action: str,
    mint: str,
    amount_str: str,
) -> None:
    runtime_context = _base_runtime_context(cfg) + "\n".join(
        [
            "Event: trade_executed",
            "Result: success",
            f"Action: {action}",
            f"Mint: {mint}",
            f"Amount: {amount_str}",
            "",
            "Hard rules:",
            "- The trade already executed successfully. Do NOT tell the user to run a command.",
            "- Reply with ONE short confirmation in CAAS voice (dry, confident).",
            "- No warnings, no lectures, no extra steps.",
        ]
    )

    synthetic_messages: List[Tuple[str, str]] = [
        ("user", f"Trade executed: {action} {amount_str} of {mint}. Confirm in-character."),
    ]

    with spinner("Thinking..."):
        reply = claude_chat(api_key, synthetic_messages, runtime_context=runtime_context)

    reply = _normalize_reply(reply)
    add_message(session_id, "assistant", reply)
    _print_assistant(reply)


def _balance_reply(
    api_key: str,
    session_id: str,
    cfg,
    *,
    sol: float,
    usd: float,
    total_usd: float,
) -> None:
    runtime_context = _base_runtime_context(cfg) + "\n".join(
        [
            "Event: wallet_value_fetched",
            "Result: success",
            f"wallet_pubkey={cfg.default_wallet_pubkey or ''}",
            f"sol_balance={sol}",
            f"sol_value_usd={usd}",
            f"total_wallet_usd={total_usd}",
            "",
            "Hard rules:",
            "- Use the provided numbers as truth.",
            "- Do NOT speculate about trades, commands, or what the user did earlier.",
            "- Reply with ONE short line in CAAS voice.",
        ]
    )

    synthetic_messages: List[Tuple[str, str]] = [
        ("user", "User asked for SOL balance. Respond using the provided numbers."),
    ]

    with spinner("Thinking..."):
        reply = claude_chat(api_key, synthetic_messages, runtime_context=runtime_context)

    reply = _normalize_reply(reply)
    add_message(session_id, "assistant", reply)
    _print_assistant(reply)


def start_repl(state: SessionState) -> None:
    init_db()
    cfg = load_config()
    if not cfg.last_session_id:
        cfg.last_session_id = str(uuid.uuid4())
        save_config(cfg)

    session_id = cfg.last_session_id
    hist_file = _history_path()
    ps = PromptSession(history=FileHistory(hist_file))

    show_banner()
    rule("COMPANION MODE")
    console.print("[dim]Type commands or talk normally. `exit` to leave.[/dim]\n")

    while True:
        try:
            raw = ps.prompt("chat> ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Disconnecting.[/dim]")
            return

        if not raw:
            continue
        if raw in {"exit", "quit"}:
            console.print("[dim]Later.[/dim]")
            return

        console.print()

        cfg = load_config()

        low = raw.lower()
        mint = _extract_mint(raw)
        amt = _extract_number(raw)

        api_key = get_secret("anthropic_api_key")

        # ===== EXECUTE BUY / SELL DIRECTLY =====
        if mint and amt and _looks_like_buy(low):
            add_message(session_id, "user", raw)
            try:
                with spinner("Executing trade..."):
                    execute_trade(
                        state=state,
                        action="buy",
                        mint=mint,
                        amount=amt,
                        denominated_in_sol=True,
                    )

                if cfg.default_wallet_pubkey:
                    invalidate_wallet_cache(cfg.default_wallet_pubkey)

                if not api_key:
                    warn("Trade executed, but Anthropic key not set for in-character confirmation.")
                    _print_assistant("Trade executed.")
                    continue

                _trade_confirmation(
                    api_key,
                    session_id,
                    cfg,
                    action="buy",
                    mint=mint,
                    amount_str=f"{amt} SOL",
                )
                continue

            except TradeError as e:
                bad(str(e))
                console.print()
                continue

        if mint and _looks_like_sell(low):
            add_message(session_id, "user", raw)
            try:
                amount = "100%" if "all" in low else int(amt) if amt else "100%"
                with spinner("Executing trade..."):
                    execute_trade(
                        state=state,
                        action="sell",
                        mint=mint,
                        amount=amount,
                        denominated_in_sol=False,
                    )

                if cfg.default_wallet_pubkey:
                    invalidate_wallet_cache(cfg.default_wallet_pubkey)

                if not api_key:
                    warn("Trade executed, but Anthropic key not set for in-character confirmation.")
                    _print_assistant("Trade executed.")
                    continue

                _trade_confirmation(
                    api_key,
                    session_id,
                    cfg,
                    action="sell",
                    mint=mint,
                    amount_str=str(amount),
                )
                continue

            except TradeError as e:
                bad(str(e))
                console.print()
                continue

        # ===== BALANCE =====
        if _looks_like_balance(raw) and cfg.default_wallet_pubkey:
            add_message(session_id, "user", raw)

            if not api_key:
                bad("Anthropic key not set. Run: caas set anthropic <key>")
                console.print()
                continue

            try:
                invalidate_wallet_cache(cfg.default_wallet_pubkey)
                with spinner("Fetching wallet value..."):
                    v = get_wallet_value(cfg.default_wallet_pubkey, cache_seconds=0.0)

                _balance_reply(
                    api_key,
                    session_id,
                    cfg,
                    sol=v.sol,
                    usd=v.usd,
                    total_usd=v.total_usd,
                )
                continue

            except WalletValueError as e:
                bad(str(e))
                console.print()
                continue
            except Exception as e:
                bad(f"Unexpected error fetching wallet value: {e}")
                console.print()
                continue

        # ===== NORMAL CHAT =====
        if not api_key:
            bad("Anthropic key not set. Run: caas set anthropic <key>")
            console.print()
            continue

        add_message(session_id, "user", raw)

        runtime_context = _base_runtime_context(cfg)
        try:
            _assistant_reply(api_key, session_id, runtime_context)
        except (AnthropicAuthError, AnthropicAPIError) as e:
            bad(str(e))
            console.print()
            continue
