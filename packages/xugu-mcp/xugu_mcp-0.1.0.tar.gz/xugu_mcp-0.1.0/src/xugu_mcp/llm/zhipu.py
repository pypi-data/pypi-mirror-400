"""
zAI (Zhipu AI / 智谱 AI) LLM provider implementation.

Zhipu AI provides an OpenAI-compatible API for their GLM models.
"""
from typing import AsyncIterator

from openai import AsyncOpenAI

from .base import BaseLLMProvider, LLMConfig, LLMMessage, LLMResponse


class ZhipuProvider(BaseLLMProvider):
    """zAI (Zhipu AI) LLM provider."""

    # Zhipu AI GLM models
    MODELS = {
        "glm-4": "glm-4",
        "glm-4-plus": "glm-4-plus",
        "glm-4-air": "glm-4-air",
        "glm-4-flash": "glm-4-flash",
        "glm-3-turbo": "glm-3-turbo",
        "glm-4v": "glm-4v",  # Vision model
    }

    # Default base URL for Zhipu AI
    DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        # Use Zhipu AI's base URL if not provided
        base_url = config.base_url or self.DEFAULT_BASE_URL

        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=base_url,
            timeout=config.timeout,
        )

    def validate_config(self) -> bool:
        """Validate Zhipu AI configuration."""
        return bool(self.config.api_key)

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate response using Zhipu AI API."""
        try:
            # Convert messages to API format
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Call Zhipu AI API (OpenAI-compatible)
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
        """Generate streaming response using Zhipu AI API."""
        try:
            # Convert messages to API format
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Stream Zhipu AI API
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
        """Get Zhipu AI model information."""
        return {
            "provider": "zAI (Zhipu AI / 智谱 AI)",
            "model": self.model,
            "api_base": str(self.client.base_url),
        }
