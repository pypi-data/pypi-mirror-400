# src/caas/cli.py  (FULL FILE with: caas launch token)
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from .config import load_config, save_config
from .gate import clear as clear_gate
from .gate import is_unlocked, set_unlocked
from .memory import init_db
from .pumpportal_launcher import PumpPortalLaunchError, PumpPortalLauncher
from .pumpportal_trader import PumpPortalTrader
from .repl import start_repl
from .secrets import clear_all_secrets, get_secret, set_secret
from .session import SessionState, parse_solana_secret
from .ui import bad, console, ok, panel, rule, show_banner, warn, spinner
from .wallet_value import (
    WalletPortfolioError,
    WalletValueError,
    get_wallet_portfolio,
    get_wallet_value,
)
from .pnl import record_trade_async, enrich_pending_trades_now
from .memory import list_positions


app = typer.Typer(
    add_completion=False,
    add_help_option=False,
    help="CAAS - Companion as a Service (Claude + Pump.fun trading).",
)

STATE = SessionState()


def _ensure_init() -> None:
    init_db()


def _welcome_once_print_boot_panel() -> bool:
    cfg = load_config()
    if cfg.seen_welcome:
        return False

    body = Text()
    body.append("Welcome to CAAS.\n\n", style="bold")
    body.append("Run ", style="dim")
    body.append("caas help", style="bold cyan")
    body.append(" or ", style="dim")
    body.append("caas --help", style="bold cyan")
    body.append(" to get started.\n\n", style="dim")
    body.append("Recommended first run:\n", style="dim")
    body.append("  caas init\n  caas unlock\n  caas buy --solana 1 <mint>\n", style="dim")

    console.print(Panel(body, border_style="accent", title="[title]Boot Sequence[/title]"))

    cfg.seen_welcome = True
    save_config(cfg)
    return True


def _ensure_wallet_loaded_for_trade() -> None:
    if not is_unlocked():
        bad("Wallet locked. Run: caas unlock")
        raise typer.Exit(code=1)

    secret = get_secret("solana_private_key")
    if not secret:
        bad("No wallet set. Run: caas set wallet")
        raise typer.Exit(code=1)

    STATE.unlock_with_secret(secret)


def _read_masked_windows(prompt: str) -> str:
    from .winmask import read_masked

    return read_masked(prompt)


def _ask_wallet_secret() -> str:
    if sys.platform.startswith("win"):
        console.print("[dim]Masked input is ON (Windows-safe). Use Ctrl+V to paste.[/dim]")
        return _read_masked_windows("Solana private key: ").strip()
    return Prompt.ask("Solana private key", password=True).strip()


def _ask_anthropic_secret() -> str:
    if sys.platform.startswith("win"):
        console.print("[dim]Masked input is ON (Windows-safe). Use Ctrl+V to paste.[/dim]")
        return _read_masked_windows("Anthropic API key: ").strip()
    return Prompt.ask("Anthropic API key", password=True).strip()


def _ask_rpc_url() -> str:
    if sys.platform.startswith("win"):
        console.print("[dim]Masked input is ON (Windows-safe). Use Ctrl+V to paste.[/dim]")
        return _read_masked_windows("Solana RPC URL: ").strip()
    return Prompt.ask("Solana RPC URL", password=True).strip()


def _wallet_value_suffix(pubkey: str) -> str:
    try:
        with spinner("Fetching wallet value..."):
            v = get_wallet_value(pubkey, cache_seconds=10.0)
        return f" [ok]({v.sol:.2f} SOL) (${v.usd:,.2f})[/ok]"
    except WalletValueError:
        return ""
    except Exception:
        return ""


