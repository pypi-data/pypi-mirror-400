import asyncio
import re
import os
from pathlib import Path
from typing import List, Dict, Any

# ================= OPTIONAL DEPENDENCIES =================
try:
    from mnemonic import Mnemonic
    MNEMONIC_AVAILABLE = True
except Exception:
    Mnemonic = None
    MNEMONIC_AVAILABLE = False

try:
    from eth_account import Account
    ETH_AVAILABLE = True
except Exception:
    Account = None
    ETH_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    requests = None
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except Exception:
    BeautifulSoup = None
    BS4_AVAILABLE = False
# ========================================================

from ..tor import TorProxy

# AI provider is OPTIONAL
try:
    from ..ai.providers import get_provider
    AI_AVAILABLE = True
except Exception:
    get_provider = None
    AI_AVAILABLE = False


class DarkWebCryptoHunter:
    def __init__(self):
        # ---- HARD GUARDS ----
        if not MNEMONIC_AVAILABLE:
            raise RuntimeError(
                "Missing dependency: mnemonic\n"
                "Install with: pip install deepstrike-ai[crypto]"
            )

        if not REQUESTS_AVAILABLE:
            raise RuntimeError(
                "Missing dependency: requests\n"
                "Install with: pip install deepstrike-ai[crypto]"
            )

        self.mnemo = Mnemonic("english")
        self.tor_session = self._get_tor_session()

        self.ai = None
        if AI_AVAILABLE:
            try:
                self.ai = get_provider("gemini") or get_provider("openai")
            except Exception:
                self.ai = None

        # Enhanced patterns
        self.patterns = {
            "bip39": r'(?i)\b(?:abandon able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add addict adult adventure)[^a-zA-Z]{0,10}(?:\w+\s*){11,23}\w+\b',
            "wif": r'[5KL][1-9A-HJ-NP-Za-km-z]{50,51}',
            "eth_priv": r'0x[a-fA-F0-9]{64}',
            "btc_priv": r'[2-9a-zA-HJ-NP-Z]{51,52}',
            "monero": r'4[0-9AB][1-9A-HJ-NP-Za-km-z]{93,94}',
        }

    def _get_tor_session(self):
        session = requests.Session()
        session.proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050",
        }
        return session

    async def hunt(self, paths: List[str]) -> List[Dict[str, Any]]:
        findings = []

        for path in paths:
            local_findings = await self._scan_filesystem(Path(path))
            findings.extend(local_findings)

        if self.ai:
            dark_findings = await self._ai_darkweb_scan()
            findings.extend(dark_findings)

        return self._dedupe_findings(findings)

    async def _scan_filesystem(self, path: Path) -> List[Dict]:
        findings = []

        if path.is_file() and path.suffix.lower() in {".txt", ".log", ".json", ".conf"}:
            content = await asyncio.to_thread(self._read_file, path)

            for ptype, pattern in self.patterns.items():
                for match in re.findall(pattern, content):
                    validated = await self._validate_crypto(ptype, match)
                    if validated:
                        findings.append({
                            "type": ptype,
                            "value": match,
                            "source": "filesystem",
                            "path": str(path),
                            **validated,
                        })

        return findings

    async def _ai_darkweb_scan(self) -> List[Dict]:
        if not self.ai:
            return []

        prompt = """
        Search dark web onion sites for leaked crypto wallets, private keys,
        BIP39 seeds, WIF keys. Return ONLY valid patterns found.
        """

        try:
            response = await self.ai.generate(prompt)
            findings = []

            for ptype, pattern in self.patterns.items():
                for match in re.findall(pattern, response):
                    findings.append({
                        "type": ptype,
                        "value": match,
                        "source": "darkweb_ai",
                        "validated": False,
                    })

            return findings
        except Exception:
            return []

    async def _validate_crypto(self, ptype: str, value: str) -> Dict[str, Any]:
        try:
            if (
                ptype == "bip39"
                and MNEMONIC_AVAILABLE
                and ETH_AVAILABLE
                and self.mnemo.check(value)
            ):
                seed = self.mnemo.to_seed(value)
                account = Account.from_key(seed[:32])
                balance = await self._check_eth_balance(account.address)

                return {
                    "address": account.address,
                    "balance": balance,
                    "valid": True,
                }
        except Exception:
            pass

        return {"valid": True}

    async def _check_eth_balance(self, address: str) -> float:
        try:
            resp = self.tor_session.get(
                "https://api.etherscan.io/api",
                params={
                    "module": "account",
                    "action": "balance",
                    "address": address,
                    "tag": "latest",
                },
                timeout=15,
            )
            return float(resp.json().get("result", 0)) / 1e18
        except Exception:
            return 0.0

    def _read_file(self, path: Path, max_bytes=2_000_000) -> str:
        with open(path, "r", errors="ignore") as f:
            return f.read(min(max_bytes, path.stat().st_size))

    def _dedupe_findings(self, findings: List[Dict]) -> List[Dict]:
        seen = set()
        result = []
        for f in findings:
            key = f"{f['type']}-{f['value'][:20]}"
            if key not in seen:
                seen.add(key)
                result.append(f)
        return result

