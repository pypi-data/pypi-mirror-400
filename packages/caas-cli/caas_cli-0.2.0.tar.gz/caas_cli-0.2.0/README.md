# CAAS

**Companion as a Service**  
A terminal-native Solana companion for **Pump.fun trading**, wallet management, and conversational command execution.

CAAS is designed to feel like a _sessioned assistant_ it remembers state, gates your wallet, shows live balances, and lets you trade or talk naturally from a single CLI.

---

## Install

```bash
pip install caas-cli
```

---

## First-Time Setup

```bash
caas init
```

This walks you through:

- Solana RPC configuration
- Anthropic API key (stored in OS keychain)
- Solana wallet (masked input, Windows-safe)

---

## Wallet Gate (Safety Layer)

Before any trade, your wallet must be unlocked:

```bash
caas unlock
```

- Unlocks wallet in-memory for 30 minutes by default
- Automatically re-locks after TTL
- Manually lock anytime:

```bash
caas lock wallet
```

> This is a convenience gate not encryption. Use responsibly.

---

## Trading (Pump.fun)

Buy tokens with SOL:

```bash
caas buy --solana 1 <mint>
```

Sell tokens:

```bash
caas sell --solana "25%" <mint>
caas sell --solana all <mint>
```

Features:

- Slippage + priority fee control
- Pool selection (`pump`, `auto`, etc.)
- Spinner-wrapped transactions
- Clean success / warning output

---

## Portfolio & Status

View Saved Keys:

```bash
caas show keys
```

View full portfolio:

```bash
caas show port
```

Check overall status:

```bash
caas status
```

Shows:

- RPC
- Anthropic key
- Wallet state
- Unlock gate
- Slippage / fees / pool

---

## Configuration Commands

```bash
caas set rpc
caas set anthropic
caas set wallet
caas set wallet-file <path>
caas set slippage
caas set priority-fee
caas set pool
```

All secrets are stored securely via OS keychain.

---

## Companion Mode

Start an interactive session:

```bash
caas start
```

In companion mode you can:

- Talk normally
- Issue commands like `buy`, `sell`, `status`
- Let CAAS manage context and state across turns

This is where the Companion part lives.

---

## Reset Everything

```bash
caas reset
```

Clears:

- Config
- Wallet gate
- Stored secrets

---

## Help

```bash
caas help
```

Shows the full rich, in-terminal help panel.

---

## Notes

- Built with **Typer + Rich** for a native terminal UX
- Wallet value + portfolio fetched via a secure proxy (no API keys shipped)
- Designed for fast iteration, not babysitting