def _render_pretty_help() -> None:
    show_banner()
    rule("HELP")

    txt = (
        "[title]Quickstart[/title]\n"
        "  caas init\n"
        "  caas unlock\n"
        "  caas buy --solana 1 <mint>\n"
        "  caas sell --solana \"50%\" <mint>\n"
        "  caas start\n\n"
        "[title]Setup[/title]\n"
        "  caas set rpc <url>\n"
        "  caas set anthropic <key>\n"
        "  caas set wallet\n"
        "  caas set wallet-file <path>\n"
        "  caas set slippage <percent>\n"
        "  caas set priority-fee <sol>\n"
        "  caas set pool <pump|auto|...>\n\n"
        "[title]Launch[/title]\n"
        "  caas launch token\n\n"
        "[title]Wallet Gate[/title]\n"
        "  caas unlock --ttl 1800    (unlocks across commands for 30 min)\n"
        "  caas lock wallet          (re-lock immediately)\n\n"
        "[title]Show[/title]\n"
        "  caas status               (prints config + gate + wallet state summary)\n"
        "  caas show port            (portfolio + token balances)\n"
        "  caas show keys            (prints full values; requires unlock + confirm)\n\n"
        "[title]Trading[/title]\n"
        "  caas buy  --solana 1 <mint>\n"
        "  caas sell --solana \"25%\" <mint>\n"
        "  caas sell --solana all <mint>\n\n"
        "[title]Reset[/title]\n"
        "  caas reset\n\n"
        "[title]Companion Mode[/title]\n"
        "  caas start\n"
        "  Then talk normally, or type commands like: buy, sell, status\n"
    )

    console.print(Panel(txt, border_style="accent"))


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    help_: bool = typer.Option(False, "--help", "-h", help="Show this message and exit.", is_eager=True),
):
    _ensure_init()

    if help_:
        _render_pretty_help()
        raise typer.Exit(code=0)

    if ctx.invoked_subcommand is None:
        show_banner()
        _welcome_once_print_boot_panel()
        console.print("[dim]Use `caas help` or `caas --help` to get started.[/dim]")
        panel(
            "Commands",
            "init - status - start - unlock - lock wallet - buy - sell - launch token\n\n"
            "Config: set rpc - set anthropic - set wallet",
        )


set_app = typer.Typer(help="Set configuration/secrets.")
app.add_typer(set_app, name="set")


@app.command("help")
def pretty_help():
    _render_pretty_help()


@set_app.command("rpc")
def set_rpc(
    value: Optional[str] = typer.Argument(None, help="RPC URL. If omitted, you will be prompted."),
):
    cfg = load_config()
    show_banner()
    rule("CONFIG")

    url = (value or "").strip()
    if not url:
        url = _ask_rpc_url()

    cfg.rpc_url = url
    save_config(cfg)
    ok("RPC set.")


@set_app.command("anthropic")
def set_anthropic(
    key: Optional[str] = typer.Argument(None, help="Anthropic API key. If omitted, you will be prompted."),
):
    show_banner()
    rule("SECRETS")

    k = (key or "").strip()
    if not k:
        k = _ask_anthropic_secret()

    set_secret("anthropic_api_key", k)
    ok("Anthropic key saved to OS keychain.")


@set_app.command("wallet")
def set_wallet():
    show_banner()
    rule("SECRETS")

    console.print("[dim]Paste your Solana private key then press Enter.[/dim]")
    console.print("[dim]Tip: On Windows CMD, use Ctrl+V for paste in masked prompts.[/dim]")

    secret = _ask_wallet_secret()
    set_secret("solana_private_key", secret)

    try:
        kp = parse_solana_secret(secret)
    except Exception:
        bad("Unrecognized Solana private key format.")
        warn("If paste is acting weird, use: caas set wallet-file <path>")
        raise typer.Exit(code=1)

    cfg = load_config()
    cfg.default_wallet_pubkey = str(kp.pubkey())
    save_config(cfg)

    ok(f"Wallet saved. Pubkey: {kp.pubkey()}")
    warn("Use `caas unlock` before trading. Use `caas lock wallet` when done.")


