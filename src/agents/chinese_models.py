"""
Chinese Model Providers
"""
import logging
from moonshot import Moonshot
from minimax import MiniMax
from src.llm_providers import LLMProvider

class KimiProvider(LLMProvider):
    def __init__(self, api_key: str, providers: dict = {}):
        self.client = Moonshot(api_key=api_key)
        self.logger = logging.getLogger("KimiProvider")
        self.providers = providers

    async def generate(self, prompt: str, **kwargs) -> str:
        # This is a placeholder, as the actual API may differ.
        return await self.client.generate(prompt)

    async def embed(self, text: str) -> list:
        self.logger.warning("Kimi `embed` method is not implemented.")
        return await self.providers["openai"].embed(text)

class MiniMaxProvider(LLMProvider):
    def __init__(self, api_key: str, group_id: str, providers: dict = {}):
        self.client = MiniMax(api_key=api_key, group_id=group_id)
        self.logger = logging.getLogger("MiniMaxProvider")
        self.providers = providers

    async def generate(self, prompt: str, **kwargs) -> str:
        # This is a placeholder, as the actual API may differ.
        return await self.client.generate(prompt)

    async def embed(self, text: str) -> list:
        self.logger.warning("MiniMax `embed` method is not implemented.")
        return await self.providers["openai"].embed(text)
