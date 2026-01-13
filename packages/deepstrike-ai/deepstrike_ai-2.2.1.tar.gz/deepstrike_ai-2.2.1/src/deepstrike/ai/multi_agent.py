import asyncio
from typing import Dict, List, Any
from ..config import config
from .providers import get_provider

class MultiAIAgent:
    def __init__(self):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize available AI providers"""
        provider_map = {
            "openai": config.openai_key,
            "anthropic": config.anthropic_key,
            "grok": config.grok_key
        }
        
        for name, key in provider_map.items():
            if key:
                try:
                    self.providers[name] = get_provider(name)
                    print(f"🤖 Loaded {name}")
                except Exception as e:
                    print(f"⚠️ Failed to load {name}: {e}")
    
    async def plan_attack(self, target: Dict[str, Any]) -> Dict[str, List[str]]:
        """Get attack plan from best available AI"""
        prompt = f"""
        Analyze this target for penetration testing:
        Target: {target}
        
        Create prioritized attack plan in JSON format:
        {{
            "recon": ["nmap", "gobuster"],
            "exploits": ["ms17_010"],
            "payloads": ["reverse_tcp"],
            "post": ["persistence"]
        }}
        """
        
        for provider_name, provider in self.providers.items():
            try:
                response = await provider.generate(prompt)
                # Parse JSON response
                import json
                return json.loads(response)
            except Exception as e:
                print(f"{provider_name} failed: {e}")
                continue
        
        return {"recon": ["nmap"], "exploits": [], "payloads": []}
    
    async def generate_payload(self, target_os: str, exploit: str) -> str:
        """Generate custom payload"""
        prompt = f"""
        Generate safe pentest payload for {target_os} targeting {exploit}.
        Return ONLY the base64 encoded shellcode/shell.
        """
        
        for provider_name, provider in self.providers.items():
            try:
                return await provider.generate(prompt)
            except:
                continue
        
        return ""
    
    def get_status(self) -> Dict[str, int]:
        return {"available_providers": len(self.providers)}