@set_app.command("wallet-file")
def set_wallet_file(path: str = typer.Argument(..., help="Path to a file containing the private key")):
    show_banner()
    rule("SECRETS")

    p = Path(path)
    if not p.exists():
        bad(f"File not found: {path}")
        raise typer.Exit(code=1)

    secret = p.read_text("utf-8").strip()
    set_secret("solana_private_key", secret)

    try:
        kp = parse_solana_secret(secret)
    except Exception as e:
        bad(str(e))
        raise typer.Exit(code=1)

    cfg = load_config()
    cfg.default_wallet_pubkey = str(kp.pubkey())
    save_config(cfg)

    ok(f"Wallet saved from file. Pubkey: {kp.pubkey()}")
    warn("Use `caas unlock` before trading. Use `caas lock wallet` when done.")


@set_app.command("slippage")
def set_slippage(
    value: Optional[float] = typer.Argument(None, help="Slippage percent. If omitted, you will be prompted."),
):
    cfg = load_config()
    show_banner()
    rule("CONFIG")

    v = value
    if v is None:
        v = float(Prompt.ask("Slippage percent", default=str(cfg.slippage)))

    cfg.slippage = float(v)
    save_config(cfg)
    ok(f"Slippage set to {cfg.slippage}%.")


@set_app.command("priority-fee")
def set_priority_fee(
    value: Optional[float] = typer.Argument(None, help="Priority fee in SOL. If omitted, you will be prompted."),
):
    cfg = load_config()
    show_banner()
    rule("CONFIG")

    v = value
    if v is None:
        v = float(Prompt.ask("Priority fee in SOL", default=str(cfg.priority_fee)))

    cfg.priority_fee = float(v)
    save_config(cfg)
    ok(f"Priority fee set to {cfg.priority_fee} SOL.")


@set_app.command("pool")
def set_pool(
    value: Optional[str] = typer.Argument(None, help="Default pool (pump/auto/...). If omitted, you will be prompted."),
):
    cfg = load_config()
    show_banner()
    rule("CONFIG")

    v = (value or "").strip()
    if not v:
        v = Prompt.ask("Default pool (pump/auto/...)", default=cfg.pool).strip()

    cfg.pool = v
    save_config(cfg)
    ok(f"Pool set to {cfg.pool}.")


show_app = typer.Typer(help="Show configuration and portfolio.")
app.add_typer(show_app, name="show")


@show_app.command("port")
def show_port():
    cfg = load_config()
    show_banner()
    rule("PORTFOLIO")

    if not cfg.default_wallet_pubkey:
        bad("Wallet not set. Run: caas set wallet")
        raise typer.Exit(code=1)

    pubkey = cfg.default_wallet_pubkey

    # best-effort: catch up PnL quickly if a trade just happened
    if cfg.rpc_url:
        try:
            enrich_pending_trades_now(rpc_url=cfg.rpc_url, wallet_pubkey=pubkey, limit=6)
        except Exception:
            pass

    try:
        with spinner("Fetching portfolio..."):
            port = get_wallet_portfolio(pubkey, cache_seconds=10.0)
    except WalletPortfolioError as e:
        bad(str(e))
        return
    except Exception as e:
        bad(f"Unexpected error fetching portfolio: {e}")
        return

    # cost basis map (mint -> cost_usd)
    try:
        pos_map = {p["mint"]: p for p in list_positions(pubkey)}
    except Exception:
        pos_map = {}

    t = Table(show_header=False, box=None, pad_edge=False)

    for it in port.items:
        amt = f"{it.ui_amount:,.4f}"
        sym = it.symbol or ""
        usd_val = float(it.value_usd or 0.0)
        usd = f"${usd_val:,.2f}" if it.value_usd is not None else "$0.00"
        name = it.name or it.symbol or it.address[:4] + "..." + it.address[-4:]

        # default: no PnL shown unless we have cost basis
        pnl_suffix = ""

        p = pos_map.get(it.address)
        if p:
            cost = float(p.get("cost_usd") or 0.0)
            if cost > 0:
                pnl = usd_val - cost
                pct = (pnl / cost) * 100.0
                is_up = pnl >= 0
                style = "ok" if is_up else "bad"
                sign = "+" if is_up else ""
                pnl_suffix = f" [{style}]({sign}${pnl:,.2f} {pct:+.1f}%)[/{style}]"

        t.add_row(name, f"[ok]({amt} {sym}) ({usd})[/ok]{pnl_suffix}")

    console.print(t)

