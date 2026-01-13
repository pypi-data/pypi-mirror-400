import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Dict, List

load_dotenv()

@dataclass
class Config:
    # AI Keys
    openai_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    grok_key: str = os.getenv("GROK_API_KEY", "")
    
    # Crypto
    wallet_addr: str = os.getenv("WALLET_ADDR", "")
    
    # TOR
    tor_port: int = int(os.getenv("TOR_PORT", "9050"))
    tor_socks: str = os.getenv("TOR_SOCKS", "127.0.0.1:9050")
    
    # Paths
    reports_dir: str = os.getenv("REPORTS_DIR", "./reports")
    
    @property
    def available_ais(self) -> List[str]:
        ais = []
        if self.openai_key: ais.append("openai")
        if self.anthropic_key: ais.append("anthropic")
        if self.grok_key: ais.append("grok")
        return ais

config = Config()
