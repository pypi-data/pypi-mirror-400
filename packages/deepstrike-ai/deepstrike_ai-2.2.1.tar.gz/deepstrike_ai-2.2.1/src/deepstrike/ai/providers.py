import os
import asyncio
import httpx
from typing import Optional

class AIProvider:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider.lower()
        self.api_key = api_key
        self.client = self._init_client()

    def _init_client(self):
        if self.provider == "openai":
            try:
                from openai import AsyncOpenAI
                return AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise RuntimeError(
                    "OpenAI support not installed. "
                    "Run: pip install deepstrike-ai[ai]"
                )

        elif self.provider == "anthropic":
            try:
                from anthropic import AsyncAnthropic
                return AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise RuntimeError(
                    "Anthropic support not installed. "
                    "Run: pip install deepstrike-ai[ai]"
                )

        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                return genai.GenerativeModel("gemini-pro")
            except ImportError:
                raise RuntimeError(
                    "Gemini support not installed. "
                    "Run: pip install deepstrike-ai[ai]"
                )

        elif self.provider == "grok":
            return httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

        return None