@show_app.command("keys")
def show_keys(
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation prompt."),
):
    show_banner()
    rule("KEYS")

    if not is_unlocked():
        bad("Wallet locked. Run: caas unlock")
        raise typer.Exit(code=1)

    warn("This prints secrets in full. Be careful with screenshots, logs, screen-share, and copy/paste.")

    if not yes:
        confirm = Prompt.ask("Type SHOW_KEYS to confirm").strip()
        if confirm != "SHOW_KEYS":
            warn("Canceled.")
            raise typer.Exit(code=0)

    cfg = load_config()
    rpc = (cfg.rpc_url or "").strip()
    pubkey = (cfg.default_wallet_pubkey or "").strip()
    anthropic = (get_secret("anthropic_api_key") or "").strip()
    sol_secret = (get_secret("solana_private_key") or "").strip()

    body = (
        f"[title]RPC[/title]\n{rpc or '[dim](not set)[/dim]'}\n\n"
        f"[title]Anthropic API Key[/title]\n{anthropic or '[dim](not set)[/dim]'}\n\n"
        f"[title]Solana Wallet Pubkey[/title]\n{pubkey or '[dim](not set)[/dim]'}\n\n"
        f"[title]Solana Private Key[/title]\n{sol_secret or '[dim](not set)[/dim]'}\n"
    )
    console.print(Panel(body, border_style="accent"))


@app.command("status")
def status():
    cfg = load_config()
    show_banner()
    rule("STATUS")

    rpc_set = bool(cfg.rpc_url)
    anthropic_set = bool(get_secret("anthropic_api_key"))
    wallet_set = bool(cfg.default_wallet_pubkey)

    wallet_row = "[bad]not set[/bad]"
    if wallet_set and cfg.default_wallet_pubkey:
        wallet_row = f"[ok]set[/ok]{_wallet_value_suffix(cfg.default_wallet_pubkey)}"

    t = Table(show_header=False, box=None, pad_edge=False)
    t.add_row("RPC", "[ok]set[/ok]" if rpc_set else "[bad]not set[/bad]")
    t.add_row("Anthropic", "[ok]set[/ok]" if anthropic_set else "[bad]not set[/bad]")
    t.add_row("Wallet", wallet_row)
    t.add_row("Wallet gate", "[ok]unlocked[/ok]" if is_unlocked() else "[warn]locked[/warn]")
    t.add_row("Slippage", f"{cfg.slippage}%")
    t.add_row("Priority fee", f"{cfg.priority_fee} SOL")
    t.add_row("Pool", cfg.pool)
    console.print(t)

    console.print("\n[dim]Use `caas show port` or `caas show keys`.[/dim]")


@app.command("reset")
def reset(yes: bool = typer.Option(False, "--yes", help="Skip confirmation prompt.")):
    show_banner()
    rule("RESET")

    if not yes:
        confirm = Prompt.ask("Type RESET to confirm").strip()
        if confirm != "RESET":
            warn("Canceled.")
            raise typer.Exit(code=0)

    try:
        STATE.lock()
    except Exception:
        pass
    try:
        clear_gate()
    except Exception:
        pass

    try:
        from .config import config_path

        p = config_path()
        if p.exists():
            p.unlink()
            ok("Config cleared.")
        else:
            ok("Config already empty.")
    except Exception as e:
        warn(f"Config clear warning: {e}")

    clear_all_secrets()
    ok("Secrets cleared (anthropic + wallet).")

    panel("Next", "Run `caas init` to set up again, or use `caas set ...` commands.")


