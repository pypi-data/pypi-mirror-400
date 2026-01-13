import sys
import socket
import importlib.util
from typing import List, Tuple

CHECKS = [
    ("PySocks (socks)", "socks"),
    ("stem", "stem"),
    ("lxml", "lxml"),
    ("cryptography", "cryptography"),
    ("aiohttp", "aiohttp"),
]

def _check_module(name: str) -> Tuple[bool, str]:
    spec = importlib.util.find_spec(name)
    return (spec is not None, name)

def _check_port(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except Exception:
        return False

def run_doctor() -> int:
    print("🩺 DeepStrike Doctor\n")

    # Python
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📦 Virtualenv: {'YES' if sys.prefix != sys.base_prefix else 'NO'}\n")

    # Modules
    print("🔎 Python Dependencies:")
    failures: List[str] = []
    for label, mod in CHECKS:
        ok, _ = _check_module(mod)
        if ok:
            print(f"  ✅ {label}")
        else:
            print(f"  ❌ {label}  → missing")
            failures.append(mod)

    # TOR
    print("\n🧅 TOR Services:")
    tor_socks = _check_port("127.0.0.1", 9050)
    tor_ctrl = _check_port("127.0.0.1", 9051)

    print(f"  SOCKS (9050): {'✅ open' if tor_socks else '❌ closed'}")
    print(f"  Control (9051): {'✅ open' if tor_ctrl else '❌ closed'}")

    # Summary
    print("\n📋 Summary:")
    if not failures and tor_socks:
        print("  ✅ Environment looks healthy")
        return 0

    if failures:
        print("  ❌ Missing modules:")
        for m in failures:
            print(f"     - {m}")
        print("     Fix: pip install -r requirements.txt")

    if not tor_socks:
        print("  ❌ TOR is not running")
        print("     Fix: tor &")

    return 1
