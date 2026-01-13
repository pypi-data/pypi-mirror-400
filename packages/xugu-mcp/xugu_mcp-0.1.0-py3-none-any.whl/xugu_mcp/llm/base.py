"""
Base LLM provider interface for XuguDB MCP Server.

All LLM providers must implement this interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMMessage:
    """Message for LLM conversation."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from LLM provider."""

    content: str
    model: str
    tokens_used: int | None = None
    finish_reason: str | None = None
    error: str | None = None


@dataclass
class LLMConfig:
    """Base configuration for LLM providers."""

    api_key: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 4096
    timeout: int = 60
    base_url: str | None = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            messages: List of conversation messages
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        """Generate a streaming response from the LLM.

        Args:
            messages: List of conversation messages
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Yields:
            Chunks of the response as they arrive
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the provider configuration.

        Returns:
            True if config is valid
        """
        pass

    def format_messages(
        self,
        system: str | None = None,
        user: str | None = None,
        assistant: str | None = None,
    ) -> list[LLMMessage]:
        """Helper to format messages.

        Args:
            system: System message content
            user: User message content
            assistant: Assistant message content

        Returns:
            List of LLMMessage objects
        """
        messages = []
        if system:
            messages.append(LLMMessage(role="system", content=system))
        if user:
            messages.append(LLMMessage(role="user", content=user))
        if assistant:
            messages.append(LLMMessage(role="assistant", content=assistant))
        return messages

    def get_model_info(self) -> dict[str, str]:
        """Get information about the current model.

        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.__class__.__name__,
            "model": self.model,
        }
