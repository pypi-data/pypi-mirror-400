# src/caas/pumpportal_launcher.py
from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import requests
from solders.commitment_config import CommitmentLevel
from solders.keypair import Keypair
from solders.rpc.config import RpcSendTransactionConfig
from solders.rpc.requests import SendVersionedTransaction
from solders.transaction import VersionedTransaction

IPFS_URL = "https://pump.fun/api/ipfs"
TRADE_LOCAL_URL = "https://pumpportal.fun/api/trade-local"

Pool = Literal["pump", "raydium", "pump-amm", "launchlab", "raydium-cpmm", "bonk", "auto"]


@dataclass
class LaunchResult:
    signature: str
    mint: str
    metadata_uri: str


class PumpPortalLaunchError(RuntimeError):
    pass


class PumpPortalLauncher:
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url

    def launch_token(
        self,
        signer_keypair: Keypair,
        *,
        name: str,
        symbol: str,
        description: str,
        twitter: str = "",
        telegram: str = "",
        website: str = "",
        show_name: bool = True,
        image_path: Path,
        dev_buy_sol: float = 1.0,
        slippage: float = 10.0,
        priority_fee: float = 0.0005,
        pool: Pool = "pump",
        is_mayhem_mode: bool = False,
        commitment: CommitmentLevel = CommitmentLevel.Confirmed,
        timeout: float = 30.0,
    ) -> LaunchResult:
        image_path = Path(image_path).expanduser().resolve()
        if not image_path.exists():
            raise PumpPortalLaunchError(f"Image not found: {image_path}")

        mime, _ = mimetypes.guess_type(str(image_path))
        if not mime:
            mime = "application/octet-stream"

        # 1) Upload metadata + image to IPFS (pump.fun)
        form_data = {
            "name": name,
            "symbol": symbol,
            "description": description,
            "twitter": twitter,
            "telegram": telegram,
            "website": website,
            "showName": "true" if show_name else "false",
        }

        with image_path.open("rb") as f:
            files = {"file": (image_path.name, f.read(), mime)}

        ipfs_resp = requests.post(IPFS_URL, data=form_data, files=files, timeout=timeout)
        if ipfs_resp.status_code != 200:
            raise PumpPortalLaunchError(f"IPFS upload failed: {ipfs_resp.status_code} {ipfs_resp.text}")

        try:
            ipfs_json = ipfs_resp.json()
            metadata_uri = ipfs_json["metadataUri"]
        except Exception as e:
            raise PumpPortalLaunchError(f"IPFS response parse failed: {e} :: {ipfs_resp.text}")

        token_metadata = {"name": name, "symbol": symbol, "uri": metadata_uri}

        # 2) Request unsigned create tx bytes from trade-local (NO api key)
        mint_keypair = Keypair()

        body = {
            "publicKey": str(signer_keypair.pubkey()),
            "action": "create",
            "tokenMetadata": token_metadata,
            "mint": str(mint_keypair.pubkey()),
            "denominatedInSol": "true",
            "amount": dev_buy_sol,
            "slippage": slippage,
            "priorityFee": priority_fee,
            "pool": pool,
            "isMayhemMode": "true" if is_mayhem_mode else "false",
        }

        r = requests.post(
            TRADE_LOCAL_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(body),
            timeout=timeout,
        )
        if r.status_code != 200:
            raise PumpPortalLaunchError(f"trade-local failed: {r.status_code} {r.text}")

        unsigned = VersionedTransaction.from_bytes(r.content)

        # create requires both signatures: mint + signer (payer)
        signed = VersionedTransaction(unsigned.message, [mint_keypair, signer_keypair])

        cfg = RpcSendTransactionConfig(preflight_commitment=commitment)
        payload = SendVersionedTransaction(signed, cfg).to_json()

        rpc_resp = requests.post(
            self.rpc_url,
            headers={"Content-Type": "application/json"},
            data=payload,
            timeout=timeout,
        )
        rpc_resp.raise_for_status()
        j = rpc_resp.json()

        if "result" not in j:
            raise PumpPortalLaunchError(f"RPC send failed: {j}")

        return LaunchResult(signature=j["result"], mint=str(mint_keypair.pubkey()), metadata_uri=metadata_uri)
