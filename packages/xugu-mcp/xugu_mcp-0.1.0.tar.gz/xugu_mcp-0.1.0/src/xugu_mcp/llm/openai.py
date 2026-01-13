"""
OpenAI LLM provider implementation.
"""
from typing import AsyncIterator

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from .base import BaseLLMProvider, LLMConfig, LLMMessage, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    # Common OpenAI models
    MODELS = {
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        "gpt-4-turbo": "gpt-4-turbo",
        "gpt-4": "gpt-4",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
    }

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
        )

    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        return bool(self.config.api_key)

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate response using OpenAI API."""
        try:
            # Convert messages to OpenAI format
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Call OpenAI API
            response: ChatCompletion = await self.client.chat.completions.create(
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
        """Generate streaming response using OpenAI API."""
        try:
            # Convert messages to OpenAI format
            api_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Stream OpenAI API
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
        """Get OpenAI model information."""
        return {
            "provider": "OpenAI",
            "model": self.model,
        }