@app.command("init")
def init_wizard():
    cfg = load_config()
    show_banner()
    rule("INIT")

    if not cfg.rpc_url:
        cfg.rpc_url = _ask_rpc_url()
        save_config(cfg)
        ok("RPC saved.")
    else:
        ok("RPC already set.")

    if not get_secret("anthropic_api_key"):
        key = _ask_anthropic_secret()
        set_secret("anthropic_api_key", key)
        ok("Anthropic key saved.")
    else:
        ok("Anthropic key already set.")

    if not get_secret("solana_private_key"):
        console.print("[dim]Paste your Solana private key then press Enter.[/dim]")
        console.print("[dim]Tip: On Windows CMD, use Ctrl+V for paste in masked prompts.[/dim]")

        secret = _ask_wallet_secret()
        set_secret("solana_private_key", secret)

        try:
            kp = parse_solana_secret(secret)
        except Exception:
            bad("Unrecognized Solana private key format.")
            warn("If paste keeps acting weird, use: caas set wallet-file <path>")
            raise typer.Exit(code=1)

        cfg.default_wallet_pubkey = str(kp.pubkey())
        save_config(cfg)
        ok(f"Wallet saved. Pubkey: {kp.pubkey()}")
    else:
        ok("Wallet already set.")

    panel("Heads up", "Lock your wallet after trading: `caas lock wallet`.")
    ok("Init complete.")


@app.command("start")
def start():
    start_repl(STATE)


@app.command("lock")
def lock_wallet(what: str = typer.Argument(..., help="Use: caas lock wallet")):
    if what != "wallet":
        raise typer.BadParameter("Only supported: wallet")
    STATE.lock()
    clear_gate()
    show_banner()
    rule("SECURITY")
    ok("Wallet locked (cleared from session memory).")


@app.command("unlock")
def unlock_wallet(ttl: int = typer.Option(1800, "--ttl", help="Unlock duration in seconds (default 1800).")):
    secret = get_secret("solana_private_key")
    show_banner()
    rule("SECURITY")

    if not secret:
        bad("No wallet set. Run: caas set wallet")
        raise typer.Exit(code=1)

    STATE.unlock_with_secret(secret)
    set_unlocked(ttl_seconds=int(ttl))

    ok("Wallet unlocked for this session.")
    warn("No password yet. This is a convenience gate, not real encryption.")


@app.command("buy")
def buy(
    solana: float = typer.Option(..., "--solana", help="Amount of SOL to spend."),
    mint: str = typer.Argument(..., help="Token mint address (CA)."),
):
    cfg = load_config()
    show_banner()
    rule("TRADE")

    if not cfg.rpc_url:
        bad("RPC not set. Run: caas set rpc <url>")
        raise typer.Exit(code=1)

    _ensure_wallet_loaded_for_trade()

    trader = PumpPortalTrader(cfg.rpc_url)

    with spinner("Buying..."):
        res = trader.trade(
            STATE.wallet(),
            action="buy",
            mint=mint,
            amount=solana,
            denominated_in_sol=True,
            slippage=cfg.slippage,
            priority_fee=cfg.priority_fee,
            pool=cfg.pool,
        )

    # record for accurate PnL using Helius tx lookup (async so it stays fast)
    wallet_pubkey = str(STATE.wallet().pubkey())
    record_trade_async(
        rpc_url=cfg.rpc_url,
        wallet_pubkey=wallet_pubkey,
        mint=mint,
        side="buy",
        signature=res.signature,
    )

    ok(f"Bought {solana:.2f} SOL of {mint}")
    warn("Use `caas show port` to see token balances + PnL.")



@app.command("sell")
def sell(
    solana: str = typer.Option(..., "--solana", help='Percent ("35%"), amount ("12345"), or "all".'),
    mint: str = typer.Argument(..., help="Token mint address (CA)."),
):
    cfg = load_config()
    show_banner()
    rule("TRADE")

    if not cfg.rpc_url:
        bad("RPC not set. Run: caas set rpc <url>")
        raise typer.Exit(code=1)

    _ensure_wallet_loaded_for_trade()

    v = solana.strip().lower()
    if v == "all":
        amount = "100%"
    elif v.endswith("%"):
        amount = v
    else:
        try:
            amount = int(v)
        except ValueError:
            bad('Invalid --solana. Use "all", "35%", or "12345".')
            raise typer.Exit(code=1)

    trader = PumpPortalTrader(cfg.rpc_url)

    with spinner("Selling..."):
        res = trader.trade(
            STATE.wallet(),
            action="sell",
            mint=mint,
            amount=amount,
            denominated_in_sol=False,
            slippage=cfg.slippage,
            priority_fee=cfg.priority_fee,
            pool=cfg.pool,
        )

    wallet_pubkey = str(STATE.wallet().pubkey())
    record_trade_async(
        rpc_url=cfg.rpc_url,
        wallet_pubkey=wallet_pubkey,
        mint=mint,
        side="sell",
        signature=res.signature,
    )

    ok(f"Sell sent for {mint}.")
    warn("Use `caas show port` to see token balances + PnL.")



