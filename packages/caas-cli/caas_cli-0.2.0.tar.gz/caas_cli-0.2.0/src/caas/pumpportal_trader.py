from __future__ import annotations
import requests
from dataclasses import dataclass
from typing import Literal, Union

from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig

TRADE_LOCAL_URL = "https://pumpportal.fun/api/trade-local"

Pool = Literal["pump", "raydium", "pump-amm", "launchlab", "raydium-cpmm", "bonk", "auto"]
Action = Literal["buy", "sell"]

@dataclass
class TradeResult:
    signature: str

class PumpPortalTrader:
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url

    def trade(
        self,
        wallet: Keypair,
        action: Action,
        mint: str,
        amount: Union[float, int, str],
        *,
        denominated_in_sol: bool,
        slippage: float,
        priority_fee: float,
        pool: Pool = "auto",
        commitment: CommitmentLevel = CommitmentLevel.Confirmed,
    ) -> TradeResult:
        body = {
            "publicKey": str(wallet.pubkey()),
            "action": action,
            "mint": mint,
            "amount": amount,
            "denominatedInSol": "true" if denominated_in_sol else "false",
            "slippage": slippage,
            "priorityFee": priority_fee,
            "pool": pool,
        }

        r = requests.post(TRADE_LOCAL_URL, data=body, timeout=30)
        r.raise_for_status()

        unsigned = VersionedTransaction.from_bytes(r.content)
        signed = VersionedTransaction(unsigned.message, [wallet])

        cfg = RpcSendTransactionConfig(preflight_commitment=commitment)
        payload = SendVersionedTransaction(signed, cfg).to_json()

        rpc_resp = requests.post(
            self.rpc_url,
            headers={"Content-Type": "application/json"},
            data=payload,
            timeout=30,
        )
        rpc_resp.raise_for_status()
        j = rpc_resp.json()

        if "result" not in j:
            raise RuntimeError(f"RPC send failed: {j}")

        return TradeResult(signature=j["result"])
