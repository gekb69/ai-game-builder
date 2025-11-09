"""
Multi-LLM Provider Integration
Supports OpenAI, Anthropic, Google, HuggingFace, Ollama
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import openai
from anthropic import AsyncAnthropic
import google.generativeai as genai
from huggingface_hub import InferenceClient
import ollama
from src.agents.chinese_models import KimiProvider, MiniMaxProvider

class LLMProvider(ABC):
    """Abstract LLM provider"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        self.logger.warning("`generate` method is not implemented.")
        return ""

    @abstractmethod
    async def embed(self, text: str) -> list:
        self.logger.warning("`embed` method is not implemented.")
        return []

class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4/GPT-3.5 provider"""

    def __init__(self, api_key: str, model: str = "gpt-4", providers: Dict = {}):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger("OpenAIProvider")
        self.providers = providers

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7)
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI error: {e}")
            return f"Error: {str(e)}"

    async def embed(self, text: str) -> list:
        response = await self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", providers: Dict = {}):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger("AnthropicProvider")
        self.providers = providers

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"Anthropic error: {e}")
            return f"Error: {str(e)}"

    async def embed(self, text: str) -> list:
        self.logger.warning("Anthropic `embed` method is not implemented.")
        # Placeholder: Fallback to the default provider's embed method.
        return await self.providers["openai"].embed(text)

class GoogleProvider(LLMProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: str, model: str = "gemini-pro", providers: Dict = {}):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.logger = logging.getLogger("GoogleProvider")
        self.providers = providers

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config={
                    "max_output_tokens": kwargs.get("max_tokens", 4096),
                    "temperature": kwargs.get("temperature", 0.7)
                }
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Google AI error: {e}")
            return f"Error: {str(e)}"

    async def embed(self, text: str) -> list:
        self.logger.warning("Google `embed` method is not implemented.")
        # Placeholder: Fallback to the default provider's embed method.
        return await self.providers["openai"].embed(text)

class HuggingFaceProvider(LLMProvider):
    """HuggingFace models"""

    def __init__(self, api_key: str, model: str = "meta-llama/Llama-2-7b-chat-hf", providers: Dict = {}):
        self.client = InferenceClient(model=model, token=api_key)
        self.logger = logging.getLogger("HuggingFaceProvider")
        self.providers = providers

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await asyncio.to_thread(
                self.client.text_generation,
                prompt,
                max_new_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7)
            )
            return response
        except Exception as e:
            self.logger.error(f"HuggingFace error: {e}")
            return f"Error: {str(e)}"

    async def embed(self, text: str) -> list:
        self.logger.warning("HuggingFace `embed` method is not implemented.")
        # Placeholder: Fallback to the default provider's embed method.
        return await self.providers["openai"].embed(text)

class OllamaProvider(LLMProvider):
    """Local Ollama models"""

    def __init__(self, url: str = "http://localhost:11434", model: str = "llama2", providers: Dict = {}):
        self.url = url
        self.model = model
        self.logger = logging.getLogger("OllamaProvider")
        self.providers = providers

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await asyncio.to_thread(
                ollama.chat,
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            self.logger.error(f"Ollama error: {e}")
            return f"Error: {str(e)}"

    async def embed(self, text: str) -> list:
        try:
            response = await asyncio.to_thread(
                ollama.embeddings,
                model=self.model,
                prompt=text
            )
            return response["embedding"]
        except Exception as e:
            self.logger.error(f"Ollama embed error: {e}")
            return []

class LLMProviderManager:
    """Manages multiple LLM providers"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("LLMProviderManager")
        self.providers: Dict[str, LLMProvider] = {}
        self.active_provider = None

    async def initialize(self):
        """Initialize all configured providers"""
        self.logger.info("🤖 Initializing LLM Providers...")

        # OpenAI
        if self.config.llm_providers.openai.enabled:
            self.providers["openai"] = OpenAIProvider(
                api_key=self.config.llm_providers.openai.api_key,
                model=self.config.llm_providers.openai.model,
                providers=self.providers,
            )

        # Anthropic
        if self.config.llm_providers.anthropic.enabled:
            self.providers["anthropic"] = AnthropicProvider(
                api_key=self.config.llm_providers.anthropic.api_key,
                model=self.config.llm_providers.anthropic.model,
                providers=self.providers,
            )

        # Google
        if self.config.llm_providers.google.enabled:
            self.providers["google"] = GoogleProvider(
                api_key=self.config.llm_providers.google.api_key,
                model=self.config.llm_providers.google.model,
                providers=self.providers,
            )

        # HuggingFace
        if self.config.llm_providers.huggingface.enabled:
            self.providers["huggingface"] = HuggingFaceProvider(
                api_key=self.config.llm_providers.huggingface.api_key,
                model=self.config.llm_providers.huggingface.model,
                providers=self.providers,
            )

        # Ollama
        if self.config.llm_providers.ollama.enabled:
            self.providers["ollama"] = OllamaProvider(
                url=self.config.llm_providers.ollama.url,
                model=self.config.llm_providers.ollama.model,
                providers=self.providers,
            )

        # Kimi
        if self.config.llm_providers.kimi.enabled:
            self.providers["kimi"] = KimiProvider(
                api_key=self.config.llm_providers.kimi.api_key,
                providers=self.providers,
            )

        # MiniMax
        if self.config.llm_providers.minimax.enabled:
            self.providers["minimax"] = MiniMaxProvider(
                api_key=self.config.llm_providers.minimax.api_key,
                group_id=self.config.llm_providers.minimax.group_id,
                providers=self.providers,
            )

        # Set default provider
        if self.providers:
            self.active_provider = list(self.providers.keys())[0]

        self.logger.info(f"✅ {len(self.providers)} LLM providers initialized")

    async def generate(self, prompt: str, provider: Optional[str] = None, **kwargs) -> str:
        """Generate text with specified provider"""
        if not self.providers:
            return "No LLM providers available"

        provider_name = provider or self.active_provider
        if provider_name not in self.providers:
            return f"Provider {provider_name} not available"

        return await self.providers[provider_name].generate(prompt, **kwargs)

    async def embed(self, text: str, provider: Optional[str] = None) -> list:
        """Get embeddings"""
        if not self.providers:
            return []

        provider_name = provider or self.active_provider
        return await self.providers[provider_name].embed(text)

    def get_providers_status(self) -> Dict[str, bool]:
        """Get status of all providers"""
        return {name: provider is not None for name, provider in self.providers.items()}
