from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from solders.keypair import Keypair
import base64

@dataclass
class SessionState:
    wallet_unlocked: bool = False
    _wallet: Optional[Keypair] = None

    def lock(self) -> None:
        self.wallet_unlocked = False
        self._wallet = None

    def unlock_with_secret(self, secret: str) -> None:
        self._wallet = parse_solana_secret(secret)
        self.wallet_unlocked = True

    def wallet(self) -> Keypair:
        if not self.wallet_unlocked or self._wallet is None:
            raise RuntimeError("Wallet is locked. Run: caas unlock")
        return self._wallet

def parse_solana_secret(secret: str) -> Keypair:
    s = secret.strip()

    if s.startswith("[") and s.endswith("]"):
        import json
        arr = json.loads(s)
        return Keypair.from_bytes(bytes(arr))

    try:
        import base58
        b = base58.b58decode(s)
        if len(b) == 32:
            return Keypair.from_seed(b)
        if len(b) == 64:
            return Keypair.from_bytes(b)
    except Exception:
        pass

    try:
        b = base64.b64decode(s)
        if len(b) == 32:
            return Keypair.from_seed(b)
        if len(b) == 64:
            return Keypair.from_bytes(b)
    except Exception:
        pass

    raise ValueError("Unrecognized Solana private key format.")
