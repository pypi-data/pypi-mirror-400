"""
Local LLM provider implementation using Ollama.

Ollama provides a local API compatible with OpenAI's format.
"""
from typing import AsyncIterator

from openai import AsyncOpenAI

from .base import BaseLLMProvider, LLMConfig, LLMMessage, LLMResponse


class LocalProvider(BaseLLMProvider):
    """Local LLM provider using Ollama."""

    # Common Ollama models
    MODELS = {
        "llama3": "llama3",
        "llama3.2": "llama3.2",
        "qwen2": "qwen2",
        "qwen2.5": "qwen2.5",
        "mistral": "mistral",
        "codellama": "codellama",
        "deepseek-coder": "deepseek-coder",
        "gemma": "gemma",
    }

    # Default base URL for Ollama
    DEFAULT_BASE_URL = "http://localhost:11434/v1/"

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        # Use Ollama's base URL if not provided
        base_url = config.base_url or self.DEFAULT_BASE_URL

        self.client = AsyncOpenAI(
            api_key="ollama",  # Ollama doesn't require a real API key
            base_url=base_url,
            timeout=config.timeout,
        )

    def validate_config(self) -> bool:
        """Validate Ollama configuration."""
        # For local Ollama, we just check if base_url is set
        return bool(self.config.base_url or self.DEFAULT_BASE_URL)

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate response using Ollama API."""
        try:
            # Convert messages to API format
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Call Ollama API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=temperature if temperature is not None else self.config.temperature,
                max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
            )

            # Extract response
            choice = response.choices[0]
            content = choice.message.content or ""

            return LLMResponse(
                content=content,
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else None,
                finish_reason=choice.finish_reason,
            )

        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model,
                error=str(e),
            )

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Generate streaming response using Ollama API."""
        try:
            # Convert messages to API format
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Stream Ollama API
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=temperature if temperature is not None else self.config.temperature,
                max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content

        except Exception as e:
            yield f"[Error: {str(e)}]"

    def get_model_info(self) -> dict[str, str]:
        """Get Ollama model information."""
        return {
            "provider": "Local (Ollama)",
            "model": self.model,
            "api_base": str(self.client.base_url),
        }
