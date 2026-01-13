import socket
import requests
import time

# ---- SAFE DEPENDENCY IMPORTS (NO LOGIC CHANGE) ----
try:
    import socks
except ImportError:
    raise RuntimeError(
        "PySocks is missing. Install it with: pip install PySocks"
    )

try:
    from stem import Signal
    from stem.control import Controller
except ImportError:
    raise RuntimeError(
        "stem is missing. Install it with: pip install stem"
    )
# --------------------------------------------------

class TorProxy:
    @staticmethod
    def setup() -> bool:
        """Start TOR and return SOCKS proxy status"""
        try:
            # Test TOR connection
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            socket.socket = socks.socksocket
            
            # Test connection
            response = requests.get("http://httpbin.org/ip", timeout=10)
            if "tor" in response.text.lower():
                print("🔒 TOR proxy active")
                return True
            return False
        except:
            print("❌ TOR not running. Start with: tor &")
            return False
    
    @staticmethod
    def renew_circuit():
        """Renew TOR circuit for fresh IP"""
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                print("🔄 TOR circuit renewed")
        except:
            print("⚠️ Could not renew TOR circuit")
    
    @staticmethod
    def get_ip() -> str:
        """Get current TOR exit IP"""
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        try:
            r = requests.get("http://httpbin.org/ip", timeout=10)
            return r.json()["origin"]
        except:
            return "unknown"

