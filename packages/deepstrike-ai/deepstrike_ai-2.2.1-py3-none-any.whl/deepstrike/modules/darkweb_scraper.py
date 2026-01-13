from __future__ import annotations

import asyncio
import re
import os
from typing import List, Dict, Any
from pathlib import Path
from urllib.parse import urljoin, urlparse

from ..tor import TorProxy

# ================= OPTIONAL DEPENDENCIES =================
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

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except Exception:
    aiohttp = None
    AIOHTTP_AVAILABLE = False
# ========================================================


class DarkWebScraper:
    def __init__(self):
        if not (REQUESTS_AVAILABLE and BS4_AVAILABLE and AIOHTTP_AVAILABLE):
            raise RuntimeError(
                "DarkWebScraper requires optional dependencies.\n"
                "Install with: pip install deepstrike-ai[scraper]"
            )

        self.tor_session = self._get_tor_session()
        self.download_dir = Path("darkweb_downloads")
        self.download_dir.mkdir(exist_ok=True)

        self.cc_patterns = {
            "visa": r"4[0-9]{12}(?:[0-9]{3})?",
            "mastercard": r"5[1-5][0-9]{14}",
            "amex": r"3[47][0-9]{13}",
            "discover": r"6(?:011|5[0-9]{2})[0-9]{12}",
        }

    def _get_tor_session(self):
        session = requests.Session()
        session.proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050",
        }
        return session

    async def scrape(
        self, query: str, download: bool = False, max_pages: int = 5
    ) -> List[Dict]:
        onion_sites = [
            f"http://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/?q={query}",
            "http://pastesite.onion",
            "http://leakforums.onion/search",
        ]

        results = []

        async with aiohttp.ClientSession() as session:
            for site in onion_sites[:max_pages]:
                try:
                    async with session.get(
                        site,
                        proxy="socks5://127.0.0.1:9050",
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as resp:
                        html = await resp.text()
                        soup = BeautifulSoup(html, "html.parser")

                        text = soup.get_text()
                        cc_matches = self._extract_cc(text)

                        result = {
                            "site": site,
                            "cc_cards": cc_matches,
                            "title": soup.title.string if soup.title else "Unknown",
                        }

                        if download:
                            await self._download_assets(session, soup, site)

                        results.append(result)

                except Exception as e:
                    print(f"Failed {site}: {e}")

        return results

    def _extract_cc(self, text: str) -> List[str]:
        cards = []
        for cctype, pattern in self.cc_patterns.items():
            for match in re.findall(pattern, text):
                if self._luhn_check(match):
                    cards.append(f"{cctype}: {match}")
        return cards

    def _luhn_check(self, card_number: str) -> bool:
        digits = [int(d) for d in card_number if d.isdigit()]
        if len(digits) < 13:
            return False

        total = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                doubled = digit * 2
                total += doubled // 10 + doubled % 10
            else:
                total += digit

        return total % 10 == 0

    async def _download_assets(
        self,
        session: aiohttp.ClientSession,
        soup: BeautifulSoup,
        base_url: str,
    ):
        for img in soup.find_all("img", limit=10):
            img_url = urljoin(base_url, img.get("src", ""))
            await self._download_file(session, img_url, "images")

        for link in soup.find_all(
            "a", href=re.compile(r"\.(pdf|doc|txt|zip)$"), limit=5
        ):
            file_url = urljoin(base_url, link["href"])
            await self._download_file(session, file_url, "files")

    async def _download_file(
        self, session: aiohttp.ClientSession, url: str, category: str
    ):
        try:
            async with session.get(
                url, proxy="socks5://127.0.0.1:9050"
            ) as resp:
                if resp.status == 200:
                    filename = (
                        os.path.basename(urlparse(url).path)
                        or f"{category}_{hash(url)}.bin"
                    )
                    path = self.download_dir / category / filename
                    path.parent.mkdir(exist_ok=True)

                    with open(path, "wb") as f:
                        f.write(await resp.read())
        except Exception:
            pass

    async def hunt_credit_cards(self, query: str) -> List[str]:
        results = await self.scrape(query)
        all_cards = []
        for result in results:
            all_cards.extend(result.get("cc_cards", []))
        return list(set(all_cards))

