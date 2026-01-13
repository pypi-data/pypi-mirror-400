"""
Claude LLM provider implementation using Anthropic API.
"""
from typing import AsyncIterator

from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage

from .base import BaseLLMProvider, LLMConfig, LLMMessage, LLMResponse


class ClaudeProvider(BaseLLMProvider):
    """Claude LLM provider using Anthropic API."""

    # Available Claude models
    MODELS = {
        "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku": "claude-3-5-haiku-20241022",
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
    }

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        # Normalize model name
        if config.model in self.MODELS:
            self.model = self.MODELS[config.model]
        else:
            self.model = config.model

        self.client = AsyncAnthropic(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
        )

    def validate_config(self) -> bool:
        """Validate Claude configuration."""
        return bool(self.config.api_key)

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate response using Claude API."""
        try:
            # Convert messages to Anthropic format
            system_message = None
            api_messages = []

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    api_messages.append(
                        {"role": msg.role, "content": msg.content}
                    )

            # Call Claude API
            response: AnthropicMessage = await self.client.messages.create(
                model=self.model,
                messages=api_messages,
                system=system_message,
                temperature=temperature if temperature is not None else self.config.temperature,
                max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
            )

            # Extract response
            content = response.content[0].text

            return LLMResponse(
                content=content,
                model=response.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
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
        """Generate streaming response using Claude API."""
        try:
            # Convert messages to Anthropic format
            system_message = None
            api_messages = []

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    api_messages.append(
                        {"role": msg.role, "content": msg.content}
                    )

            # Stream Claude API
            stream = await self.client.messages.create(
                model=self.model,
                messages=api_messages,
                system=system_message,
                temperature=temperature if temperature is not None else self.config.temperature,
                max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
                stream=True,
            )

            async for event in stream:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield event.delta.text

        except Exception as e:
            yield f"[Error: {str(e)}]"

    def get_model_info(self) -> dict[str, str]:
        """Get Claude model information."""
        return {
            "provider": "Claude (Anthropic)",
            "model": self.model,
            "api_base": str(self.client.base_url),
        }