launch_app = typer.Typer(help="Launch tokens via PumpPortal.")
app.add_typer(launch_app, name="launch")


def _resolve_image_path(raw: str, images_dir: Path) -> Path:
    p = Path(raw).expanduser()
    if p.is_absolute() or p.parent != Path("."):
        return p
    return images_dir / raw


def _copy_to_clipboard(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return False

    # 1) best case: pyperclip
    try:
        import pyperclip  # type: ignore
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    # 2) platform fallbacks
    try:
        import subprocess, sys

        if sys.platform.startswith("win"):
            subprocess.run("clip", input=text, text=True, check=True, shell=True)
            return True
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            return True

        # linux: try wl-copy then xclip
        for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"]):
            try:
                subprocess.run(cmd, input=text, text=True, check=True)
                return True
            except Exception:
                continue
    except Exception:
        pass

    return False



@launch_app.command("token")
def launch_token():
    cfg = load_config()
    show_banner()
    rule("LAUNCH")

    if not cfg.rpc_url:
        bad("RPC not set. Run: caas set rpc <url>")
        raise typer.Exit(code=1)

    _ensure_wallet_loaded_for_trade()

    images_dir = Path.cwd() / "caas-cli/images"
    images_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[dim]Token images folder: {images_dir}[/dim]")

    # only ask for what you want
    name = Prompt.ask("Token name").strip()
    symbol = Prompt.ask("Token symbol").strip()
    description = Prompt.ask("Description", default="").strip()
    twitter = Prompt.ask("Twitter (optional)", default="").strip()
    telegram = Prompt.ask("Telegram (optional)", default="").strip()
    website = Prompt.ask("Website (optional)", default="").strip()

    img_raw = Prompt.ask("Token image (filename in ./caas-cli/images or full path)").strip()
    image_path = _resolve_image_path(img_raw, images_dir)
    if not image_path.exists():
        bad(f"Image not found: {image_path.name if image_path.is_absolute() else str(image_path)}")
        raise typer.Exit(code=1)

    dev_buy_sol = float(Prompt.ask("Dev buy (SOL)", default="1").strip())

    console.print()
    warn("Ready. Press Enter again to launch.")
    Prompt.ask("", default="", show_default=False)

    launcher = PumpPortalLauncher(cfg.rpc_url)

    try:
        with spinner("Launching token..."):
            res = launcher.launch_token(
                STATE.wallet(),
                name=name,
                symbol=symbol,
                description=description,
                twitter=twitter,
                telegram=telegram,
                website=website,
                show_name=True,               # default
                image_path=image_path,
                dev_buy_sol=dev_buy_sol,
                slippage=cfg.slippage,        # default from config
                priority_fee=cfg.priority_fee,# default from config
                pool="pump",                  # default
                is_mayhem_mode=False,         # default
            )
    except PumpPortalLaunchError as e:
        bad(str(e))
        console.print()
        raise typer.Exit(code=1)
    except Exception as e:
        bad(f"Unexpected launch error: {e}")
        console.print()
        raise typer.Exit(code=1)

    # output: single “dump” line + clipboard copy
    ca = str(res.mint).strip()
    sym = (symbol or "").strip()
    nm = (name or "").strip()

    copied = _copy_to_clipboard(ca)
    suffix = " [dim](copied)[/dim]" if copied else ""

    # e.g. Brain $BRAIN CA
    console.print(f"[ok]{nm} ${sym} {ca}[/ok]{suffix}")
